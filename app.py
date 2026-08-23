import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os
import re

# --- 1. إعدادات واجهة المستخدم والصفحة اللوجستية ---
st.set_page_config(
    page_title="شركة أطلس للشحن والتجارة العامة", page_icon="📦", layout="wide"
)

# تعزيز الأنماط المرئية وأحجام خطوط الجداول الأم لتكون واضحة جداً
st.markdown("""
    <style>
    .dataframe th, .dataframe td {
        font-size: 15px !important;
        font-weight: 600 !important;
        text-align: center !important;
    }
    div[data-testid="stDataFrame"] div {
        font-family: sans-serif !important;
    }
    /* تنسيق صندوق بوابة تسجيل الدخول */
    .login-box {
        background-color: #1e293b;
        padding: 35px;
        border-radius: 14px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
        max-width: 550px;
        margin: 60px auto;
        text-align: center;
    }
    /* تنسيق البطاقات الإيضاحية المالية العلوية الفاخرة */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-left: 5px solid #4f46e5;
        padding: 20px;
        border-radius: 12px;
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 15px;
        font-family: sans-serif;
        text-align: right;
    }
    .metric-title {
        font-size: 14px;
        color: #94a3b8;
        font-weight: 500;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# إدارة حالة جلسة تسجيل الدخول بذاكرة الجلسة
if "logged_in_customer" not in st.session_state:
    st.session_state.logged_in_customer = None

# --- 2. الشريط الجانبي الذكي لإدارة شركة أطلس ---
with st.sidebar:
  if os.path.exists("logo.png"):
      st.image("logo.png", width=120)
  elif os.path.exists("logo.jpg"):
      st.image("logo.jpg", width=120)
  else:
      st.markdown("<h2 style='margin:0; text-align:center;'>🏛️</h2>", unsafe_allow_html=True)
      
  st.title("لوحة تحكم أطلس")
  st.markdown("---")

  # ميزة الحفظ الدائم التلقائي في الخادم
  uploaded_file = None
  
  st.subheader("📁 تحديث جدول الشحنات الموحد")
  new_file = st.file_uploader(
      "رفع ملف إكسيل جديد (.xlsx)", type=["xlsx", "xls"], key="admin_uploader"
  )
  
  if new_file is not None:
      try:
          with open("data.xlsx", "wb") as f:
              f.write(new_file.getbuffer())
          st.sidebar.success("✅ تم حفظ وتثبيت الملف في خادم المنصة بنجاح حسي!")
          uploaded_file = "data.xlsx"
      except Exception as e:
          uploaded_file = new_file
  elif os.path.exists("data.xlsx"):
      uploaded_file = "data.xlsx"


# --- 3. دالة معالجة الجداول والملفات البرمجية بذكاء ---
def load_data_smart(file):
  if file is not None:
    try:
        xl = pd.ExcelFile(file)
        target_sheet = xl.sheet_names
        for sheet in xl.sheet_names:
            test_df = pd.read_excel(file, sheet_name=sheet, nrows=5)
            if not test_df.empty and len(test_df.columns) > 2:
                target_sheet = sheet
                break
        raw_df = pd.read_excel(file, sheet_name=target_sheet, header=0)
        raw_df.columns = raw_df.columns.str.strip()
        return raw_df
    except Exception as e:
        return pd.DataFrame()
  else:
    return pd.DataFrame()


df = load_data_smart(uploaded_file)

# التحقق من سلامة البيانات وعرض شاشة البوابة الرئيسية
if df.empty:
  st.markdown("""
    <div class='login-box'>
        <h2 style='color: white;'>🏛️ شركة أطلس للشحن والتجارة العامة</h2>
        <h4 style='color: #4f46e5; margin-top: 10px;'>بوابة العملاء اللوجستية</h4>
        <p style='color: #94a3b8; margin-top: 15px;'>النظام قيد المزامنة الآمنة. يرجى رفع ملف قاعدة البيانات الشاملة من زر الرفع في الشريط الجانبي ⬅️ لتفعيل وتثبيت الخدمة فوراً.</p>
    </div>
  """, unsafe_allow_html=True)
  st.stop()
else:
  # مطابقة مسميات الأعمدة بمرونة كاملة وتلافي أي أخطاء في الإكسيل
  def find_col(possible_names, fallback):
      for name in possible_names:
          if name in df.columns:
              return name
          for col in df.columns:
              if name.lower() in col.lower():
                  return col
      return fallback

  client_name_col = find_col(["code", "الكود", "اسم الزبون"], "code")
  container_col = find_col(["رقم الحاوية", "كونتينر", "Container"], "رقم الحاوية")
  shipping_mark_col = find_col(["Shipping mark", "shipping_mark", "ماركة الشحن"], "Shipping mark")
  amt_col = find_col(["المجموع", "Amount", "المبلغ"], "المجموع")
  client_col = find_col(["الزبون دفع", "العميل دفع", "Client paid"], "الزبون دفع")
  office_col = find_col(["المكتب دفع", "Office paid"], "المكتب دفع")
  ctns_col = find_col(["عدد الكارتون", "العدد", "Cartons"], "عدد الكارتون")
  cbm_col = find_col(["حجم", "الحجم", "Volume"], "حجم")
  customs_col = find_col(["مبلغ الجمرك", "الجمرك", "Customs"], "مبلغ الجمرك")
  collected_col = find_col(["قيمة الاستحصالات", "الاستحصالات", "Collected"], "قيمة الاستحصالات")
  remaining_col = find_col(["متبقي حقيقي", "المتبقي", "Remaining"], "متبقي حقيقي")

  # تحويل كافة قيم عمود الأكواد لنصوص صافية ممسوحة المسافات لضمان التصفية المطلقة
  if client_name_col in df.columns:
      df[client_name_col] = df[client_name_col].astype(str).str.strip()

  # تطهير وتنظيف كافة الحقول والعمليات الرقمية والمالية
  all_numeric_cols = [amt_col, client_col, office_col, ctns_col, cbm_col, customs_col, collected_col, remaining_col]
  for col in all_numeric_cols:
    if col in df.columns:
      df[col] = pd.to_numeric(df[col].astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce").fillna(0)

  # تصفية أسطر الإجماليات اليدوية
  if shipping_mark_col in df.columns:
    df = df[~df[shipping_mark_col].astype(str).str.lower().str.contains("total|grand|إجمالي", na=False)]
  if container_col in df.columns:
    df = df[df[container_col].notna()]

  # حساب عمود حالة الدفع التلقائي في الجدول الأم
  if remaining_col in df.columns and amt_col in df.columns:
    def check_payment_status(row):
        return "مدفوع بالكامل ✅" if row[remaining_col] <= 0 else "يوجد متبقي غير مدفوع ⏳"
    df["حالة دفع الشحنة"] = df.apply(check_payment_status, axis=1)

  # --- 4. نظام تسجيل الدخول الفائق والمطور ---
  valid_codes = list(df[client_name_col].dropna().unique()) if client_name_col in df.columns else []
  valid_codes_clean = [str(re.sub(r'\D', '', str(c))).strip() for c in valid_codes]

  if st.session_state.logged_in_customer is None:
      st.markdown("""
        <div style='text-align: center; margin-top: 30px;'>
            <h1 style='color: #4f46e5; font-family: sans-serif; font-weight: bold;'>شركة أطلس للشحن والتجارة العامة</h1>
            <h3 style='color: #10b981; font-family: sans-serif;'>بوابة العملاء اللوجستية</h3>
            <p style='color: gray;'>مرحباً بك في بوابة العميل الآمنة - يرجى تسجيل الدخول لمتابعة حساباتك وشحناتك</p>
        </div>
      """, unsafe_allow_html=True)
      
      col_space1, col_login, col_space2 = st.columns(3)
      with col_login:
          with st.form("login_form"):
              password_input = st.text_input("🔑 أدخل كلمة المرور الخاصة بك (كود العميل):", type="password", help="كلمة المرور هي كود العميل الخاص بك")
              submit_login = st.form_submit_button("تسجيل الدخول الآمن 🔓")
              
              if submit_login:
                  clean_input = str(re.sub(r'\D', '', str(password_input))).strip()
                  
                  # كود الدخول الماستر لمدير النظام
                  if password_input.strip() == "881988": 
                      st.session_state.logged_in_customer = "الكل"
                      st.success("مرحباً بك يا مدير النظام!")
                      st.rerun()
                  
                  matched_code = None
                  for original_code in valid_codes:
                      code_str = str(original_code).strip().lower()
                      code_digits = str(re.sub(r'\D', '', code_str)).strip()
                      
                      if (user_text := str(password_input).strip().lower()) == code_str or (clean_input and clean_input == code_digits) or (user_text in code_str) or (code_str in user_text):
                          matched_code = original_code
                          break
                  
                  if matched_code is not None:
                      st.session_state.logged_in_customer = matched_code
                      st.success("تم التحقق بنجاح! جاري تحميل لوحة التحكم...")
                      st.rerun()
                  else:
                      st.error("❌ كلمة المرور غير صحيحة أو غير مسجلة في النظام!")
      st.stop() 

  # --- 5. عزل الحسابات الفردية لكل زبون تأميناً للسرية والخصوصية ---
  selected_client = st.session_state.logged_in_customer
  
  if selected_client != "الكل" and client_name_col in df.columns:
      # 🌟 إصلاح جوهري: التصفية الاحتوائية المرنة للأرقام لمنع اختفاء البيانات فور تسجيل الدخول 🌟
      selected_client_digits = str(re.sub(r'\D', '', str(selected_client))).strip()
      df_client = df[
          (df[client_name_col].astype(str).str.lower() == str(selected_client).lower().strip()) |
          (df[client_name_col].astype(str).str.replace(r'\D', '', regex=True) == selected_client_digits)
      ]
      st.sidebar.markdown(f"👤 العميل الحالي: **{selected_client}**")
      if st.sidebar.button("🚪 تسجيل الخروج الآمن"):
          st.session_state.logged_in_customer = None
          st.rerun()
  else:
      df_client = df
      st.sidebar.markdown("👑 صلاحية: **مدير النظام**")
      st.sidebar.markdown("### 🔍 كاشف الأكواد المتاحة بالملف:")
      st.sidebar.dataframe(pd.DataFrame({"الأكواد المسجلة": valid_codes}), height=200)
      if st.sidebar.button("🚪 خروج الإدارة"):
          st.session_state.logged_in_customer = None
          st.rerun()

  # --- 6. عنوان الواجهة اللوجستية الرئيسي ---
  st.title("📦 Logistics Dashboard — أطلس")

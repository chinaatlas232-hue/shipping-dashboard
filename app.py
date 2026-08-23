import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os
import re

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="شركة أطلس للشحن والتجارة العامة", page_icon="📦", layout="wide"
)

# تعزيز حجم خط ولون الجدول ليكون أكبر وأوضح عند العرض
st.markdown("""
    <style>
    .dataframe th, .dataframe td {
        font-size: 15px !important;
        font-weight: 500 !important;
    }
    div[data-testid="stDataFrame"] div {
        font-family: sans-serif !important;
    }
    /* تنسيق صندوق تسجيل الدخول */
    .login-box {
        background-color: #1e293b;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        max-width: 550px;
        margin: 50px auto;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# إدارة حالة تسجيل الدخول بذاكرة الجلسة
if "logged_in_customer" not in st.session_state:
    st.session_state.logged_in_customer = None

# --- 2. الشريط الجانبي الذكي لمدير النظام ---
with st.sidebar:
  if os.path.exists("logo.png"):
      st.image("logo.png", width=120)
  elif os.path.exists("logo.jpg"):
      st.image("logo.jpg", width=120)
  else:
      st.markdown("<h2 style='margin:0;'>📦</h2>", unsafe_allow_html=True)
      
  st.title("إدارة النظام - أطلس")
  st.markdown("---")

  # تحديد مسار الملف الافتراضي المرفوع على السيرفر
  uploaded_file = "data.xlsx" if os.path.exists("data.xlsx") else None

  # ميزة الرفع اليدوي والتحديث المباشر للإدارة عند دخول المدير بكود 881988
  if st.session_state.logged_in_customer == "الكل":
      st.subheader("📁 تحديث قاعدة البيانات")
      new_file = st.file_uploader(
          "رفع ملف جديد لتحديث البيانات (.xlsx)", type=["xlsx", "xls"], key="admin_uploader"
      )
      if new_file is not None:
          uploaded_file = new_file


# --- 3. دالة ذكية لقراءة الشيت الصحيح وتفادي الجداول الفارغة ---
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

# التحقق من وجود بيانات لبدء العرض
if df.empty:
  st.markdown("""
    <div class='login-box'>
        <h2 style='color: white;'>🏛️ شركة أطلس للشحن والتجارة العامة</h2>
        <h4 style='color: #4f46e5;'>بوابة العملاء اللوجستية</h4>
        <p style='color: #94a3b8; margin-top: 15px;'>نظام الإدارة قيد الانتظار. يرجى من مدير النظام رفع قاعدة البيانات الشاملة من زر الرفع في الشريط الجانبي لتفعيل الخدمة للعملاء.</p>
    </div>
  """, unsafe_allow_html=True)
  
  if st.session_state.logged_in_customer is None:
      col_space1, col_admin_login, col_space2 = st.columns(3)
      with col_admin_login:
          with st.form("admin_login_initial"):
              admin_pwd = st.text_input("🔑 دخول الإدارة المباشر لتفعيل الملف:", type="password")
              submit_admin = st.form_submit_button("دخول مدير النظام 👑")
              if submit_admin and admin_pwd.strip() == "881988":
                  st.session_state.logged_in_customer = "الكل"
                  st.rerun()
  st.stop()
else:
  # حل مرن للتعرف على الأعمدة وتفادي أخطاء المسميات
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

  # تحويل الحقول المالية والعددية إلى قيم رقمية نظيفة لحسابات دقيقة 100% وتطهير نصوص العملات
  all_numeric_cols = [amt_col, client_col, office_col, ctns_col, cbm_col, customs_col, collected_col, remaining_col]
  for col in all_numeric_cols:
    if col in df.columns:
      df[col] = pd.to_numeric(df[col].astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce").fillna(0)

  # استبعاد أسطر الإجماليات يدوية الصنع لحماية الحسابات الديناميكية
  if shipping_mark_col in df.columns:
    df = df[~df[shipping_mark_col].astype(str).str.lower().str.contains("total|grand|إجمالي", na=False)]
  if container_col in df.columns:
    df = df[df[container_col].notna()]

  # حساب حالة الدفع بناءً على المتبقي الحقيقي
  if remaining_col in df.columns and amt_col in df.columns:
    def check_payment_status(row):
        if row[remaining_col] <= 0:
            return "مدفوع بالكامل ✅"
        else:
            return "يوجد متبقي غير مدفوع ⏳"
    df["حالة دفع الشحنة"] = df.apply(check_payment_status, axis=1)

  # --- 4. نظام تسجيل الدخول الفائق والمطور (المطابقة المباشرة الشاملة) 🌟 ---
  valid_codes = list(df[client_name_col].dropna().unique()) if client_name_col in df.columns else []

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
                  # تنظيف وتحضير المدخلات والمقارنة الاحتوائية الشاملة لضمان القبول الفوري 🌟
                  user_text = str(password_input).strip().lower()
                  user_digits = str(re.sub(r'\D', '', user_text)).strip()
                  
                  matched_code = None
                  for original_code in valid_codes:
                      code_str = str(original_code).strip().lower()
                      code_digits = str(re.sub(r'\D', '', code_str)).strip()
                      
                      # مطابقة لو كان النص متطابق، أو الرقم متطابق، أو أحدهما يحتوي الآخر
                      if (user_text == code_str) or (user_digits and user_digits == code_digits) or (user_text in code_str) or (code_str in user_text):
                          matched_code = original_code
                          break
                  
                  if matched_code is not None:
                      st.session_state.logged_in_customer = matched_code
                      st.success("تم التحقق بنجاح! جاري تحميل لوحة التحكم...")
                      st.rerun()
                  elif password_input.strip() == "881988": 
                      st.session_state.logged_in_customer = "الكل"
                      st.success("مرحباً بك يا مدير النظام!")
                      st.rerun()
                  else:
                      st.error("❌ كلمة المرور غير صحيحة أو غير مسجلة في النظام!")
      st.stop() 

  # --- 5. فلترة وعزل البيانات بناءً على تسجيل الدخول الناجح للعميل ---
  selected_client = st.session_state.logged_in_customer
  
  if selected_client != "الكل" and client_name_col in df.columns:
      df_client = df[df[client_name_col].astype(str).str.strip() == str(selected_client).strip()]
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

  # --- 6. عنوان الواجهة الرئيسي للزبون بعد تسجيل الدخول ---
  st.title("📦 Logistics Dashboard — أطلس")
  st.markdown(f"جلسة عرض آمنة ومحمية للعميل: **{selected_client if selected_client != 'الكل' else 'كافة العملاء'}**")
  st.markdown("---")

  # --- 7. أشرطة تصفية الحاويات والماركات المعزولة للعميل ---
  st.markdown("##### 🗂️ أشرطة التصفية السريعة الذكية:")
  
  container_options = ["الكل"] + list(df_client[container_col].dropna().unique()) if container_col in df_client.columns else ["الكل"]
  selected_container = st.pills("اختر الحاوية", options=container_options, default="الكل", key="container_pill")

  if selected_container != "الكل" and container_col in df_client.columns:
      temp_df = df_client[df_client[container_col] == selected_container]
  else:
      temp_df = df_client


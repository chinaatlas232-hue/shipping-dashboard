import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os

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

  # 🌟 حل مرن: البحث الذكي عن الملف بمختلف الصيغ (data.xlsx أو DATA.xlsx أو data.XLSX) لضمان القراءة تماماً
  uploaded_file = None
  for filename in os.listdir("."):
      if filename.lower() == "data.xlsx":
          uploaded_file = filename
          break

  # إتاحة الرفع اليدوي والتحديث المباشر للإدارة فقط عند دخول المدير بكود 881988
  if st.session_state.logged_in_customer == "الكل":
      st.subheader("📁 تحديث قاعدة البيانات")
      new_file = st.file_uploader(
          "رفع ملف جديد لتحديث البيانات (.xlsx)", type=["xlsx", "xls"], key="admin_uploader"
      )
      if new_file is not None:
          uploaded_file = new_file


# --- 3. دالة قراءة وتجهيز البيانات النظيفة والمباشرة (بدون كاش) ---
def load_data_fresh(file):
  if file is not None:
    try:
        raw_df = pd.read_excel(file, header=0)
        raw_df.columns = raw_df.columns.str.strip()
        return raw_df
    except Exception as e:
        return pd.DataFrame()
  else:
    return pd.DataFrame()


df = load_data_fresh(uploaded_file)

# التحقق من وجود بيانات لبدء العرض
if df.empty:
  st.markdown("""
    <div class='login-box'>
        <h2 style='color: white;'>🏛️ شركة أطلس للشحن والتجارة العامة</h2>
        <h4 style='color: #4f46e5;'>بوابة العملاء اللوجستية</h4>
        <p style='color: #94a3b8; margin-top: 15px;'>نظام الإدارة قيد الانتظار. يرجى التأكد من رفع ملف قاعدة البيانات وتسميته <b>data.xlsx</b> داخل حساب GitHub بجانب ملف الكود لكي يعمل الرابط مباشرة.</p>
    </div>
  """, unsafe_allow_html=True)
  
  # نموذج احتياطي وسري لدخول الإدارة لتشغيل وتحديث النظام مباشرة من الهاتف 🌟
  col_space1, col_admin_login, col_space2 = st.columns(3)
  with col_admin_login:
      with st.form("admin_login_initial"):
          admin_pwd = st.text_input("🔑 دخول الإدارة المباشر للتحديث المالي:", type="password")
          admin_submit = st.form_submit_button("دخول مدير النظام وتطهير الكاش 👑")
          if admin_submit and admin_pwd.strip() == "881988":
              st.session_state.logged_in_customer = "الكل"
              st.rerun()
  st.stop()
else:
  # حل ذكي ومرن للتعرف على الأعمدة وتفادي الـ KeyError تماماً
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

  # --- 4. نظام تسجيل الدخول الاحترافي المحدث والمحصن ضد المسافات والخلايا النصية ---
  valid_codes = list(df[client_name_col].dropna().unique()) if client_name_col in df.columns else []
  valid_codes_clean = [str(c).strip().lower() for c in valid_codes]

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
              password_input = st.text_input("🔑 أدخل كلمة المرور الخاصة بك (كود العميل):", type="password", help="كلمة المرور هي كود العميل الخاص بك مثل B12")
              submit_login = st.form_submit_button("تسجيل الدخول الآمن 🔓")
              
              if submit_login:
                  clean_input = str(password_input).strip().lower()
                  
                  if clean_input in valid_codes_clean:
                      actual_code = valid_codes[valid_codes_clean.index(clean_input)]
                      st.session_state.logged_in_customer = actual_code
                      st.success("تم التحقق بنجاح! جاري تحميل لوحة التحكم الخاصة بك...")
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
      df[client_name_col] = df[client_name_col].astype(str).str.strip()
      df_client = df[df[client_name_col].str.lower() == str(selected_client).lower().strip()]
      st.sidebar.markdown(f"👤 العميل الحالي: **{selected_client}**")
      if st.sidebar.button("🚪 تسجيل الخروج الآمن"):
          st.session_state.logged_in_customer = None
          st.rerun()
  else:
      df_client = df
      st.sidebar.markdown("👑 صلاحية: **مدير النظام**")
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

  shipping_mark_options = ["الكل"] + list(temp_df[shipping_mark_col].dropna().unique()) if shipping_mark_col in temp_df.columns else ["الكل"]
  selected_mark = st.pills("اختر ماركة الشحن (Shipping Mark)", options=shipping_mark_options, default="الكل", key="mark_pill")

  filtered_df = temp_df
  if selected_mark != "الكل" and shipping_mark_col in filtered_df.columns:
      filtered_df = filtered_df[filtered_df[shipping_mark_col] == selected_mark]

  # --- 8. العمليات الحسابية والمؤشرات الديناميكية للعميل المختار ---
  total_orders = len(filtered_df)
  total_containers = filtered_df[container_col].nunique() if container_col in filtered_df.columns else 0
  total_amount_val = filtered_df[amt_col].sum() if amt_col in filtered_df.columns else 0
  total_client_paid = filtered_df[client_col].sum() if client_col in filtered_df.columns else 0

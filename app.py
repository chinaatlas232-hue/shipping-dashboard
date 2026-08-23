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

# --- 2. الشريط الجانبي: مخصص لك لرفع قاعدة البيانات الموحدة ---
with st.sidebar:
  if os.path.exists("logo.png"):
      st.image("logo.png", width=120)
  elif os.path.exists("logo.jpg"):
      st.image("logo.jpg", width=120)
  else:
      st.markdown("<h2 style='margin:0;'>📦</h2>", unsafe_allow_html=True)
      
  st.title("إدارة النظام - أطلس")
  st.markdown("---")

  # رفع ملف إكسل الشامل
  st.subheader("📁 رفع قاعدة البيانات")
  uploaded_file = st.file_uploader(
      "رفع ملف الإكسيل الشامل لكافة العملاء (.xlsx)", type=["xlsx", "xls"]
  )


# --- 3. قراءة البيانات الأصلية النظيفة ---
@st.cache_data
def load_data(file):
  if file is not None:
    raw_df = pd.read_excel(file, header=0)
    raw_df.columns = raw_df.columns.str.strip()
    return raw_df
  else:
    return pd.DataFrame()


df = load_data(uploaded_file)

# التحقق من وجود بيانات لبدء العرض
if df.empty:
  st.markdown("""
    <div class='login-box'>
        <h2 style='color: white;'>🏛️ شركة أطلس للشحن والتجارة العامة</h2>
        <h4 style='color: #4f46e5;'>بوابة العملاء اللوجستية</h4>
        <p style='color: #94a3b8; margin-top: 15px;'>نظام الإدارة قيد الانتظار. يرجى من مدير النظام رفع قاعدة البيانات الشاملة من الشريط الجانبي لتفعيل الخدمة للعملاء.</p>
    </div>
  """, unsafe_allow_html=True)
else:
  # تعيين العمود مصفح العملاء بناءً على اسم "code" الموجود في ملفك حرفياً
  client_name_col = "code"
  
  # بقية مسميات الأعمدة الحقيقية لجدولك النظيف
  container_col = "رقم الحاوية"
  shipping_mark_col = "Shipping mark"
  amt_col = "المجموع"
  client_col = "الزبون دفع"
  office_col = "المكتب دفع"
  ctns_col = "عدد الكارتون"
  cbm_col = "حجم"
  customs_col = "مبلغ الجمرك"
  collected_col = "قيمة الاستحصالات"
  remaining_col = "متبقي حقيقي"

  # تحويل الحقول المالية والعددية إلى قيم رقمية نظيفة لحسابات دقيقة 100% وتطهير أي نصوص
  all_numeric_cols = [amt_col, client_col, office_col, ctns_col, cbm_col, customs_col, collected_col, remaining_col]
  for col in all_numeric_cols:
    if col in df.columns:
      df[col] = pd.to_numeric(df[col].astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce").fillna(0)

  # استبعاد أسطر الإجماليات يدوية الصنع لحماية الحسابات الديناميكية
  df = df[~df[shipping_mark_col].astype(str).str.lower().str.contains("total|grand|إجمالي", na=False)]
  df = df[df[container_col].notna()]

  # حساب حالة الدفع بناءً على المتبقي الحقيقي
  def check_payment_status(row):
      if row[remaining_col] <= 0:
          return "مدفوع بالكامل ✅"
      else:
          return "يوجد متبقي غير مدفوع ⏳"
          
  df["حالة دفع الشحنة"] = df.apply(check_payment_status, axis=1)

  # --- 4. نظام تسجيل الدخول الاحترافي باسم شركة أطلس وبوابة العملاء ---
  valid_codes = list(df[client_name_col].dropna().unique())
  
  if "logged_in_customer" not in st.session_state:
      st.session_state.logged_in_customer = None

  if st.session_state.logged_in_customer is None:
      # 🌟 تفعيل الهوية البصرية الرسمية لشركة أطلس في شاشة تسجيل الدخول المباشرة 🌟
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
                  clean_pwd = password_input.strip()
                  if clean_pwd in valid_codes:
                      st.session_state.logged_in_customer = clean_pwd
                      st.success("تم التحقق بنجاح! جاري تحميل لوحة التحكم الخاصة بك...")
                      st.rerun()
                  elif clean_pwd == "881988": 
                      st.session_state.logged_in_customer = "الكل"
                      st.success("مرحباً بك يا مدير النظام!")
                      st.rerun()
                  else:
                      st.error("❌ كلمة المرور غير صحيحة أو غير مسجلة في النظام!")
      st.stop() 

  # --- 5. فلترة وعزل البيانات بناءً على تسجيل الدخول الناجح للعميل ---
  selected_client = st.session_state.logged_in_customer
  
  if selected_client != "الكل":
      df_client = df[df[client_name_col] == selected_client]
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
  
  container_options = ["الكل"] + list(df_client[container_col].dropna().unique())
  selected_container = st.pills("اختر الحاوية", options=container_options, default="الكل", key="container_pill")

  if selected_container != "الكل":
      temp_df = df_client[df_client[container_col] == selected_container]
  else:
      temp_df = df_client

  shipping_mark_options = ["الكل"] + list(temp_df[shipping_mark_col].dropna().unique())
  selected_mark = st.pills("اختر ماركة الشحن (Shipping Mark)", options=shipping_mark_options, default="الكل", key="mark_pill")

  filtered_df = temp_df
  if selected_mark != "الكل":
      filtered_df = filtered_df[filtered_df[shipping_mark_col] == selected_mark]

  # --- 8. العمليات الحسابية والمؤشرات الديناميكية للعميل المختار ---
  total_orders = len(filtered_df)
  total_containers = filtered_df[container_col].nunique()
  total_amount_val = filtered_df[amt_col].sum() if amt_col in filtered_df.columns else 0
  total_client_paid = filtered_df[client_col].sum() if client_col in filtered_df.columns else 0
  total_office_paid = filtered_df[office_col].sum() if office_col in filtered_df.columns else 0
  total_cartons = int(filtered_df[ctns_col].sum()) if ctns_col in filtered_df.columns else 0
  total_volume = round(filtered_df[cbm_col].sum(), 3) if cbm_col in filtered_df.columns else 0.0

  # مجاميع الأعمدة الإضافية لشحنة الجمرك والمستخلصات
  sh_customs = filtered_df[customs_col].sum() if customs_col in filtered_df.columns else 0
  sh_collected = filtered_df[collected_col].sum() if collected_col in filtered_df.columns else 0
  sh_remaining = filtered_df[remaining_col].sum() if remaining_col in filtered_df.columns else 0

  # تحديد نص حالة الدفع بالدولار $
  if sh_remaining <= 0:
      payment_status_text = "مدفوعة بالكامل ✅"
      status_card_color = "#10b981" 
  else:
      payment_status_text = f"متبقي غير مدفوع ($ {sh_remaining:,.2f}) ⏳"
      status_card_color = "#ef4444" 

  def render_custom_card(title, value, icon, bg_color):
    card_style = f"""
        <div style="
            background-color: {bg_color}; padding: 18px; border-radius: 10px; color: #ffffff;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; font-family: sans-serif;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 14px; opacity: 0.95; font-weight: 500;">{title}</span>
                <span style="font-size: 22px;">{icon}</span>
            </div>
            <div style="font-size: 24px; font-weight: bold; letter-spacing: 0.5px;">{value}</div>
        </div>
        """
    st.markdown(card_style, unsafe_allow_html=True)

  # عرض لوحة المقاييس المعزولة بالكامل للعميل المختار بالدولار $
  row1_col1, row1_col2, row1_col3, row1_col4, row1_col5 = st.columns(5)
  with row1_col1: render_custom_card("إجمالي الشحنات الفرعية", f"{total_orders}", "📋", "#4f46e5")
  with row1_col2: render_custom_card("عدد الحاويات", f"{total_containers}", "🚢", "#0ea5e9")
  with row1_col3: render_custom_card("إجمالي المبالغ المطلوبة", f"$ {total_amount_val:,.2f}", "💵", "#10b981")
  with row1_col4: render_custom_card("إجمالي مدفوعات الزبون", f"$ {total_client_paid:,.2f}", "🤝", "#f59e0b")
  with row1_col5: render_custom_card("إجمالي المدفوع للمكتب", f"$ {total_office_paid:,.2f}", "🏢", "#6366f1")

  row2_col1, row2_col2, row2_col3, row2_col4, row2_col5 = st.columns(5)
  with row2_col1: render_custom_card("إجمالي عدد الكراتين", f"{total_cartons:,}", "📦", "#ec4899")
  with row2_col2: render_custom_card("إجمالي الحجم الكلي (CBM)", f"{total_volume:,}", "📐", "#14b8a6")

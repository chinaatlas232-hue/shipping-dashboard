import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="Logistics Dashboard — B12", page_icon="📦", layout="wide"
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
      
  st.title("إدارة النظام - B12")
  st.markdown("---")

  # رفع ملف إكسل الأم الموحد الذي يحتوي على كل العملاء والشحنات
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
  st.info("👋 مرحباً بك! يرجى رفع ملف الإكسيل الشامل الذي يحتوي على كافة الشحنات والعملاء من الشريط الجانبي لبدء التشغيل.")
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

  # --- 4. عنوان الواجهة الرئيسي للزبائن ---
  st.title("📦 Logistics Dashboard — B12")
  st.markdown("Interactive view of shipments, payments and dynamic balances")
  st.markdown("---")

  # --- 5. أشرطة التصفية السريعة المترابطة مع ميزة قفل الرابط لحماية الخصوصية 🌟 ---
  st.markdown("##### 🗂️ أشرطة التصفية السريعة الذكية:")
  
  # 🌟 جلب كود العميل من الرابط تلقائياً إن وجد لحماية الخصوصية 🌟
  url_params = st.query_params
  url_client = url_params.get("user_code", None)
  
  if client_name_col in df.columns:
      client_options = list(df[client_name_col].dropna().unique())
      
      # إذا دخل الزبون برابط مشفر خاص بكوده
      if url_client and url_client in client_options:
          selected_client = url_client
          df_client = df[df[client_name_col] == selected_client]
          st.success(f"🔓 تم تحميل البيانات الآمنة المخصصة للكود: **{selected_client}**")
      else:
          # إذا دخلت أنت كمدير للنظام، يظهر شريط الأزرار لرؤية الجميع
          client_options_with_all = ["الكل"] + client_options
          selected_client = st.pills("اختر الكود الخاص بك (Customer Code):", options=client_options_with_all, default="الكل", key="client_pill")
          if selected_client != "الكل":
              df_client = df[df[client_name_col] == selected_client]
          else:
              df_client = df
  else:
      df_client = df
      st.warning(f"⚠️ لم نجد عمود باسم '{client_name_col}' في ملفك الحقيقي.")

  # الفلتر الثاني الديناميكي: يعرض فقط الحاويات المتاحة للزبون المختار (يمنع تداخل الحاوية المشتركة)
  container_options = ["الكل"] + list(df_client[container_col].dropna().unique())
  selected_container = st.pills("اختر الحاوية", options=container_options, default="الكل", key="container_pill")

  if selected_container != "الكل":
      temp_df = df_client[df_client[container_col] == selected_container]
  else:
      temp_df = df_client

  # الفلتر الثالث الديناميكي: يعرض فقط ماركات الشحن الخاصة بالزبون والحاوية المختارة
  shipping_mark_options = ["الكل"] + list(temp_df[shipping_mark_col].dropna().unique())
  selected_mark = st.pills("اختر ماركة الشحن (Shipping Mark)", options=shipping_mark_options, default="الكل", key="mark_pill")

  # التصفية النهائية الناتجة عن عزل معلومات الزبون تماماً داخل الحاوية المشتركة
  filtered_df = temp_df
  if selected_mark != "الكل":
      filtered_df = filtered_df[filtered_df[shipping_mark_col] == selected_mark]

  # --- 6. العمليات الحسابية والمؤشرات الديناميكية للعميل المختار حصرياً بالدولار $ ---
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
  with row1_col1: render_custom_card("Orders (الطلبات الفرعية)", f"{total_orders}", "📋", "#4f46e5")
  with row1_col2: render_custom_card("Containers (الحاويات)", f"{total_containers}", "🚢", "#0ea5e9")
  with row1_col3: render_custom_card("Total Amount", f"$ {total_amount_val:,.2f}", "💵", "#10b981")
  with row1_col4: render_custom_card("Client Paid", f"$ {total_client_paid:,.2f}", "🤝", "#f59e0b")
  with row1_col5: render_custom_card("Office Paid", f"$ {total_office_paid:,.2f}", "🏢", "#6366f1")

  row2_col1, row2_col2, row2_col3, row2_col4, row2_col5 = st.columns(5)
  with row2_col1: render_custom_card("Cartons (الكراتين)", f"{total_cartons:,}", "📦", "#ec4899")
  with row2_col2: render_custom_card("Volume (الحجم)", f"{total_volume:,}", "📐", "#14b8a6")
  with row2_col3: render_custom_card("حالة دفع الزبون للشحنة", f"{payment_status_text}", "💳", status_card_color)

  st.markdown("---")

  # --- 7. قسم التحليل المالي التفصيلي للشحنة المحددة والجمارك (بالدولار $) ---
  if selected_container != "الكل" and selected_mark != "الكل":
      st.subheader(f"🔍 التحليل المالي التفصيلي المتقدم للشحنة: {selected_mark}")
      
      sub_col1, sub_col2, sub_col3 = st.columns(3)
      with sub_col1: render_custom_card("مبلغ الجمرك للشحنة", f"$ {sh_customs:,.2f}", "🛡️", "#ef4444")
      with sub_col2: render_custom_card("قيمة الاستحصالات للشحنة", f"$ {sh_collected:,.2f}", "📈", "#3b82f6")
      with sub_col3: render_custom_card("متبقي حقيقي للشحنة", f"$ {sh_remaining:,.2f}", "⏳", "#8b5cf6")
          
      st.markdown("##### 📊 المقارنة المالية التفاعلية للشحنة المحددة")
      sh_metrics = pd.DataFrame({
          "المؤشر": ["مبلغ الجمرك", "قيمة الاستحصالات", "متبقي حقيقي"],
          "القيمة": [sh_customs, sh_collected, sh_remaining]
      })
      
      fig_sh_bar = px.bar(
          sh_metrics, x="المؤشر", y="القيمة", color="المؤشر", template="plotly_dark",
          color_discrete_sequence=["#ef4444", "#3b82f6", "#8b5cf6"]
      )
      st.plotly_chart(fig_sh_bar, use_container_width=True)
      st.markdown("---")

  # --- 8. عرض جدول البيانات المفتوح دائماً والمصفى بدقة متناهية لحماية خصوصية العميل ---
  st.subheader("📋 جدول البيانات الشاملة والنقية (الجدول الأم الكامل)")
  st.dataframe(filtered_df, use_container_width=True, height=550)

  csv_data = filtered_df.to_csv(index=False).encode("utf-8")
  st.sidebar.markdown("---")
  st.sidebar.download_button(
      label="📥 تحميل التقرير الحالي (CSV)", 
      data=csv_data, 
      file_name="logistics_report.csv", 

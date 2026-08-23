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

# --- 2. الشريط الجانبي: إدارة الملفات والأمان ---
with st.sidebar:
  if os.path.exists("logo.png"):
      st.image("logo.png", width=120)
  elif os.path.exists("logo.jpg"):
      st.image("logo.jpg", width=120)
  else:
      st.markdown("<h2 style='margin:0;'>📦</h2>", unsafe_allow_html=True)
      
  st.title("لوحة التحكم اللوجستية")
  st.markdown("---")

  # أ. رفع ملف إكسل النظيف والمعدل
  st.subheader("📁 إدارة ملفات البيانات")
  uploaded_file = st.file_uploader(
      "رفع ملف بيانات الشحنات النظيف (.xlsx)", type=["xlsx", "xls"]
  )

  st.markdown("---")

  # ب. زر التحديث الآمن برقم سري (881988)
  st.subheader("🔄 تحديث النظام")
  with st.form("refresh_form"):
    entered_password = st.text_input(
        "أدخل الرقم السري للتحديث:", type="password"
    )
    submit_refresh = st.form_submit_button("تحديث وتحميل البيانات ⚡")

    if submit_refresh:
      if entered_password == "881988":
        st.cache_data.clear()
        st.success("تم التحديث بنجاح! جاري إعادة التحميل...")
        st.rerun()
      else:
        st.error("الرقم السري غير صحيح!")


# --- 3. قراءة البيانات الأصلية من ملف الإكسيل النظيف ---
@st.cache_data
def load_data(file):
  if file is not None:
    raw_df = pd.read_excel(file, header=0)
    raw_df.columns = raw_df.columns.str.strip()
    return raw_df
  else:
    return pd.DataFrame()


df = load_data(uploaded_file)

# التحقق من رفع الملف لعرض الداش بورد
if df.empty:
  st.info(
      "👋 مرحباً بك! يرجى رفع ملف الإكسيل النظيف من الشريط الجانبي لبدء حساب وعرض البيانات فوراً."
  )
else:
  # مسميات الأعمدة الأساسية
  container_col = "رقم الحاوية"
  shipping_mark_col = "Shipping mark"
  amt_col = "المجموع"
  client_col = "الزبون دفع"
  office_col = "المكتب دفع"
  ctns_col = "عدد الكارتون"
  cbm_col = "حجم"
  
  # مسميات الأعمدة المالية الخاصة بالجمارك والمستخلصات
  customs_col = "مبلغ الجمرك"
  collected_col = "قيمة الاستحصالات"
  remaining_col = "متبقي حقيقي"

  # تحويل كافة الحقول النصية والمالية إلى قيم رقمية نظيفة لضمان حساب رياضي صائب
  all_numeric_cols = [amt_col, client_col, office_col, ctns_col, cbm_col, customs_col, collected_col, remaining_col]
  for col in all_numeric_cols:
    if col in df.columns:
      df[col] = (
          pd.to_numeric(
              df[col]
              .astype(str)
              .str.replace(r"[^\d.]", "", regex=True),
              errors="coerce",
          )
          .fillna(0)
      )

  # استبعاد أسطر الإجماليات الصلبة من ملف الإكسيل لترك الحسابات لبايثون
  df = df[
      ~df[shipping_mark_col]
      .astype(str)
      .str.lower()
      .str.contains("total|grand|إجمالي", na=False)
  ]
  df = df[df[container_col].notna()]

  # حساب عمود حالة الدفع في الجدول بناءً على المتبقي الحقيقي
  def check_payment_status(row):
      if row[remaining_col] <= 0:
          return "مدفوع بالكامل ✅"
      else:
          return "يوجد متبقي غير مدفوع ⏳"
          
  df["حالة دفع الشحنة"] = df.apply(check_payment_status, axis=1)

  # --- 4. عنوان الواجهة الرئيسي ---
  st.title("📦 Logistics Dashboard — B12")
  st.markdown(
      "Interactive view of shipments by container, shipping mark, payments and freight"
  )
  st.markdown("---")

  # --- 5. شريط التصفية والسيليكر المزدوج (الحاويات + ماركة الشحن) ---
  st.markdown("##### 🗂️ أشرطة التصفية السريعة الذكية:")
  
  container_options = ["الكل"] + list(df[container_col].dropna().unique())
  selected_container = st.pills(
      "اختر الحاوية",
      options=container_options,
      default="الكل",
      key="container_pill"
  )

  if selected_container != "الكل":
      temp_df = df[df[container_col] == selected_container]
  else:
      temp_df = df

  shipping_mark_options = ["الكل"] + list(temp_df[shipping_mark_col].dropna().unique())
  selected_mark = st.pills(
      "اختر ماركة الشحن (Shipping Mark)",
      options=shipping_mark_options,
      default="الكل",
      key="mark_pill"
  )

  filtered_df = temp_df
  if selected_mark != "الكل":
      filtered_df = filtered_df[filtered_df[shipping_mark_col] == selected_mark]

  # --- 6. العمليات الحسابية والمؤشرات الديناميكية الأساسية ---
  total_orders = len(filtered_df)
  total_containers = filtered_df[container_col].nunique()
  total_amount_val = filtered_df[amt_col].sum() if amt_col in filtered_df.columns else 0
  total_client_paid = filtered_df[client_col].sum() if client_col in filtered_df.columns else 0
  total_office_paid = filtered_df[office_col].sum() if office_col in filtered_df.columns else 0
  total_cartons = int(filtered_df[ctns_col].sum()) if ctns_col in filtered_df.columns else 0
  total_volume = round(filtered_df[cbm_col].sum(), 3) if cbm_col in filtered_df.columns else 0.0

  # مجاميع الأعمدة الإضافية
  sh_customs = filtered_df[customs_col].sum() if customs_col in filtered_df.columns else 0
  sh_collected = filtered_df[collected_col].sum() if collected_col in filtered_df.columns else 0
  sh_remaining = filtered_df[remaining_col].sum() if remaining_col in filtered_df.columns else 0

  # تحديد نص حالة الدفع الإجمالي للتقرير بناءً على المتبقي الحقيقي
  if sh_remaining <= 0:
      payment_status_text = "مدفوعة بالكامل ✅"
      status_card_color = "#10b981" 
  else:
      payment_status_text = f"متبقي غير مدفوع (¥ {sh_remaining:,.2f}) ⏳"
      status_card_color = "#ef4444" 

  def render_custom_card(title, value, icon, bg_color):
    card_style = f"""
        <div style="
            background-color: {bg_color};
            padding: 18px;
            border-radius: 10px;
            color: #ffffff;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 15px;
            font-family: sans-serif;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 14px; opacity: 0.95; font-weight: 500;">{title}</span>
                <span style="font-size: 22px;">{icon}</span>
            </div>
            <div style="font-size: 24px; font-weight: bold; letter-spacing: 0.5px;">{value}</div>
        </div>
        """
    st.markdown(card_style, unsafe_allow_html=True)

  # عرض لوحة المقاييس الأساسية المحدثة
  row1_col1, row1_col2, row1_col3, row1_col4, row1_col5 = st.columns(5)
  with row1_col1: render_custom_card("Orders (الطلبات الفرعية)", f"{total_orders}", "📋", "#4f46e5")
  with row1_col2: render_custom_card("Containers (الحاويات)", f"{total_containers}", "🚢", "#0ea5e9")
  with row1_col3: render_custom_card("Total Amount", f"¥ {total_amount_val:,.2f}", "💵", "#10b981")
  with row1_col4: render_custom_card("Client Paid", f"¥ {total_client_paid:,.2f}", "🤝", "#f59e0b")
  with row1_col5: render_custom_card("Office Paid", f"¥ {total_office_paid:,.2f}", "🏢", "#6366f1")

  row2_col1, row2_col2, row2_col3, row2_col4, row2_col5 = st.columns(5)
  with row2_col1: render_custom_card("Cartons (الكراتين)", f"{total_cartons:,}", "📦", "#ec4899")
  with row2_col2: render_custom_card("Volume (الحجم)", f"{total_volume:,}", "📐", "#14b8a6")
  with row2_col3: render_custom_card("حالة دفع الزبون للشحنة", f"{payment_status_text}", "💳", status_card_color)

  st.markdown("---")

  # --- 7. الرسوم البيانية التفاعلية الأساسية ---
  chart_col1, chart_col2 = st.columns(2)

  with chart_col1:
    st.subheader("📊 Payments & Amount by Container")
    y_cols = [c for c in [amt_col, office_col, client_col] if c in filtered_df.columns]
    if y_cols and container_col in filtered_df.columns:
      color_map = {amt_col: "#10b981", office_col: "#6366f1", client_col: "#f59e0b"}
      fig_bar = px.bar(
          filtered_df, x=container_col, y=y_cols, barmode="group",
          template="plotly_dark", color_discrete_map=color_map,
          labels={"value": "المبالغ بالين", "variable": "نوع المال"},
      )
      st.plotly_chart(fig_bar, use_container_width=True)

  with chart_col2:
    st.subheader("🍩 Payment Split (نسب توزيع الأموال)")
    split_data = pd.DataFrame({
        "نوع الدفع": ["Office Paid (المكتب دفع)", "Client Paid (الزبون دفع)"],
        "المبلغ الكلي": [total_office_paid, total_client_paid],
    })
    fig_pie = px.pie(
        split_data, names="نوع الدفع", values="المبلغ الكلي", hole=0.5,
        template="plotly_dark", color_discrete_sequence=["#6366f1", "#f59e0b"] 
    )
    st.plotly_chart(fig_pie, use_container_width=True)

  st.markdown("---")

  # --- 8. قسم التحليل المالي التفصيلي للشحنة المحددة والجمارك ---
  if selected_container != "الكل" and selected_mark != "الكل":
      st.subheader(f"🔍 التحليل المالي التفصيلي المتقدم للشحنة: {selected_mark}")
      
      sub_col1, sub_col2, sub_col3 = st.columns(3)
      with sub_col1: render_custom_card("مبلغ الجمرك للشحنة", f"¥ {sh_customs:,.2f}", "🛡️", "#ef4444")
      with sub_col2: render_custom_card("قيمة الاستحصالات للشحنة", f"¥ {sh_collected:,.2f}", "📈", "#3b82f6")
      with sub_col3: render_custom_card("متبقي حقيقي للشحنة", f"¥ {sh_remaining:,.2f}", "⏳", "#8b5cf6")
          
      st.markdown("##### 📊 المقارنة المالية التفاعلية للشحنة المحددة")
      sh_metrics = pd.DataFrame({
          "المؤشر المالي": ["مبلغ الجمرك", "قيمة الاستحصالات", "متبقي حقيقي"],
          "القيمة بالين": [sh_customs, sh_collected, sh_remaining]
      })
      # 🌟 تم إصلاح إغلاق قوس الـ px.bar المسبب للـ SyntaxError هنا 🌟
      fig_sh_bar = px.bar(
          sh_metrics, x="المؤشر المالي", y="القيمة بالين", 
          color="المؤشر المالي", template="plotly_dark",

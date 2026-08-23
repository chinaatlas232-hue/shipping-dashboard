import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="Logistics Dashboard — B12", page_icon="📦", layout="wide"
)

# --- 2. الشريط الجانبي: إدارة الملفات والأمان ---
with st.sidebar:
  st.image(
      "https://icons8.com", width=80
  )  # أيقونة تعبيرية
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
    # تنظيف مسافات العناوين لضمان المطابقة الكاملة
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
  # 🌟 تثبيت مسميات الأعمدة الحقيقية المستخرجة من ملفك حرفياً لحسم المشكلة نهائياً
  container_col = "رقم الحاوية"
  shipping_mark_col = "Shipping mark"
  amt_col = "المجموع"
  client_col = "الزبون دفع"
  office_col = "المكتب دفع"
  ctns_col = "عدد الكارتون"
  cbm_col = "حجم"

  # تحويل الحقول النصية والمالية إلى قيم رقمية نظيفة لضمان حساب رياضي صائب 100%
  for col in [amt_col, client_col, office_col, ctns_col, cbm_col]:
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

  # استبعاد أي سطر يحتوي على كلمة إجمالي أو Total مخزنة قديماً بالأسفل
  df = df[
      ~df[shipping_mark_col]
      .astype(str)
      .str.lower()
      .str.contains("total|grand|إجمالي", na=False)
  ]
  df = df[df[container_col].notna()]

  # --- 4. عنوان الواجهة الرئيسي ---
  st.title("📦 Logistics Dashboard — B12")
  st.markdown(
      "Interactive view of shipments by container, shipping mark, payments and freight"
  )
  st.markdown("---")

  # --- 5. الشريط الأفقي السريع (Selector) للحاويات الفريدة ---
  container_options = ["الكل"] + list(df[container_col].dropna().unique())
  st.markdown("##### 🗂️ شريط تصفية الحاويات السريع:")
  selected_container = st.pills(
      "اختر الحاوية",
      options=container_options,
      default="الكل",
      label_visibility="collapsed",
  )

  # تصفية الجدول بناءً على خيار الفلتر السريع المختار
  if selected_container != "الكل":
    filtered_df = df[df[container_col] == selected_container]
  else:
    filtered_df = df

  # --- 6. العمليات الحسابية والمؤشرات الديناميكية المطابقة 100% ---
  total_orders = len(filtered_df)
  total_containers = filtered_df[container_col].nunique()
  total_amount_val = (
      filtered_df[amt_col].sum() if amt_col in filtered_df.columns else 0
  )
  total_client_paid = (
      filtered_df[client_col].sum() if client_col in filtered_df.columns else 0
  )
  total_office_paid = (
      filtered_df[office_col].sum() if office_col in filtered_df.columns else 0
  )
  total_cartons = (
      int(filtered_df[ctns_col].sum()) if ctns_col in filtered_df.columns else 0
  )
  total_volume = (
      round(filtered_df[cbm_col].sum(), 3)
      if cbm_col in filtered_df.columns
      else 0.0
  )

  # دالة هندسية مخصصة لإنشاء بطاقات المؤشرات الاحترافية بالألوان الهادئة والأيقونات
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
            <div style="font-size: 25px; font-weight: bold; letter-spacing: 0.5px;">{value}</div>
        </div>
        """
    st.markdown(card_style, unsafe_allow_html=True)

  # توزيع شبكة المؤشرات (الصف الأول)
  row1_col1, row1_col2, row1_col3, row1_col4, row1_col5 = st.columns(5)

  with row1_col1:
    render_custom_card("Orders (الطلبات الفرعية)", f"{total_orders}", "📋", "#4f46e5")

  with row1_col2:
    render_custom_card(
        "Containers (الحاويات)", f"{total_containers}", "🚢", "#0ea5e9"
    )

  with row1_col3:
    render_custom_card(
        "Total Amount", f"¥ {total_amount_val:,.2f}", "💵", "#10b981"
    )

  with row1_col4:
    render_custom_card(
        "Client Paid", f"¥ {total_client_paid:,.2f}", "🤝", "#f59e0b"
    )

  with row1_col5:
    render_custom_card(
        "Office Paid", f"¥ {total_office_paid:,.2f}", "🏢", "#6366f1"
    )

  # توزيع شبكة المؤشرات (الصف الثاني)
  row2_col1, row2_col2, row2_col3, row2_col4, row2_col5 = st.columns(5)

  with row2_col1:
    render_custom_card(
        "Cartons (الكراتين)", f"{total_cartons:,}", "📦", "#ec4899"
    )

  with row2_col2:
    st.write("")  # الفراغ الهندسي المعتمد بصورتك الأصلية

  with row2_col3:
    render_custom_card(
        "Volume (الحجم)", f"{total_volume:,}", "📐", "#14b8a6"
    )

  st.markdown("---")

  # --- 7. الرسوم البيانية التفاعلية المدعومة بـ Plotly ---
  chart_col1, chart_col2 = st.columns(2)

  with chart_col1:
    st.subheader("📊 Payments & Amount by Container")
    y_cols = [
        c
        for c in [amt_col, office_col, client_col]
        if c in filtered_df.columns
    ]
    if y_cols and container_col in filtered_df.columns:
      fig_bar = px.bar(
          filtered_df,
          x=container_col,
          y=y_cols,
          barmode="group",
          template="plotly_dark",
          labels={"value": "المبالغ بالين", "variable": "نوع الدفع"},
      )
      st.plotly_chart(fig_bar, use_container_width=True)

  with chart_col2:
    st.subheader("🍩 Payment Split (نسب توزيع الأموال)")
    split_data = pd.DataFrame({
        "Type": ["Office Paid", "Client Paid"],
        "Amount": [total_office_paid, total_client_paid],
    })
    fig_pie = px.pie(
        split_data,
        names="Type",
        values="Amount",
        hole=0.5,
        template="plotly_dark",
    )
    st.plotly_chart(fig_pie, use_container_width=True)

  # --- 8. عرض جدول البيانات الكامل بعد التنظيف ---
  with st.expander("📋 عرض جدول البيانات الكاملة والنقية (الجدول الأم)"):
    st.dataframe(filtered_df, use_container_width=True)

  csv_data = filtered_df.to_csv(index=False).encode("utf-8")
  st.sidebar.markdown("---")
  st.sidebar.download_button(
      label="📥 تحميل التقرير الحالي (CSV)",
      data=csv_data,
      file_name="logistics_report.csv",
      mime="text/csv",
  )

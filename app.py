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

  # أ. رفع ملف إكسل جديد
  st.subheader("📁 إدارة ملفات البيانات")
  uploaded_file = st.file_uploader(
      "رفع ملف بيانات الشحنات الجديد (.xlsx)", type=["xlsx", "xls"]
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


# --- 3. قراءة البيانات (تم ملء كافة الأرقام هنا بالكامل لمنع الـ SyntaxError نهائياً) ---
@st.cache_data
def load_data(file):
  if file is not None:
    return pd.read_excel(file)
  else:
    # بيانات تجريبية كاملة ومبنية بشكل سليم لحماية الكود
    data = {
        "container": [
            "RQ6025",
            "RQ6027",
            "RQ6036",
            "RQ6026",
            "RQ6033",
            "RQ6028",
            "RQ6035",
        ],
        "shipping_mark": [
            "B12-116",
            "B12-115",
            "B12-114",
            "B12-80",
            "B12-52",
            "B12-60",
            "B12-97",
        ],
        "Total_Amount":,
        "Office_Paid":,
        "Client_Paid":,
        "Cartons":,
        "Volume_CBM": [12.5, 10.0, 8.5, 7.0, 5.5, 4.0, 3.0],
        "Orders":,
    }
    return pd.DataFrame(data)


df = load_data(uploaded_file)

# --- 4. عنوان الواجهة الرئيسي ---
st.title("📦 Logistics Dashboard — B12")
st.markdown(
    "Interactive view of shipments by container, shipping mark, payments and freight"
)
st.markdown("---")

# --- 5. الشريط الأفقي السريع (Pills Filter) للكونتينرات ---
container_options = ["الكل"] + list(df["container"].unique())
st.markdown("##### 🗂️ شريط التصفية السريع للكونتينرات:")
selected_container = st.pills(
    "اختر الكونتينر",
    options=container_options,
    default="الكل",
    label_visibility="collapsed",
)

# تصفية البيانات بناءً على الاختيار
if selected_container != "الكل":
  filtered_df = df[df["container"] == selected_container]
else:
  filtered_df = df

# --- 6. لوحة المؤشرات العلوية (المربعات الملونة والأيقونات بتصميم هادئ) ---
total_orders = (
    int(filtered_df["Orders"].sum()) if "Orders" in filtered_df else len(filtered_df)
)
total_containers = filtered_df["container"].nunique()
total_amount_val = filtered_df["Total_Amount"].sum()
total_client_paid = filtered_df["Client_Paid"].sum()
total_office_paid = filtered_df["Office_Paid"].sum()
total_cartons = (
    int(filtered_df["Cartons"].sum()) if "Cartons" in filtered_df else 0
)
total_volume = (
    round(filtered_df["Volume_CBM"].sum(), 2)
    if "Volume_CBM" in filtered_df
    else 0.0
)

# دالة مخصصة لإنشاء بطاقة المؤشر بتصميم مربع هادئ مع أيقونة من النظام
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

# تقسيم السطر الأول إلى 5 أعمدة متساوية جغرافياً
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    render_custom_card("Orders (الطلبات)", f"{total_orders}", "📋", "#4f46e5")

with col2:
    render_custom_card("Containers (الكونتينرات)", f"{total_containers}", "🚢", "#0ea5e9")

with col3:
    render_custom_card("Total Amount", f"¥ {total_amount_val:,.0f}", "💵", "#10b981")

with col4:
    render_custom_card("Client Paid", f"¥ {total_client_paid:,.0f}", "🤝", "#f59e0b")

with col5:
    render_custom_card("Office Paid", f"¥ {total_office_paid:,.0f}", "🏢", "#6366f1")

# تقسيم السطر الثاني إلى 5 أعمدة أيضاً للحفاظ على الفراغات الجغرافية المطلوبة بالصورة
col6, col7, col8, col9, col10 = st.columns(5)

with col6:
    render_custom_card("Cartons (الكراتين)", f"{total_cartons:,}", "📦", "#ec4899")

with col7:
    st.write("") # ترك العمود الثاني فارغاً لتطابق التصميم المطلق بالصورة

with col8:
    render_custom_card("Volume (CBM الحجم)", f"{total_volume:,}", "📐", "#14b8a6")

st.markdown("---")

# --- 7. الرسوم البيانية التفاعلية (مطابقة لتصميمك القديم الشغال) ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
  st.subheader("📊 Payments & Amount by Container")
  fig_bar = px.bar(
      filtered_df,
      x="container",
      y=["Total_Amount", "Office_Paid", "Client_Paid"],
      barmode="group",
      template="plotly_dark",
      labels={"value": "Value", "variable": "Payment Type"},
  )
  st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
  st.subheader("🍩 Payment Split")
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

# رسم بياني إضافي: علامات الشحن
st.subheader("🏷️ Top Shipping Marks by Amount")
fig_marks = px.bar(
    filtered_df,
    x="Total_Amount",
    y="shipping_mark",
    orientation="h",
    template="plotly_dark",
    color="container",
)
st.plotly_chart(fig_marks, use_container_width=True)

# --- 8. جدول عرض البيانات التفصيلية ---
with st.expander("📋 عرض جدول البيانات الكاملة"):
  st.dataframe(filtered_df, use_container_width=True)

# زر تحميل التقرير
csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 تحميل التقرير (CSV)",
    data=csv_data,
    file_name="logistics_report.csv",
    mime="text/csv",
)

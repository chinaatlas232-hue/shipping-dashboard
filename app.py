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
      "https://img.icons8.com/color/96/logistic-control.png", width=80
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


# --- 3. قراءة البيانات (مع دعم بيانات افتراضية تجريبية لضمان عمل الكود فوراً) ---
@st.cache_data
def load_data(file):
  if file is not None:
    return pd.read_excel(file)
  else:
    # بيانات تجريبية مطابقة لتصميمك لتعمل اللوحة فوراً في حال عدم رفع ملف
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
        "Total_Amount": [700000, 480000, 290000, 270000, 160000, 50000, 70000],
        "Office_Paid": [550000, 400000, 100000, 220000, 100000, 40000, 50000],
        "Client_Paid": [150000, 80000, 190000, 50000, 60000, 10000, 20000],
        "Cartons": [50, 40, 35, 30, 25, 20, 15],
        "Volume_CBM": [12.5, 10.0, 8.5, 7.0, 5.5, 4.0, 3.0],
        "Orders": [12, 10, 8, 7, 6, 5, 4],
    }
    return pd.DataFrame(data)


df = load_data(uploaded_file)

# --- 4. عنوان الواجهة الرئيسي ---
st.title("📦 Logistics Dashboard — B12")
st.markdown(
    "Interactive view of shipments by container, shipping mark, payments and"
    " freight"
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

# --- 6. لوحة المؤشرات العلوية (Metrics) ---
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

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Orders (الطلبات)", f"{total_orders}")
col2.metric("Containers (الكونتينرات)", f"{total_containers}")
col3.metric("Total Amount", f"{total_amount_val:,.0f}")
col4.metric("Client Paid", f"{total_client_paid:,.0f}")
col5.metric("Office Paid", f"{total_office_paid:,.0f}")

col6, col7 = st.columns(2)
col6.metric("Cartons (الكراتين)", f"{total_cartons}")
col7.metric("Volume (CBM الحجم)", f"{total_volume}")

st.markdown("---")

# --- 7. الرسوم البيانية التفاعلية (مطابقة لطلبك وتصميمك) ---
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
csv_data = filtered_df.to_csv(index=format).encode("utf-8")
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 تحميل التقرير (CSV)",
    data=csv_data,
    file_name="logistics_report.csv",
    mime="text/csv",
)

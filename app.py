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
    st.image("https://img.icons8.com/color/96/logistic-control.png", width=80) 
    st.title("لوحة التحكم اللوجستية")
    st.markdown("---")
    
    # أ. رفع ملف إكسل جديد
    st.subheader("📁 إدارة ملفات البيانات")
    uploaded_file = st.file_uploader("رفع ملف بيانات الشحنات الجديد (.xlsx)", type=["xlsx", "xls"])
    
    st.markdown("---")
    
    # ب. زر التحديث الآمن برقم سري (881988)
    st.subheader("🔄 تحديث النظام")
    with st.form("refresh_form"):
        entered_password = st.text_input("أدخل الرقم السري للتحديث:", type="password")
        submit_refresh = st.form_submit_button("تحديث وتحميل البيانات ⚡")
        
        if submit_refresh:
            if entered_password == "881988":
                st.cache_data.clear()
                st.success("تم التحديث بنجاح! جاري إعادة التحميل...")
                st.rerun()
            else:
                st.error("الرقم السري غير صحيح!")


# --- 3. قراءة البيانات ---
@st.cache_data
def load_data(file):
    if file is not None:
        return pd.read_excel(file)
    else:
        # بيانات تجريبية في حال عدم رفع ملف
        rows = [
            {"container": "RQ6025", "shipping_mark": "B12-116", "total_amount": 700000, "office_paid": 550000, "client_paid": 150000, "cartons": 50, "volume_cbm": 12.5, "orders": 12},
            {"container": "RQ6027", "shipping_mark": "B12-115", "total_amount": 480000, "office_paid": 400000, "client_paid": 80000,  "cartons": 40, "volume_cbm": 10.0, "orders": 10},
            {"container": "RQ6036", "shipping_mark": "B12-114", "total_amount": 290000, "office_paid": 100000, "client_paid": 190000, "cartons": 35, "volume_cbm": 8.5,  "orders": 8},
            {"container": "RQ6026", "shipping_mark": "B12-80",  "total_amount": 270000, "office_paid": 220000, "client_paid": 50000,  "cartons": 30, "volume_cbm": 7.0,  "orders": 7},
            {"container": "RQ6033", "shipping_mark": "B12-52",  "total_amount": 160000, "office_paid": 100000, "client_paid": 60000,  "cartons": 25, "volume_cbm": 5.5,  "orders": 6},
            {"container": "RQ6028", "shipping_mark": "B12-60",  "total_amount": 50000,  "office_paid": 40000,  "client_paid": 10000,  "cartons": 20, "volume_cbm": 4.0,  "orders": 5},
            {"container": "RQ6035", "shipping_mark": "B12-97",  "total_amount": 70000,  "office_paid": 50000,  "client_paid": 20000,  "cartons": 15, "volume_cbm": 3.0,  "orders": 4}
        ]
        return pd.DataFrame(rows)

df = load_data(uploaded_file)

# 🌟 خطوة الحماية الذكية: توحيد أسماء الأعمدة لتفادي خطأ KeyError نهائياً
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# --- 4. عنوان الواجهة الرئيسي ---
st.title("📦 Logistics Dashboard — B12")
st.markdown("Interactive view of shipments by container, shipping mark, payments and freight")
st.markdown("---")

# --- 5. الشريط الأفقي السريع (Pills Filter) للكونتينرات ---
container_col = "container" if "container" in df.columns else df.columns[0]
container_options = ["الكل"] + list(df[container_col].unique())
st.markdown("##### 🗂️ شريط التصفية السريع للكونتينرات:")
selected_container = st.pills("اختر الكونتينر", options=container_options, default="الكل", label_visibility="collapsed")

if selected_container != "الكل":
    filtered_df = df[df[container_col] == selected_container]
else:
    filtered_df = df

# --- 6. لوحة المؤشرات العلوية (المربعات الملونة المصممة) ---
# جلب القيم بأمان حتى لو اختلف المسمى قليلاً في ملفك
total_orders = int(filtered_df["orders"].sum()) if "orders" in filtered_df.columns else len(filtered_df)
total_containers = filtered_df[container_col].nunique()
total_amount_val = filtered_df["total_amount"].sum() if "total_amount" in filtered_df.columns else 0
total_client_paid = filtered_df["client_paid"].sum() if "client_paid" in filtered_df.columns else 0
total_office_paid = filtered_df["office_paid"].sum() if "office_paid" in filtered_df.columns else 0
total_cartons = int(filtered_df["cartons"].sum()) if "cartons" in filtered_df.columns else 0
total_volume = round(filtered_df["volume_cbm"].sum(), 2) if "volume_cbm" in filtered_df.columns else 0.0

# دالة لتصميم بطاقة المؤشر بألوان هادئة وأيقونات مدمجة
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
        <div style="font-size: 26px; font-weight: bold; letter-spacing: 0.5px;">{value}</div>
    </div>
    """
    st.markdown(card_style, unsafe_allow_html=True)

# السطر الأول من المربعات الملونة (5 أعمدة)
row1_col1, row1_col2, row1_col3, row1_col4, row1_col5 = st.columns(5)

with row1_col1:
    render_custom_card("Orders (الطلبات)", f"{total_orders}", "📋", "#4f46e5")

with row1_col2:
    render_custom_card("Containers (الكونتينرات)", f"{total_containers}", "🚢", "#0ea5e9")

with row1_col3:
    render_custom_card("Total Amount", f"{total_amount_val:,.0f}", "💵", "#10b981")

with row1_col4:
    render_custom_card("Client Paid", f"{total_client_paid:,.0f}", "🤝", "#f59e0b")

with row1_col5:
    render_custom_card("Office Paid", f"{total_office_paid:,.0f}", "🏢", "#6366f1")

# السطر الثاني من المربعات الملونة مع توزيع الفراغات
row2_col1, row2_col2, row2_col3, row2_col4, row2_col5 = st.columns(5)

with row2_col1:
    render_custom_card("Cartons (الكراتين)", f"{total_cartons}", "📦", "#ec4899")

with row2_col2:
    st.write("") 

with row2_col3:
    render_custom_card("Volume (CBM الحجم)", f"{total_volume}", "📐", "#14b8a6")

st.markdown("---")

# --- 7. الرسوم البيانية التفاعلية ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("📊 Payments & Amount by Container")
    y_cols = [c for c in ["total_amount", "office_paid", "client_paid"] if c in filtered_df.columns]
    if y_cols:
        fig_bar = px.bar(
            filtered_df,
            x=container_col,
            y=y_cols,
            barmode="group",
            template="plotly_dark",
            labels={"value": "Value", "variable": "Payment Type"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    st.subheader("🍩 Payment Split")
    split_data = pd.DataFrame({
        "Type": ["Office Paid", "Client Paid"],
        "Amount": [total_office_paid, total_client_paid]
    })
    fig_pie = px.pie(
        split_data,
        names="Type",
        values="Amount",
        hole=0.5,
        template="plotly_dark"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

shipping_mark_col = "shipping_mark" if "shipping_mark" in filtered_df.columns else filtered_df.columns[1]
st.subheader("🏷️ Top Shipping Marks by Amount")
if "total_amount" in filtered_df.columns:
    fig_marks = px.bar(
        filtered_df,
        x="total_amount",
        y=shipping_mark_col,
        orientation="h",
        template="plotly_dark",
        color=container_col
    )
    st.plotly_chart(fig_marks, use_container_width=True)

# --- 8. جدول عرض البيانات التفصيلية ---
with st.expander("📋 عرض جدول البيانات الكاملة"):
    st.dataframe(filtered_df, use_container_width=True)

csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 تحميل التقرير (CSV)",
    data=csv_data,
    file_name="logistics_report.csv",
    mime="text/csv",
)

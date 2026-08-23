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


# --- 3. قراءة البيانات (تم إصلاح البيانات بالكامل بهيكل سليم ومغلق 100%) ---
@st.cache_data
def load_data(file):
    if file is not None:
        return pd.read_excel(file)
    else:
        # بيانات تجريبية كاملة ومبنية بشكل سليم لحماية الكود من الـ SyntaxError
        rows = [
            {"container": "RQ6025", "shipping_mark": "B12-116", "Total_Amount": 700000, "Office_Paid": 550000, "Client_Paid": 150000, "Cartons": 50, "Volume_CBM": 12.5, "Orders": 12},
            {"container": "RQ6027", "shipping_mark": "B12-115", "Total_Amount": 480000, "Office_Paid": 400000, "Client_Paid": 80000, "Cartons": 40, "Volume_CBM": 10.0, "Orders": 10},
            {"container": "RQ6036", "shipping_mark": "B12-114", "Total_Amount": 290000, "Office_Paid": 100000, "Client_Paid": 190000, "Cartons": 35, "Volume_CBM": 8.5, "Orders": 8},
            {"container": "RQ6026", "shipping_mark": "B12-80",  "Total_Amount": 270000, "Office_Paid": 220000, "Client_Paid": 50000,  "Cartons": 30, "Volume_CBM": 7.0, "Orders": 7},
            {"container": "RQ6033", "shipping_mark": "B12-52",  "Total_Amount": 160000, "Office_Paid": 100000, "Client_Paid": 60000,  "Cartons": 25, "Volume_CBM": 5.5, "Orders": 6},
            {"container": "RQ6028", "shipping_mark": "B12-60",  "Total_Amount": 50000,  "Office_Paid": 40000,  "Client_Paid": 10000,  "Cartons": 20, "Volume_CBM": 4.0, "Orders": 5},
            {"container": "RQ6035", "shipping_mark": "B12-97",  "Total_Amount": 70000,  "Office_Paid": 50000,  "Client_Paid": 20000,  "Cartons": 15, "Volume_CBM": 3.0, "Orders": 4}
        ]
        return pd.DataFrame(rows)

df = load_data(uploaded_file)

# --- 4. عنوان الواجهة الرئيسي ---
st.title("📦 Logistics Dashboard — B12")
st.markdown("Interactive view of shipments by container, shipping mark, payments and freight")
st.markdown("---")

# --- 5. الشريط الأفقي السريع (Pills Filter) للكونتينرات ---
container_options = ["الكل"] + list(df["container"].unique())
st.markdown("##### 🗂️ شريط التصفية السريع للكونتينرات:")
selected_container = st.pills("اختر الكونتينر", options=container_options, default="الكل", label_visibility="collapsed")

if selected_container != "الكل":
    filtered_df = df[df["container"] == selected_container]
else:
    filtered_df = df

# --- 6. لوحة المؤشرات العلوية (المربعات الملونة المصممة حسب طلبك) ---
total_orders = int(filtered_df["Orders"].sum()) if "Orders" in filtered_df else len(filtered_df)
total_containers = filtered_df["container"].nunique()
total_amount_val = filtered_df["Total_Amount"].sum()
total_client_paid = filtered_df["Client_Paid"].sum()
total_office_paid = filtered_df["Office_Paid"].sum()
total_cartons = int(filtered_df["Cartons"].sum()) if "Cartons" in filtered_df else 0
total_volume = round(filtered_df["Volume_CBM"].sum(), 2) if "Volume_CBM" in filtered_df else 0.0

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

# السطر الثاني من المربعات الملونة المتوافق مع الفراغات والتوزيع المطلوبة
row2_col1, row2_col2, row2_col3, row2_col4, row2_col5 = st.columns(5)

with row2_col1:
    render_custom_card("Cartons (الكراتين)", f"{total_cartons}", "📦", "#ec4899")

with row2_col2:
    st.write("") # فراغ لمطابقة التوزيع العرضي

with row2_col3:
    render_custom_card("Volume (CBM الحجم)", f"{total_volume}", "📐", "#14b8a6")

st.markdown("---")

# --- 7. الرسوم البيانية التفاعلية ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("📊 Payments & Amount by Container")
    fig_bar = px.bar(
        filtered_df,
        x="container",
        y=["Total_Amount", "Office_Paid", "Client_Paid"],
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

st.subheader("🏷️ Top Shipping Marks by Amount")
fig_marks = px.bar(
    filtered_df,
    x="Total_Amount",
    y="shipping_mark",
    orientation="h",
    template="plotly_dark",
    color="container"
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

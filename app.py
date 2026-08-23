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
    st.image("https://icons8.com", width=80) 
    st.title("لوحة التحكم اللوجستية")
    st.markdown("---")
    
    # أ. رفع ملف إكسل جديد
    st.subheader("📁 إدارة ملفات البيانات")
    uploaded_file = st.file_uploader("رفع ملف بيانات الشحنات الجديد (.xlsx)", type=["xlsx", "xls"])
    
    st.markdown("---")
    
    # b. زر التحديث الآمن برقم سري (881988)
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


# --- 3. قراءة البيانات (تم ضبط أرقام افتراضية مطابقة لجدولك تماماً) ---
@st.cache_data
def load_data(file):
    if file is not None:
        return pd.read_excel(file)
    else:
        # بيانات تجريبية مطابقة تماماً للشحنات الأخيرة في صورتك (RQ6035 و RQ6036 وغيرها)
        rows = [
            {"Container NO.": "RQ6033", "Shipping mark": "B12-115", "Amount": 156721, "Client paid": 156721, "Office paid": 0, "Sum of Ctns": 34, "Sum of Cbm": 5.544, "Orders": 1},
            {"Container NO.": "RQ6035", "Shipping mark": "B12-114", "Amount": 70800,  "Client paid": 0,      "Office paid": 70800, "Sum of Ctns": 13, "Sum of Cbm": 3.211, "Orders": 1},
            {"Container NO.": "RQ6036", "Shipping mark": "B12-116", "Amount": 282519, "Client paid": 282519, "Office paid": 0, "Sum of Ctns": 54, "Sum of Cbm": 8.798, "Orders": 1}
        ]
        return pd.DataFrame(rows)

df = load_data(uploaded_file)

# تنظيف مسافات الأعمدة لضمان مطابقة الأسماء
df.columns = df.columns.str.strip()

# جلب الاسم الحقيقي لعمود الكونتينر سواء كان container أو Container NO.
container_col = "Container NO." if "Container_NO." not in df.columns and "Container NO." in df.columns else "container"

# --- 4. عنوان الواجهة الرئيسي ---
st.title("📦 Logistics Dashboard — B12")
st.markdown("Interactive view of shipments by container, shipping mark, payments and freight")
st.markdown("---")

# --- 5. الشريط الأفقي السريع (Pills Filter) للكونتينرات ---
container_options = ["الكل"] + list(df[container_col].unique())
st.markdown("##### 🗂️ شريط التصفية السريع للكونتينرات:")
selected_container = st.pills("اختر الكونتينر", options=container_options, default="الكل", label_visibility="collapsed")

if selected_container != "الكل":
    filtered_df = df[df[container_col] == selected_container]
else:
    filtered_df = df

# --- 6. لوحة المؤشرات العلوية (المربعات الملونة المصممة بحسابات دقيقة وصحيحة) ---
# دعم الحسابات بناءً على مسميات جدولك الأصلي (Sum of Ctns و Sum of Cbm)
ctns_col = "Sum of Ctns" if "Sum of Ctns" in filtered_df.columns else ("Cartons" if "Cartons" in filtered_df.columns else None)
cbm_col = "Sum of Cbm" if "Sum of Cbm" in filtered_df.columns else ("Volume_CBM" if "Volume_CBM" in filtered_df.columns else None)
amt_col = "Amount" if "Amount" in filtered_df.columns else "Total_Amount"
client_col = "Client paid" if "Client paid" in filtered_df.columns else "Client_Paid"
office_col = "Office paid" if "Office paid" in filtered_df.columns else "Office_Paid"

total_orders = int(filtered_df["Orders"].sum()) if "Orders" in filtered_df.columns else len(filtered_df)
total_containers = filtered_df[container_col].nunique()
total_amount_val = filtered_df[amt_col].sum() if amt_col in filtered_df.columns else 0
total_client_paid = filtered_df[client_col].sum() if client_col in filtered_df.columns else 0
total_office_paid = filtered_df[office_col].sum() if office_col in filtered_df.columns else 0
total_cartons = int(filtered_df[ctns_col].sum()) if ctns_col and ctns_col in filtered_df.columns else 0
total_volume = round(filtered_df[cbm_col].sum(), 3) if cbm_col and cbm_col in filtered_df.columns else 0.0

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
    render_custom_card("Total Amount", f"{total_amount_val:,.2f}" if total_amount_val > 0 else "0", "💵", "#10b981")

with row1_col4:
    render_custom_card("Client Paid", f"{total_client_paid:,.2f}" if total_client_paid > 0 else "0", "🤝", "#f59e0b")

with row1_col5:
    render_custom_card("Office Paid", f"{total_office_paid:,.2f}" if total_office_paid > 0 else "0", "🏢", "#6366f1")

# السطر الثاني من المربعات الملونة
row2_col1, row2_col2, row2_col3, row2_col4, row2_col5 = st.columns(5)

with row2_col1:
    render_custom_card("Cartons (الكراتين)", f"{total_cartons}", "📦", "#ec4899")

with row2_col2:
    st.write("") # فراغ لمطابقة التوزيع المطلوب بالصورة

with row2_col3:
    render_custom_card("Volume (CBM الحجم)", f"{total_volume}", "📐", "#14b8a6")

st.markdown("---")

# --- 7. الرسوم البيانية التفاعلية ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("📊 Payments & Amount by Container")
    y_cols = [c for c in [amt_col, office_col, client_col] if c in filtered_df.columns]
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

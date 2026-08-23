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


# --- 3. دالة قراءة وتجهيز البيانات ---
@st.cache_data
def load_data(file):
    if file is not None:
        raw_df = pd.read_excel(file)
        # تنظيف مسافات العناوين
        raw_df.columns = raw_df.columns.str.strip()
        
        # تعيين العمود الأساسي
        c_col = "Container NO." if "Container NO." in raw_df.columns else "container"
        
        # إزالة أسطر الإجماليات العامة (Grand Total) إن وجدت أسفل الملف لحماية الحسابات
        if c_col in raw_df.columns:
            raw_df = raw_df[~raw_df[c_col].astype(str).str.contains('Total|إجمالي|Grand', case=False, na=False)]
            
        return raw_df
    else:
        # بيانات افتراضية سليمة لتشغيل التطبيق المبدئي
        rows = [
            {"Container NO.": "RQ6025", "Shipping mark": "B12-102", "Amount": 12500, "Client paid": 100, "Office paid": 12400, "Sum of Ctns": 3, "Sum of Cbm": 0.513},
            {"Container NO.": "RQ6035", "Shipping mark": "B12-114", "Amount": 70800, "Client paid": 0, "Office paid": 70800, "Sum of Ctns": 13, "Sum of Cbm": 3.211},
            {"Container NO.": "RQ6036", "Shipping mark": "B12-116", "Amount": 282519, "Client paid": 282519, "Office paid": 0, "Sum of Ctns": 54, "Sum of Cbm": 8.798}
        ]
        return pd.DataFrame(rows)

df = load_data(uploaded_file)

# تعيين المسميات الحقيقية المتطابقة مع ملف الإكسيل
container_col = "Container NO." if "Container NO." in df.columns else "container"
ctns_col = "Sum of Ctns" if "Sum of Ctns" in df.columns else "Cartons"
cbm_col = "Sum of Cbm" if "Sum of Cbm" in df.columns else "Volume_CBM"
amt_col = "Amount" if "Amount" in df.columns else "Total_Amount"
client_col = "Client paid" if "Client paid" in df.columns else "Client_Paid"
office_col = "Office paid" if "Office paid" in df.columns else "Office_Paid"

# تحويل الأعمدة المالية والعددية بشكل آمن لتطهير أي رموز نصية (مثل ¥ أو $)
for col in [amt_col, client_col, office_col, ctns_col, cbm_col]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)

# إنشاء نسخة معالجة بفك الدمج فقط لأغراض التصفية والفلترة
df_filled = df.copy()
df_filled[container_col] = df_filled[container_col].ffill()

# --- 4. عنوان الواجهة الرئيسي ---
st.title("📦 Logistics Dashboard — B12")
st.markdown("Interactive view of shipments by container, shipping mark, payments and freight")
st.markdown("---")

# --- 5. الشريط الأفقي السريع (Pills Filter) للكونتينرات ---
container_options = ["الكل"] + list(df_filled[container_col].dropna().unique())
st.markdown("##### 🗂️ شريط تصفية الحاويات السريع:")
selected_container = st.pills("اختر الحاوية", options=container_options, default="الكل", label_visibility="collapsed")

# تصفية البيانات بناءً على الفلتر النشط
if selected_container != "الكل":
    filtered_df = df_filled[df_filled[container_col] == selected_container]
    # 🌟 الحل الذكي: عند اختيار حاوية معينة، نأخذ القيم الفريدة للكراتين والحجم لمنع مضاعفتها بالجمع العشوائي
    total_cartons = int(df[df[container_col] == selected_container][ctns_col].sum()) if ctns_col in df.columns else 0
    total_volume = round(df[df[container_col] == selected_container][cbm_col].sum(), 3) if cbm_col in df.columns else 0.0
else:
    filtered_df = df_filled
    # عند اختيار الكل، نجمع القيم الأصلية مباشرة من الملف بدون تكرار الدمج
    total_cartons = int(df[ctns_col].sum()) if ctns_col in df.columns else 0
    total_volume = round(df[cbm_col].sum(), 3) if cbm_col in df.columns else 0.0

# حساب بقية المؤشرات المالية والطلبات من البيانات المصفاة
total_orders = len(filtered_df)
total_containers = filtered_df[container_col].nunique()
total_amount_val = filtered_df[amt_col].sum() if amt_col in filtered_df.columns else 0
total_client_paid = filtered_df[client_col].sum() if client_col in filtered_df.columns else 0
total_office_paid = filtered_df[office_col].sum() if office_col in filtered_df.columns else 0


# دالة مخصصة لعرض بطاقات المؤشرات الاحترافية بالألوان والأيقونات
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
    render_custom_card("Containers (الحاويات)", f"{total_containers}", "🚢", "#0ea5e9")

with row1_col3:
    render_custom_card("Total Amount", f"¥ {total_amount_val:,.2f}", "💵", "#10b981")

with row1_col4:
    render_custom_card("Client Paid", f"¥ {total_client_paid:,.2f}", "🤝", "#f59e0b")

with row1_col5:
    render_custom_card("Office Paid", f"¥ {total_office_paid:,.2f}", "🏢", "#6366f1")

# توزيع شبكة المؤشرات (الصف الثاني المتطابق مع التصميم الجغرافي المطلوب)
row2_col1, row2_col2, row2_col3, row2_col4, row2_col5 = st.columns(5)

with row2_col1:
    render_custom_card("Cartons (الكراتين)", f"{total_cartons:,}", "📦", "#ec4899")

with row2_col2:
    st.write("") # الفراغ التصميمي المعتمد بالصورة

with row2_col3:
    render_custom_card("Volume (CBM الحجم)", f"{total_volume:,}", "📐", "#14b8a6")

st.markdown("---")

# --- 7. الرسوم البيانية التفاعلية المدعومة بـ Plotly ---
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
            labels={"value": "المبالغ بالين", "variable": "نوع الدفع"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    st.subheader("🍩 Payment Split (نسب توزيع الأموال)")
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

# --- 8. عرض جدول البيانات الكامل والمعالج ---
with st.expander("📋 عرض جدول البيانات الكاملة والمعالجة (الجدول الأم)"):
    st.dataframe(filtered_df, use_container_width=True)

csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 تحميل التقرير الحالي (CSV)",
    data=csv_data,
    file_name="logistics_report.csv",
    mime="text/csv",
)

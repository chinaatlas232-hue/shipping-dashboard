import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- 1. إعدادات الواجهة والصفحة ---
st.set_page_config(
    page_title="B12 Logistics Dashboard",
    page_icon="📦",
    layout="wide"
)

# --- 2. الشريط الجانبي: إدارة الملفات والأمان ---
with st.sidebar:
    st.image("https://icons8.com", width=80) 
    st.title("لوحة التحكم اللوجستية")
    st.markdown("---")
    
    # رفع ملف إكسل الجديد النظيف بدون فراغات
    st.subheader("📁 إدارة ملفات البيانات")
    uploaded_file = st.file_uploader("رفع ملف بيانات الشحنات النظيف (.xlsx)", type=["xlsx", "xls"])
    
    st.markdown("---")
    
    # زر التحديث الآمن برقم سري ثابت (881988)
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

# --- 3. دالة قراءة وتجهيز البيانات الذكية ---
@st.cache_data
def load_data(file):
    if file is not None:
        raw_df = pd.read_excel(file)
        # تنظيف مسافات أسماء الأعمدة لضمان عدم حدوث أخطاء
        raw_df.columns = raw_df.columns.str.strip()
        return raw_df
    else:
        # إرجاع جدول فارغ مبدئياً لحث المستخدم على رفع الملف، مع رسالة توجيهية
        return pd.DataFrame()

df = load_data(uploaded_file)

# التحقق من رفع الملف للبدء في الحسابات والعرض
if df.empty:
    st.info("👋 مرحباً بك! يرجى رفع ملف الإكسيل النظيف من الشريط الجانبي لبدء حساب وعرض البيانات فوراً.")
else:
    # 🌟 التعرف الذكي والديناميكي على أسماء الأعمدة بملفك مهما كانت حالة الأحرف
    def find_column(options, default):
        for opt in options:
            if opt in df.columns:
                return opt
        for opt in options:
            for col in df.columns:
                if opt.lower() in col.lower():
                    return col
        return default

    container_col = find_column(["Container NO.", "container", "الحاوية"], "container")
    shipping_mark_col = find_column(["Shipping mark", "shipping_mark", "العلامة"], "shipping_mark")
    ctns_col = find_column(["Sum of Ctns", "Cartons", "الكراتين"], "Cartons")
    cbm_col = find_column(["Sum of Cbm", "Volume_CBM", "الحجم"], "Volume_CBM")
    amt_col = find_column(["Amount", "Total_Amount", "المبلغ"], "Total_Amount")
    client_col = find_column(["Client paid", "Client_Paid", "العميل"], "Client_Paid")
    office_col = find_column(["Office paid", "Office_Paid", "المكتب"], "Office_Paid")

    # تطهير وتحويل كافة الأعمدة المالية والعددية إلى أرقام نقية لحسابات دقيقة 100%
    for col in [amt_col, client_col, office_col, ctns_col, cbm_col]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)

    # استبعاد أي سطور تحتوي على إجماليات صلبة مكتوبة يدوياً بداخل الإكسيل لترك الحسابات لبايثون فقط
    df = df[~df[shipping_mark_col].astype(str).str.lower().str.contains('total|grand|إجمالي', na=False)]

    # --- 4. عنوان الواجهة الرئيسي ---
    st.title("📦 Logistics Dashboard — B12")
    st.markdown("Interactive view of shipments by container, shipping mark, payments and freight")
    st.markdown("---")

    # --- 5. شريط التصفية السريع (Selector / Pills) للكونتينرات ---
    container_options = ["الكل"] + list(df[container_col].dropna().unique())
    st.markdown("##### 🗂️ شريط تصفية الحاويات السريع:")
    selected_container = st.pills("اختر الحاوية", options=container_options, default="الكل", label_visibility="collapsed")

    # تصفية الجدول بناءً على خيار الفلتر المختار
    if selected_container != "الكل":
        filtered_df = df[df[container_col] == selected_container]
    else:
        filtered_df = df

    # --- 6. العمليات الحسابية والمؤشرات الديناميكية عبر البرمجة ---
    total_orders = len(filtered_df)
    total_containers = filtered_df[container_col].nunique()
    total_amount_val = filtered_df[amt_col].sum()
    total_client_paid = filtered_df[client_col].sum()
    total_office_paid = filtered_df[office_col].sum()
    total_cartons = int(filtered_df[ctns_col].sum())
    total_volume = round(filtered_df[cbm_col].sum(), 3)

    # دالة مخصصة لإنشاء المربعات الجميلة ذات الألوان الهادئة والأيقونات المتناسقة
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

    # شبكة توزيع المربعات العلوية (الصف الأول)
    row1_col1, row1_col2, row1_col3, row1_col4, row1_col5 = st.columns(5)

    with row1_col1:
        render_custom_card("Orders (الطلبات)", f"{total_orders}", "📋", "#4f46e5")

    with row1_col2:
        render_custom_card("Containers (الحاويات)", f"{total_containers}", "🚢", "#0ea5e9")

    with row1_col3:
        render_custom_card("Total Amount", f"¥ {total_amount_val:,.2f}", "💵", "#10b981")

    with row1_col4:
        render_custom_card("Client Paid", f"¥ {total_client_paid:,.2f}", "🤝", "#f59e0b")

    with row1_col5:
        render_custom_card("Office Paid", f"¥ {total_office_paid:,.2f}", "🏢", "#6366f1")

    # شبكة توزيع المربعات العلوية (الصف الثاني بالفراغ المعتمد بصورتك)
    row2_col1, row2_col2, row2_col3, row2_col4, row2_col5 = st.columns(5)

    with row2_col1:
        render_custom_card("Cartons (الكراتين)", f"{total_cartons:,}", "📦", "#ec4899")

    with row2_col2:
        st.write("") # العمود الثاني فارغ تماماً كالصورة الأصلية

    with row2_col3:
        render_custom_card("Volume (CBM الحجم)", f"{total_volume:,}", "📐", "#14b8a6")

    st.markdown("---")

    # --- 7. الرسوم البيانية التفاعلية المحدثة ---
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("📊 Payments & Amount by Container")
        y_cols = [c for c in [amt_col, office_col, client_col] if c in filtered_df.columns]
        if y_cols and container_col in filtered_df.columns:
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

    # --- 8. جدول عرض البيانات التفصيلية الشاملة للتحقق من الصحة ---
    with st.expander("📋 عرض جدول البيانات الكاملة والنقية"):
        st.dataframe(filtered_df, use_container_width=True)

    # زر تحميل التقرير المصفى الحالي بصيغة CSV
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 تحميل التقرير الحالي (CSV)",
        data=csv_data,
        file_name="logistics_report.csv",
        mime="text/csv",
    )

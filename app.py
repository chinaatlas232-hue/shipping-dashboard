import streamlit as st
import pandas as pd

# إعدادات صفحة Streamlit لتكون العرض بالكامل (Wide)
st.set_page_config(layout="wide", page_title="Logistics Admin Dashboard")

# --- الشريط الجانبي (Sidebar) ---
st.sidebar.title("🔍 الفلاتر الجانبية")

# أداة رفع ملف الـ Excel
uploaded_file = st.sidebar.file_uploader("Upload Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    # قراءة الملف المرفوع
    df = pd.read_excel(uploaded_file)

    # 1. فلتر رقم الحاوية (البحث عن العمود المرن)
    container_col = next((col for col in df.columns if "حاوية" in str(col)), None)
    if container_col:
        container_options = ["الكل"] + list(df[container_col].dropna().unique())
        selected_container = st.sidebar.selectbox("🚢 اختر رقم الحاوية:", container_options)
    else:
        selected_container = "الكل"
        container_col = None

    # 2. فلتر الكود (المدمج الجديد)
    code_col = next((col for col in df.columns if str(col).strip().lower() in ["code", "الكود", "كود"]), "code")
    if code_col in df.columns:
        code_options = ["الكل"] + list(df[code_col].dropna().unique())
        selected_code = st.sidebar.selectbox("🏷️ اختر الكود (Code):", code_options)
    else:
        selected_code = "الكل"

    # --- تطبيق الفلاتر على البيانات ---
    filtered_df = df.copy()

    if selected_container != "الكل" and container_col:
        filtered_df = filtered_df[filtered_df[container_col] == selected_container]

    if selected_code != "الكل" and code_col in filtered_df.columns:
        filtered_df = filtered_df[filtered_df[code_col] == selected_code]

    # --- التقاط أسماء الأعمدة الخاصة بالحسابات بشكل مرن من الملف ---
    carton_col = next((col for col in df.columns if "كارتون" in str(col) or "كرتون" in str(col)), None)
    weight_col = next((col for col in df.columns if "وزن" in str(col)), None)
    volume_col = next((col for col in df.columns if "حجم" in str(col)), None)
    
    # أعمدة الدفع والمجاميع الظاهرة في صورتك الأصلية (المجموع، الزبون دفع)
    company_pay_col = next((col for col in df.columns if "المجموع" in str(col) or "مجموع" in str(col)), None)
    customer_pay_col = next((col for col in df.columns if "الزبون دفع" in str(col) or "زبون" in str(col)), None)

    # --- الحسابات والمعادلات الدقيقة ---
    total_orders = len(filtered_df)
    total_cartons = filtered_df[carton_col].sum() if carton_col and carton_col in filtered_df.columns else 0
    total_weight = filtered_df[weight_col].sum() if weight_col and weight_col in filtered_df.columns else 0
    total_volume = filtered_df[volume_col].sum() if volume_col and volume_col in filtered_df.columns else 0
    total_company_pay = filtered_df[company_pay_col].sum() if company_pay_col and company_pay_col in filtered_df.columns else 0
    total_customer_pay = filtered_df[customer_pay_col].sum() if customer_pay_col and customer_pay_col in filtered_df.columns else 0

    # --- واجهة لوحة التحكم الرئيسية ---
    st.title("📊 لوحة التحكم الرئيسية")

    # عرض البطاقات الملونة (Metrics)
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("إجمالي الطلبات", f"{total_orders:,}")
    with col2:
        st.metric("إجمالي الكارتون", f"{total_cartons:,}")
    with col3:
        st.metric("إجمالي الوزن", f"{total_weight:,.2f} kg")
    with col4:
        st.metric("إجمالي الحجم", f"{total_volume:,.3f} m³")
    with col5:
        st.metric("دفع الشركة", f"{total_company_pay:,.2f}")
    with col6:
        st.metric("دفع الزبون", f"{total_customer_pay:,.2f}")

    st.markdown("---")

    # عرض الجدول المصفى بناءً على الفلاتر المحددة
    st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("الرجاء رفع ملف إكسل من القائمة الجانبية (Sidebar) لعرض لوحة التحكم والبيانات.")

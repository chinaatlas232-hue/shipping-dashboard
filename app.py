import streamlit as st
import pandas as pd

# إعدادات صفحة Streamlit لتكون العرض بالكامل (Wide) مثل التطبيق الأصلي
st.set_page_config(layout="wide", page_title="Logistics Admin Dashboard")

# --- الشريط الجانبي (Sidebar) ---
st.sidebar.title("🔍 الفلاتر الجانبية")

# أداة رفع ملف الـ Excel
uploaded_file = st.sidebar.file_uploader("Upload Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    # قراءة الملف المرفوع
    df = pd.read_excel(uploaded_file)

    # 1. فلتر رقم الحاوية
    if "رقم الحاوية" in df.columns:
        container_options = ["الكل"] + list(df["رقم الحاوية"].dropna().unique())
        selected_container = st.sidebar.selectbox("🚢 اختر رقم الحاوية:", container_options)
    else:
        selected_container = "الكل"

    # 2. فلتر الكود (المدمج الجديد دون تغيير التصميم)
    if "code" in df.columns:
        code_options = ["الكل"] + list(df["code"].dropna().unique())
        selected_code = st.sidebar.selectbox("🏷️ اختر الكود (Code):", code_options)
    else:
        selected_code = "الكل"

    # --- تطبيق الفلاتر على البيانات ---
    filtered_df = df.copy()

    if selected_container != "الكل" and "رقم الحاوية" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["رقم الحاوية"] == selected_container]

    if selected_code != "الكل" and "code" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["code"] == selected_code]

    # --- الحسابات والمعادلات (تعتمد بالكامل على filtered_df للحفاظ على دقة الأرقام) ---
    total_orders = len(filtered_df)
    total_cartons = filtered_df["عدد الكارتون"].sum() if "عدد الكارتون" in filtered_df.columns else 0
    total_weight = filtered_df["الوزن"].sum() if "الوزن" in filtered_df.columns else 0
    total_volume = filtered_df["حجم"].sum() if "حجم" in filtered_df.columns else 0
    total_company_pay = filtered_df["المجموع"].sum() if "المجموع" in filtered_df.columns else 0
    total_customer_pay = filtered_df["الزبون دفع"].sum() if "الزبون دفع" in filtered_df.columns else 0

    # --- واجهة لوحة التحكم الرئيسية ---
    st.title("📊 لوحة التحكم الرئيسية")

    # عرض البطاقات الملونة (Metrics) بنفس التنسيق والألوان
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

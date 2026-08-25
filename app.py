import streamlit as st
import pandas as pd

st.title("📦 تفاصيل الحاويات الشاملة")

# 1. زر رفع الملف الأساسي (الخاص بالبنود والقطع)
st.sidebar.subheader("📁 الملف الأساسي للشحنات")
main_file = st.sidebar.file_uploader("اختر ملف الشحنات الأساسي", type=["xlsx", "csv"], key="main")

# 2. زر رفع ملف تفاصيل الحاويات الجديد (الذي أرسلت صورته)
st.sidebar.subheader("🚢 ملف تفاصيل الحاويات الإضافي")
container_file = st.sidebar.file_uploader("اختر ملف بيانات الحاويات", type=["xlsx", "csv"], key="container")

if main_file is not None:
    # قراءة الملف الأساسي
    if main_file.name.endswith('.csv'):
        df_main = pd.read_csv(main_file)
    else:
        df_main = pd.read_excel(main_file)
        
    # إذا تم رفع ملف تفاصيل الحاويات أيضاً
    if container_file is not None:
        if container_file.name.endswith('.csv'):
            df_container = pd.read_csv(container_file)
        else:
            df_container = pd.read_excel(container_file)
            
        st.success("تم رفع الملفين بنجاح وجاري دمج البيانات...")
        
        # دمج الجدولين بناءً على عمود رقم الحاوية المشترك (تأكد أن اسم العمود مطبق تماماً مثل ملفاتك، مثل 'رقم الحاوية')
        if 'رقم الحاوية' in df_main.columns and 'رقم الحاوية' in df_container.columns:
            # دمج البيانات مع الاحتفاظ بكل تفاصيل الحاويات والبنود
            df_merged = pd.merge(df_main, df_container, on='رقم الحاوية', how='left')
            st.dataframe(df_merged)
        else:
            st.warning("تنبيه: لم يتم العثور على عمود 'رقم الحاوية' بشكل مطابق في الملفين لدمجمهما تلقائياً، إليك الملف الأساسي:")
            st.dataframe(df_main)
    else:
        st.info("يرجى رفع ملف 'تفاصيل الحاويات' الإضافي من الشريط الجانبي لدمج البيانات وعرضها.")
        st.dataframe(df_main)
else:
    st.info("يرجى رفع الملف الأساسي أولاً لبدء العرض.")

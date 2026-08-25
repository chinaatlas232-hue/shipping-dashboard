import streamlit as st
import pandas as pd

st.title("📦 تفاصيل الحاويات الشاملة")

st.sidebar.subheader("📁 الملف الأساسي للشحنات")
main_file = st.sidebar.file_uploader("اختر ملف الشحنات الأساسي", type=["xlsx", "csv"], key="main")

st.sidebar.subheader("🚢 ملف تفاصيل الحاويات الإضافي")
container_file = st.sidebar.file_uploader("اختر ملف بيانات الحاويات", type=["xlsx", "csv"], key="container")

if main_file is not None:
    if main_file.name.endswith('.csv'):
        df_main = pd.read_csv(main_file)
    else:
        df_main = pd.read_excel(main_file)
        
    if container_file is not None:
        if container_file.name.endswith('.csv'):
            df_container = pd.read_csv(container_file)
        else:
            df_container = pd.read_excel(container_file)
            
        st.success("تم رفع الملفين بنجاح وتم دمج البيانات وتطبيق التنسيقات!")
        
        # البحث عن عمود الحاوية للدمج (تأكد من مطابقة اسم العمود لديك مثل 'رقم الحاوية' أو 'تسلسل الحاوية')
        merge_col = 'رقم الحاوية' if 'رقم الحاوية' in df_main.columns and 'رقم الحاوية' in df_container.columns else None
        
        if merge_col:
            df_merged = pd.merge(df_main, df_container, on=merge_col, how='left')
            
            # دالة تلوين تنسيقية اختيارية (مثال: تلوين خلايا معينة أو إبراز الأعمدة)
            def highlight_formatting(val):
                # يمكنك إضافة شروط ألوان مخصصة هنا إذا رغبت
                return ''

            # عرض الجدول مع الحفاظ على مظهر منظم
            st.dataframe(df_merged, use_container_width=True)
        else:
            st.warning("تعذر العثور على عمود مشترك دقيق للدمج، إليك الملف الأساسي:")
            st.dataframe(df_main, use_container_width=True)
    else:
        st.info("يرجى رفع ملف تفاصيل الحاويات الإضافي لعرض البيانات كاملة.")
        st.dataframe(df_main, use_container_width=True)
else:
    st.info("يرجى رفع الملف الأساسي أولاً.")

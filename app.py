import streamlit as st
import pandas as pd

st.title("📦 تفاصيل الحاويات الشاملة")

# أزرار الرفع في الشريط الجانبي
st.sidebar.subheader("📁 الملف الأساسي للشحنات")
main_file = st.sidebar.file_uploader("اختر ملف الشحنات الأساسي", type=["xlsx", "csv"], key="main_file_key")

st.sidebar.subheader("🚢 ملف تفاصيل الحاويات الإضافي")
container_file = st.sidebar.file_uploader("اختر ملف بيانات الحاويات", type=["xlsx", "csv"], key="container_file_key")

# التحقق من الملف الأساسي وعرضه
if main_file is not None:
    try:
        if main_file.name.endswith('.csv'):
            df_main = pd.read_csv(main_file)
        else:
            df_main = pd.read_excel(main_file)
            
        # تنظيف أسماء الأعمدة لتجنب أخطاء المسافات
        df_main.columns = df_main.columns.astype(str).str.strip()
        
        # إذا تم رفع ملف الحاويات أيضاً، نحاول دمجه بأمان
        if container_file is not None:
            try:
                if container_file.name.endswith('.csv'):
                    df_container = pd.read_csv(container_file)
                else:
                    df_container = pd.read_excel(container_file)
                
                df_container.columns = df_container.columns.astype(str).str.strip()
                
                # البحث عن عمود مشترك للدمج (مثل رقم الحاوية)
                common_cols = [col for col in df_main.columns if col in df_container.columns]
                
                if common_cols:
                    # دمج باستخدام أول عمود مشترك يتم العثور عليه
                    merge_column = common_cols[0]
                    df_merged = pd.merge(df_main, df_container, on=merge_column, how='left', suffixes=('', '_cont'))
                    st.success(f"تم دمـج الملفين بنجاح بناءً على عمود: '{merge_column}'")
                    st.dataframe(df_merged, use_container_width=True)
                else:
                    st.warning("تم رفع الملفين، لكن لم يتم العثور على عمود مشترك دقيق للدمج (مثل رقم الحاوية). إليك الجدول الأساسي:")
                    st.dataframe(df_main, use_container_width=True)
            
            except Exception as err:
                st.error(f"حدث خطأ أثناء معالجة ملف الحاويات: {err}")
                st.dataframe(df_main, use_container_width=True)
        else:
            st.info("يرجى رفع ملف تفاصيل الحاويات الإضافي إذا رغبت بدمج البيانات.")
            st.dataframe(df_main, use_container_width=True)
            
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف الأساسي: {e}")
else:
    st.info("يرجى رفع الملف الأساسي للشحنات من الشريط الجانبي لبدء العرض.")

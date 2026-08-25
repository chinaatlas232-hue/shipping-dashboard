import pandas as pd
import streamlit as st

# ==========================================
# 1. تعريف دالة تنظيف البيانات (في البداية)
# ==========================================
def clean_dataframe_for_streamlit(df_input: pd.DataFrame) -> pd.DataFrame:
    """تنظيف DataFrame وتوحيد أنواع البيانات لمنع خطأ PyArrow"""
    df_clean = df_input.copy()
    
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object' or isinstance(df_clean[col].dtype, pd.CategoricalDtype):
            s = df_clean[col].astype(str).str.strip()
            s_cleaned = s.replace(['', 'nan', 'None', 'null'], None)
            
            # تنظيف أي رموز عملات أو فواصل
            s_numeric_candidate = s.str.replace(r'[^\d.-]', '', regex=True)
            converted_num = pd.to_numeric(s_numeric_candidate, errors='coerce')
            
            non_null_orig = s_cleaned.dropna()
            if len(non_null_orig) > 0 and converted_num.dropna().count() / len(non_null_orig) > 0.5:
                df_clean[col] = converted_num
            else:
                df_clean[col] = s_cleaned
                
    return df_clean

# ==========================================
# 2. قراءة ملف البيانات
# ==========================================
# قم بتعديل اسم الملف "data.xlsx" أو "data.csv" إلى اسم الملف الخاص بك
try:
    df = pd.read_excel("data.xlsx")  # أو pd.read_csv("data.csv")
except Exception as e:
    st.error(f"حدث خطأ أثناء قراءة ملف البيانات: {e}")
    st.stop()

# ==========================================
# 3. تنظيف البيانات وعرضها
# ==========================================
# استدعاء الدالة بعد قراءة df بنجاح
df = clean_dataframe_for_streamlit(df)

# عرض الجدول على المنصة
st.title("لوحة تحكم الشحن")
st.dataframe(df)

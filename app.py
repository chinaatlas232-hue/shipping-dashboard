import pandas as pd
import streamlit as st

def clean_dataframe_for_streamlit(df: pd.DataFrame) -> pd.DataFrame:
    """
    تنظيف كافة الأعمدة وتحويلها إلى أنواع بيانات متوافقة مع PyArrow/Streamlit
    """
    df_clean = df.copy()
    
    for col in df_clean.columns:
        # إذا كان العمود نصياً أو يحوي كائنات (object)
        if df_clean[col].dtype == 'object' or isinstance(df_clean[col].dtype, pd.CategoricalDtype):
            # 1. تحويل العمود إلى نص وإزالة المساحات الزائدة
            s = df_clean[col].astype(str).str.strip()
            
            # 2. فحص ما إذا كان العمود ينتهي/يبدأ بأرقام أو يحتوي رموز عملات
            # نحول الخانات الفارغة أو النصوص 'nan' إلى NaN
            s_cleaned = s.replace(['', 'nan', 'None', 'null'], None)
            
            # 3. محاولة تنظيف رموز العملات والأرقام (مثل ¥2,732.74)
            s_numeric_candidate = s.str.replace(r'[^\d.-]', '', regex=True)
            
            # محاولة التحويل إلى أرقام
            converted_num = pd.to_numeric(s_numeric_candidate, errors='coerce')
            
            # إذا نجح تحويل معظم القيم غير الفارغة إلى أرقام، نعتمد التحويل الرقمي
            non_null_orig = s_cleaned.dropna()
            if len(non_null_orig) > 0 and converted_num.dropna().count() / len(non_null_orig) > 0.5:
                df_clean[col] = converted_num
            else:
                # وإلا نتركه كنص صافٍ مع استبدال القيم الفارغة بـ None
                df_clean[col] = s_cleaned
                
    return df_clean

# ---------------------------------------------------------
# مثال لتطبيق الحل في كودك:
# ---------------------------------------------------------
# 1. بعد قراءة الملف (سواء من Excel أو CSV)
# df = pd.read_excel("data.xlsx")

# 2. قم بتمرير البيانات للدالة لتنظيفها
df = clean_dataframe_for_streamlit(df)

# 3. الآن يمكنك استخدام st.dataframe بشكل طبيعي دون أخطاء PyArrow
st.dataframe(df, use_container_width=True)

import pandas as pd
import streamlit as st

# 1. ضبط إعدادات الصفحة واستغلال العرض الكامل (wide layout)
st.set_page_config(
    page_title="Logistics Admin Dashboard", page_icon="📦", layout="wide"
)

# 2. إضافة تنسيقات CSS لتكبير حجم الجداول داخل Streamlit
st.markdown(
    """
    <style>
    /* توسيع الحاويات لتأخذ كامل عرض الشاشة */
    .block-container {
        max-width: 99% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* تكبير حجم الخط وارتفاع الصفوف داخل الجداول */
    [data-testid="stDataFrame"] div[role="grid"] {
        font-size: 16px !important;
    }
    
    [data-testid="stDataFrame"] div[role="row"] {
        min-height: 40px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- كود عرض الجدول مع ضبط الارتفاع والعرض ---
# استخدم height لزيادة الطول الرأسي (مثلاً 800 بكسل أو أكثر)
st.dataframe(
    filtered_df,
    use_container_width=True,  # ملء عرض الصفحة بالكامل
    height=850,  # زيادة الارتفاع الرأسي للجدول
)

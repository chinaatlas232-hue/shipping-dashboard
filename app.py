import pandas as pd
import streamlit as st  # <-- يجب أن يكون هذا السطر في البداية

# إعداد الصفحة
st.set_page_config(
    page_title="Logistics Admin Dashboard", page_icon="📦", layout="wide"
)


# دالة تحميل البيانات تأتي بعد الاستيراد
@st.cache_data
def load_data(file):
  ...

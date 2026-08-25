import pandas as pd
import streamlit as st

st.set_page_config(page_title="شركة أطلس المحيط - اعمار الديون", layout="wide")

st.title("⏳ اعمار الديون للعملاء (Aging Report)")

# استبدل 'data.xlsx' باسم ملف Excel الفعلي الموجود في مشروعك
try:
  df = pd.read_excel("data.xlsx")
except Exception as e:
  st.warning("الرجاء تأكد من اسم ملف البيانات الصحيح في مجلد المشروع.")
  # مثال افتراضي لتجنب التوقف إذا لم يوجد الملف بعد
  df = pd.DataFrame()

if not df.empty:
  # تصفية الصفوف بحيث يتم إبقاء القيم التي أكبر من 0 في الإجمالي العام
  if "Grand Total" in df.columns:
    df_filtered = df[df["Grand Total"] > 0]
  else:
    df_filtered = df.copy()

  st.markdown(
      "### جدول اعمار الديون (توزيع المتبقي حسب الحاويات والأكواد النشطة فقط)"
  )
  st.dataframe(df_filtered, use_container_width=True)

  csv = df_filtered.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="Download as CSV",
      data=csv,
      file_name="filtered_aging_report.csv",
      mime="text/csv",
  )

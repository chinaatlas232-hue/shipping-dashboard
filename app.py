import pandas as pd
import streamlit as st

st.set_page_config(page_title="شركة أطلس المحيط - اعمار الديون", layout="wide")

st.title("⏳ اعمار الديون للعملاء (Aging Report)")

# إضافة زر لرفع ملف Excel مباشرة من جهازك لتجنب مشاكل المسار
uploaded_file = st.file_uploader(
    "الرجاء رفع ملف البيانات (ذكاء.xlsx)", type=["xlsx", "csv"]
)

if uploaded_file is not None:
  try:
    df = pd.read_excel(uploaded_file)
  except Exception as e:
    df = pd.read_csv(uploaded_file)

  # تصفية الصفوف بحيث يتم إبقاء القيم التي أكبر من 0 في عمود المتبقي أو الإجمالي
  if "المتبقي" in df.columns:
    df_filtered = df[df["المتبقي"] > 0]
  elif "Grand Total" in df.columns:
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
else:
  st.info("الرجاء رفع ملف 'ذكاء.xlsx' عبر الزر أعلاه لعرض الجدول وتصفيته.")

import pandas as pd
import streamlit as st

# إعداد الصفحة
st.set_page_config(page_title="شركة أطلس المحيط - اعمار الديون", layout="wide")

st.title("⏳ اعمار الديون للعملاء (Aging Report)")

# (مثال على تحميل البيانات - قم باستبداله بمسار ملفك الفعلي)
# df = pd.read_excel('your_data.xlsx')

# افتراض أن لديك DataFrame جاهز باسم df
# خطوة التصفية لاستبعاد الصفوف التي لا تحتوي على مبالغ أو أيام مستحقة (تساوي صفر أو فارغة)
if "Grand Total" in df.columns:
  # تصفية الصفوف بحيث يتم إبقاء القيم التي أكبر من 0 فقط
  df_filtered = df[df["Grand Total"] > 0]
else:
  df_filtered = df.copy()

# عرض العنوان الفرعي للجدول المحدث
st.markdown("### جدول اعمار الديون (توزيع المتبقي حسب الحاويات والأكواد النشطة فقط)")

# عرض الجدول بعد التصفية
st.dataframe(df_filtered, use_container_width=True)

# زر تحميل البيانات المصفاة كملف Excel أو CSV
csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download as CSV",
    data=csv,
    file_name="filtered_aging_report.csv",
    mime="text/csv",
)

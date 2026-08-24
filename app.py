import streamlit as st
import pandas as pd
import io

# إعدادات الصفحة
st.set_page_config(page_title="كشف الكمارك المستحصلة", layout="wide")

# العنوان الرئيسي (تم تعديل الاسم وإزالة Pivot Report)
st.markdown("<h1>💰 كشف الكمارك المستحصلة من العميل</h1>", unsafe_allow_html=True)

# 1. إدخال البحث الذكي
search_query = st.text_input(
    "🔍 بحث ذكي (ابحث برقم الكود، اسم الكفيل، أو رقم الحاوية):", 
    value="b12"
)

# 2. بيانات توضيحية (قم بربطها ببيانات DataFrame الخاصة بك)
# مثال لتجميع البيانات والحسابات:
total_customs = 21844.20
remaining_osama = 10181.10
paid_osama = 11663.10
remaining_pending = 0.00

# 3. عرض البطاقات الإحصائية (KPIs)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="أجور الجمرك الكلي", value=f"${total_customs:,.2f}")

with col2:
    st.metric(label="متبقي (اسامة)", value=f"${remaining_osama:,.2f}")

with col3:
    st.metric(label="مسدد (اسامة)", value=f"${paid_osama:,.2f}")

with col4:
    st.metric(label="متبقي (لم تصل بعد)", value=f"${remaining_pending:,.2f}")

st.markdown("---")

# 4. أزرار التحميل
btn_col1, btn_col2, _ = st.columns([1, 1, 4])

# تجهيز جدول بيانات للعرض والتصدير (مثال للبيانات)
data = {
    "Row Labels": ["— الكفيل: اسامة (B12)", "↳ RQ6025", "↳ RQ6026", "↳ RQ6027", "↳ RQ6028", "↳ RQ6033", "↳ RQ6035", "↳ RQ6036", "Grand Total"],
    "Sum of مبلغ الجمرك": [21844.20, 8419.80, 2549.10, 4915.20, 694.20, 1663.20, 963.30, 2639.40, 21844.20],
    "Sum of قيمة الاستحصالات": [11663.10, 8419.80, 2549.10, 0.00, 694.20, 0.00, 0.00, 0.00, 11663.10],
    "Sum of متبقي حقيقي": [10181.00, 0.00, 0.00, 4915.00, 0.00, 1663.00, 963.00, 2639.00, 10181.00]
}
df = pd.DataFrame(data)

# تصدير Excel
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Sheet1')
excel_data = buffer.getvalue()

with btn_col1:
    st.download_button(
        label="📊 Download as Excel",
        data=excel_data,
        file_name="customs_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with btn_col2:
    st.download_button(
        label="📥 Download as CSV",
        data=df.to_csv(index=False).encode('utf-8-sig'),
        file_name="customs_report.csv",
        mime="text/csv"
    )

st.write("")

# 5. عرض الجدول
st.dataframe(df, use_container_width=True)

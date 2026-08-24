import streamlit as st
import pandas as pd
import io

# إعداد الصفحة
st.set_page_config(page_title="كشف الكمارك المستحصلة", layout="wide")

# إضافة تنسيقات CSS مخصصة لإرجاع التصميم الداكن والألوان
st.markdown("""
<style>
    /* خلفية التطبيق داكنة */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* تصميم البطاقات الإحصائية */
    .kpi-card {
        padding: 18px;
        border-radius: 8px;
        text-align: center;
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .kpi-title { font-size: 14px; margin-bottom: 8px; opacity: 0.9; }
    .kpi-value { font-size: 22px; font-weight: bold; }

    .bg-blue { background-color: #1e3a8a; }
    .bg-orange { background-color: #d97706; }
    .bg-green { background-color: #15803d; }
    .bg-red { background-color: #b91c1c; }

    /* تنسيق الجدول */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 14px;
        background-color: #ffffff;
        color: #000000;
        border-radius: 4px;
        overflow: hidden;
    }
    .styled-table th {
        background-color: #1f2937;
        color: #ffffff;
        text-align: right;
        padding: 10px 15px;
    }
    .styled-table td {
        padding: 8px 15px;
        border-bottom: 1px solid #e5e7eb;
        text-align: right;
    }
    .styled-table tr:nth-of-type(even) {
        background-color: #f9fafb;
    }
    .highlight-row {
        background-color: #f3f4f6;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 1. العنوان الرئيسي
st.markdown("<h2 style='color: white;'>💰 كشف الكمارك المستحصلة من العميل</h2>", unsafe_allow_html=True)

# 2. مربع البحث الذكي
search_query = st.text_input(
    "🔍 بحث ذكي (ابحث برقم الكود، اسم الكفيل، أو رقم الحاوية):", 
    value="b12"
)

st.write("")

# 3. عرض البطاقات الملونة (KPIs)
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
        <div class="kpi-card bg-blue">
            <div class="kpi-title">أجور الجمرك الكلي</div>
            <div class="kpi-value">$21,844.20</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
        <div class="kpi-card bg-orange">
            <div class="kpi-title">متبقي (اسامة)</div>
            <div class="kpi-value">$10,181.10</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
        <div class="kpi-card bg-green">
            <div class="kpi-title">مسدد (اسامة)</div>
            <div class="kpi-value">$11,663.10</div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
        <div class="kpi-card bg-red">
            <div class="kpi-title">متبقي (لم تصل بعد)</div>
            <div class="kpi-value">$0.00</div>
        </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown("---")

# 4. أزرار التحميل
data = {
    "Row Labels": ["— الكفيل: اسامة (B12)", "↳ RQ6025", "↳ RQ6026", "↳ RQ6027", "↳ RQ6028", "↳ RQ6033", "↳ RQ6035", "↳ RQ6036", "Grand Total"],
    "Sum of مبلغ الجمرك": ["$21,844.20", "$8,419.80", "$2,549.10", "$4,915.20", "$694.20", "$1,663.20", "$963.30", "$2,639.40", "$21,844.20"],
    "Sum of قيمة الاستحصالات": ["$11,663.10", "$8,419.80", "$2,549.10", "$0.00", "$694.20", "$0.00", "$0.00", "$0.00", "$11,663.10"],
    "Sum of متبقي حقيقي": ["$10,181", "$0", "$0", "$4,915", "$0", "$1,663", "$963", "$2,639", "$10,181"]
}
df = pd.DataFrame(data)

btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 5])

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Sheet1')
excel_data = buffer.getvalue()

with btn_col1:
    st.download_button("📊 Download as Excel", data=excel_data, file_name="customs_report.xlsx")

with btn_col2:
    st.download_button("📥 Download as CSV", data=df.to_csv(index=False).encode('utf-8-sig'), file_name="customs_report.csv")

# 5. عرض الجدول بتنسيق HTML المخصص
table_html = """
<table class="styled-table">
    <thead>
        <tr>
            <th>#</th>
            <th>Row Labels</th>
            <th>Sum of مبلغ الجمرك</th>
            <th>Sum of قيمة الاستحصالات</th>
            <th>Sum of متبقي حقيقي</th>
        </tr>
    </thead>
    <tbody>
"""

for idx, row in df.iterrows():
    row_class = "highlight-row" if "الكفيل" in str(row["Row Labels"]) or "Grand Total" in str(row["Row Labels"]) else ""
    table_html += f"""
        <tr class="{row_class}">
            <td>{idx}</td>
            <td>{row['Row Labels']}</td>
            <td>{row['Sum of مبلغ الجمرك']}</td>
            <td>{row['Sum of قيمة الاستحصالات']}</td>
            <td>{row['Sum of متبقي حقيقي']}</td>
        </tr>
    """

table_html += "</tbody></table>"

st.markdown(table_html, unsafe_allow_html=True)

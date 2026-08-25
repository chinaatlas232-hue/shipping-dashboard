import pandas as pd
import streamlit as st

st.set_page_config(page_title="لوحة التحكم الرئيسية", layout="wide")


# 1. تحضير وتخزين الأكواد لتسريع الأداء مع +10,000 كود
@st.cache_data
def get_unique_codes(data):
    if "code" in data.columns:
        return sorted(data["code"].dropna().astype(str).unique().tolist())
    return []


# ⚠️ افترضنا وجود dataframe باسم df (أبقِ كود قراءة البيانات الخاص بك كما هو أعلى هذه الجزئية)
# df = pd.read_excel("...")

# --- 2. العنوان الرئيسي الأصلي ---
st.markdown(
    "<h1 style='text-align: right;'>📊 لوحة التحكم الرئيسية</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- 3. شريط البحث (قائمة منسدلة سريعة للأكواد) ---
code_options = get_unique_codes(df)

search_query = st.multiselect(
    "🔍 بحث سريع في كافة الأعمدة (إخفاء باقي البيانات غير المطابقة):",
    options=code_options,
    default=[],
    placeholder="اختر أو اكتب الكود للبحث...",
)

# تصفية البيانات
if search_query:
    filtered_df = df[df["code"].astype(str).isin(search_query)]
else:
    filtered_df = df

# --- 4. الحسابات الديناميكية للبطاقات ---
total_orders = len(filtered_df)
total_cartons = (
    filtered_df["عدد الكارتون"].sum() if "عدد الكارتون" in filtered_df else 0
)
total_weight = filtered_df["الوزن"].sum() if "الوزن" in filtered_df else 0
total_volume = filtered_df["حجم"].sum() if "حجم" in filtered_df else 0
total_company_pay = (
    filtered_df["مكتب دفع"].sum() if "مكتب دفع" in filtered_df else 0
)
total_customer_pay = (
    filtered_df["الزبون دفع"].sum() if "الزبون دفع" in filtered_df else 0
)

# --- 5. إعادة تصميم البطاقات الملونة الأصلية (HTML/CSS) ---
cards_html = f"""
<style>
    .card-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        justify-content: space-between;
        margin-top: 15px;
        margin-bottom: 20px;
        direction: rtl;
    }}
    .card {{
        flex: 1;
        min-width: 140px;
        border-radius: 12px;
        padding: 18px 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    .card-title {{ font-size: 14px; font-weight: bold; margin-bottom: 8px; }}
    .card-value {{ font-size: 20px; font-weight: bold; }}
    .bg-navy {{ background-color: #1e2b6e; }}
    .bg-blue {{ background-color: #0099e5; }}
    .bg-teal {{ background-color: #009688; }}
    .bg-orange {{ background-color: #e67e22; }}
    .bg-green {{ background-color: #27ae60; }}
    .bg-purple {{ background-color: #8e44ad; }}
</style>

<div class="card-container">
    <div class="card bg-navy">
        <div class="card-title">إجمالي الطلبات</div>
        <div class="card-value">{total_orders:,}</div>
    </div>
    <div class="card bg-blue">
        <div class="card-title">إجمالي الكارتون</div>
        <div class="card-value">{total_cartons:,}</div>
    </div>
    <div class="card bg-teal">
        <div class="card-title">إجمالي الوزن</div>
        <div class="card-value">{total_weight:,.2f}<br><small style='font-size:12px'>kg</small></div>
    </div>
    <div class="card bg-orange">
        <div class="card-title">إجمالي الحجم</div>
        <div class="card-value">{total_volume:,.3f}<br><small style='font-size:12px'>m³</small></div>
    </div>
    <div class="card bg-green">
        <div class="card-title">دفع الشركة</div>
        <div class="card-value">${total_company_pay:,.2f}</div>
    </div>
    <div class="card bg-purple">
        <div class="card-title">دفع الزبون</div>
        <div class="card-value">${total_customer_pay:,.2f}</div>
    </div>
</div>
"""

st.markdown(cards_html, unsafe_allow_html=True)

# --- 6. أزرار التحميل (بنفس الشكل الأصلي) ---
col_btn1, col_btn2, _ = st.columns([1.5, 1.5, 7])

csv_data = filtered_df.to_csv(index=False).encode("utf-8-sig")

with col_btn1:
    st.download_button(
        "📊 Download as Excel",
        data=csv_data,
        file_name="data.csv",
        mime="text/csv",
    )
with col_btn2:
    st.download_button(
        "📥 Download as CSV",
        data=csv_data,
        file_name="data.csv",
        mime="text/csv",
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- 7. جدول البيانات الرئيسي ---
st.dataframe(filtered_df, use_container_width=True)

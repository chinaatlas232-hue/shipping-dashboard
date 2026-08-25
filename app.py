import pandas as pd
import streamlit as st

st.set_page_config(page_title="لوحة التحكم الرئيسية", layout="wide")


# 1. دالة قراءة أو جلب البيانات (تأكد من تعديل اسم الملف إذا كان غير data.xlsx)
@st.cache_data
def get_data():
    try:
        return pd.read_excel("data.xlsx")
    except Exception:
        # بيانات تجريبية في حال عدم وجود الملف لتجنب توقف التطبيق
        return pd.DataFrame(
            {
                "No.": [1, 2, 3, 4, 5],
                "code": ["B12", "B12", "B12", "B1020", "B12"],
                "Shipping mark": [
                    "B12-102",
                    "B12-90",
                    "B12-95",
                    "B1020-15",
                    "B12-93",
                ],
                "رقم دخول المخزن": [
                    "RS26040898317",
                    "RS26040898304",
                    "RS26040898300",
                    "RS26040798220",
                    "RS26040798202",
                ],
                "نوع البضاعة": [
                    "Ladys Dress",
                    "Ladys Dress",
                    "Ladys Clothes",
                    "lady suit",
                    "Ladys Dress,",
                ],
                "عدد الكارتون": [3, 1, 1, 3, 3],
                "الوزن": [128, 20, 66, 137, 124],
                "حجم": [0.513, 0.098, 0.383, 0.578, 0.384],
                "رقم الحاوية": [
                    "RQ6025",
                    "RQ6025",
                    "RQ6025",
                    "RQ6025",
                    "RQ6025",
                ],
                "Staff": ["Joyce", "Joyce", "Joyce", "JASMINE", "Joyce"],
                "المجموع": [12500, 4400, 10800, 0, 21350],
                "الزبون دفع": [100, 690, 0, 0, 690],
                "مكتب دفع": [1240, 371, 1080, 0, 2066],
            }
        )


# تحميل المتغير df أولاً لتفادي خطأ NameError
df = get_data()


# 2. استخراج الأكواد بأعلى سرعة وأداء لـ +10,000 كود
@st.cache_data
def get_unique_codes(dataframe):
    if "code" in dataframe.columns:
        return sorted(dataframe["code"].dropna().astype(str).unique().tolist())
    return []


code_options = get_unique_codes(df)

# --- 3. تصميم الواجهة الأصلية ---
st.markdown("<h1>📊 لوحة التحكم الرئيسية</h1>", unsafe_allow_html=True)
st.markdown("---")

# شريط البحث القائمة المنسدلة في نفس المكان والشرط الأصلي
search_query = st.multiselect(
    "🔍 بحث سريع في كافة الأعمدة (إخفاء باقي البيانات غير المطابقة):",
    options=code_options,
    default=[],
    placeholder="اختر أو اكتب الكود للبحث...",
)

# الفلترة
if search_query:
    filtered_df = df[df["code"].astype(str).isin(search_query)]
else:
    filtered_df = df

# --- 4. حسابات البطاقات ---
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

# --- 5. البطاقات الملونة الأصلية (CSS) ---
st.markdown(
    f"""
<style>
    .kpi-container {{
        display: flex;
        flex-direction: row-reverse;
        gap: 10px;
        margin: 20px 0;
    }}
    .kpi-card {{
        flex: 1;
        padding: 15px 5px;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-family: sans-serif;
    }}
    .kpi-title {{ font-size: 14px; font-weight: bold; margin-bottom: 5px; }}
    .kpi-value {{ font-size: 18px; font-weight: bold; }}
    .c-blue1 {{ background-color: #1a237e; }}
    .c-blue2 {{ background-color: #0288d1; }}
    .c-teal {{ background-color: #00897b; }}
    .c-orange {{ background-color: #e65100; }}
    .c-green {{ background-color: #2e7d32; }}
    .c-purple {{ background-color: #7b1fa2; }}
</style>

<div class="kpi-container">
    <div class="kpi-card c-purple">
        <div class="kpi-title">دفع الزبون</div>
        <div class="kpi-value">${total_customer_pay:,.2f}</div>
    </div>
    <div class="kpi-card c-green">
        <div class="kpi-title">دفع الشركة</div>
        <div class="kpi-value">${total_company_pay:,.2f}</div>
    </div>
    <div class="kpi-card c-orange">
        <div class="kpi-title">إجمالي الحجم</div>
        <div class="kpi-value">{total_volume:,.3f} m³</div>
    </div>
    <div class="kpi-card c-teal">
        <div class="kpi-title">إجمالي الوزن</div>
        <div class="kpi-value">{total_weight:,.2f} kg</div>
    </div>
    <div class="kpi-card c-blue2">
        <div class="kpi-title">إجمالي الكارتون</div>
        <div class="kpi-value">{total_cartons:,}</div>
    </div>
    <div class="kpi-card c-blue1">
        <div class="kpi-title">إجمالي الطلبات</div>
        <div class="kpi-value">{total_orders:,}</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# --- 6. أزرار التحميل ---
col1, col2, _ = st.columns([1.5, 1.5, 7])

csv_bytes = filtered_df.to_csv(index=False).encode("utf-8-sig")

with col1:
    st.download_button(
        "📊 Download as Excel",
        data=csv_bytes,
        file_name="data.csv",
        mime="text/csv",
    )
with col2:
    st.download_button(
        "📥 Download as CSV",
        data=csv_bytes,
        file_name="data.csv",
        mime="text/csv",
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- 7. الجدول الرئيسي ---
st.dataframe(filtered_df, use_container_width=True)

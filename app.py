import pandas as pd
import streamlit as st

# 1. إعدادات الصفحة
st.set_page_config(page_title="لوحة التحكم الرئيسية", layout="wide")


# 2. تحميل البيانات وتخزين الأكواد في الذاكرة المؤقتة لتسريع الأداء (+10,000 كود)
@st.cache_data
def load_data():
    # ⚠️ استبدل 'data.xlsx' باسم ملفك الحقيقي (سواء Excel أو CSV)
    # مثال للـ CSV: return pd.read_csv("data.csv")
    try:
        df = pd.read_excel("data.xlsx")
    except:
        # بيانات افتراضية تجريبية في حال عدم وجود الملف
        df = pd.DataFrame(
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
    return df


df = load_data()


# دالة تسريع استخراج الأكواد من العمود
@st.cache_data
def get_unique_codes(data):
    if "code" in data.columns:
        return sorted(data["code"].dropna().astype(str).unique().tolist())
    return []


# --- 3. الهيدر والعنوان الرئيسي ---
st.title("📊 لوحة التحكم الرئيسية")

st.markdown("---")

# --- 4. شريط البحث السريع (القائمة المنسدلة للأكواد) ---
code_options = get_unique_codes(df)

selected_codes = st.multiselect(
    "🔍 بحث سريع في كافة الأعمدة (إخفاء باقي البيانات غير المطابقة):",
    options=code_options,
    default=[],
    placeholder="اختر أو اكتب الكود للبحث...",
)

# تصفية البيانات فوراً بناءً على الأكواد المختارة
if selected_codes:
    filtered_df = df[df["code"].astype(str).isin(selected_codes)]
else:
    filtered_df = df

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. البطاقات الإحصائية (KPIs) ---
# حساب القيم ديناميكياً بناءً على البيانات المفلترة
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

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(label="إجمالي الطلبات", value=f"{total_orders:,}")
with col2:
    st.metric(label="إجمالي الكارتون", value=f"{total_cartons:,}")
with col3:
    st.metric(label="إجمالي الوزن", value=f"{total_weight:,.2f} kg")
with col4:
    st.metric(label="إجمالي الحجم", value=f"{total_volume:,.3f} m³")
with col5:
    st.metric(label="دفع الشركة", value=f"${total_company_pay:,.2f}")
with col6:
    st.metric(label="دفع الزبون", value=f"${total_customer_pay:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. أزرار التحميل ---
btn_col1, btn_col2, _ = st.columns([1, 1, 4])


# تحويل البيانات لملف Excel
@st.cache_data
def convert_to_csv(data):
    return data.to_csv(index=False).encode("utf-8-sig")


csv_data = convert_to_csv(filtered_df)

with btn_col1:
    st.download_button(
        label="📊 Download as Excel",
        data=csv_data,
        file_name="data_export.csv",
        mime="text/csv",
    )

with btn_col2:
    st.download_button(
        label="📥 Download as CSV",
        data=csv_data,
        file_name="data_export.csv",
        mime="text/csv",
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- 7. جدول البيانات الرئيسي ---
st.dataframe(filtered_df, use_container_width=True, hide_index=False)

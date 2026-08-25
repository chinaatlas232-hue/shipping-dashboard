import pandas as pd
import streamlit as st

# 1. تحميل أو تعريف البيانات أولاً (استبدل هذا السطر بطريقة تحميل ملفك مثل pd.read_excel أو pd.read_csv)
# مثال: df = pd.read_excel("data.xlsx")


# 2. دالة استخراج الأكواد لتسريع الأداء مع الأعداد الكبيرة (+10,000)
@st.cache_data
def get_unique_codes(dataframe):
    if "code" in dataframe.columns:
        return sorted(dataframe["code"].dropna().astype(str).unique().tolist())
    return []


# 3. تعريف القائمة المنسدلة للأكواد بعد التأكد من وجود df
if "df" in locals() or "df" in globals():
    unique_codes = get_unique_codes(df)
else:
    unique_codes = []  # قائمة فارغة لتجنب الخطأ في حال لم تُحمل البيانات بعد

# --- واجهة البحث والفلاتر السريعة ---
st.markdown("### 🔍 البحث السريع عن الأكواد")

col1, col2 = st.columns([3, 1])

with col1:
    selected_codes = st.multiselect(
        label="اختر أو اكتب الكود للبحث:",
        options=unique_codes,  # هنا تم تعريف المتغير بنجاح
        default=[],
        placeholder="اختر كود من القائمة...",
    )

with col2:
    st.write("⚡ **فلاتر سريعة:**")
    btn_all = st.button("عرض الكل", use_container_width=True)
    btn_reset = st.button("إعادة ضبط", use_container_width=True)

# تصفية البيانات
if btn_reset:
    selected_codes = []

if selected_codes and not btn_all and ("df" in locals() or "df" in globals()):
    filtered_df = df[df["code"].astype(str).isin(selected_codes)]
elif "df" in locals() or "df" in globals():
    filtered_df = df
else:
    filtered_df = pd.DataFrame()

# عرض الجدول
st.dataframe(filtered_df, use_container_width=True)

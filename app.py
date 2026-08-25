import pandas as pd
import streamlit as st

# إعداد الصفحة لتكون بعرض الشاشة (Wide)
st.set_page_config(
    page_title="نظام إدارة اللوجستيات - النسخة المحدثة",
    page_icon="🚢",
    layout="wide",
)

st.title("📦 إدارة الطلبات والشحنات - لوحة التحكم المحدثة")
st.markdown("---")

# 1. محاكاة قاعدة البيانات (استبدل هذا بملف الـ Excel الخاص بك باستخدام pd.read_excel)
data = {
    "رقم الحاوية": ["RQ6025", "RQ6026", "RQ6025", "RQ6027", "RQ6028"],
    "Code": ["KST", "KST", "QR8120-A1", "QR8116-1", "QR812-135"],
    "رقم دخول المخزن": [
        "RS2608244348",
        "RS26082513728",
        "RS2608244315",
        "RS2608244418",
        "RS2608244322",
    ],
    "نوع البضاعة": [
        "LADYS BAGS",
        "Air conditioner",
        "LADY SUIT",
        "Lady bag",
        "women top",
    ],
    "القطع": [1, 1, 1, 1, 1],
    "الوزن": [72.5, 24.1, 40.0, 30.5, 62.2],
    "CBM": [0.12, 0.14, 0.18, 0.25, 0.22],
    "حالة الطلب": [
        "تحت الإدخال",
        "تم الإدخال",
        "تحت الإدخال",
        "تم الإدخال",
        "جاهز للشحن",
    ],
    "دفع الزبون": [2, 3, 5, 4, 3],
    "دفع الشركة": [4, 6, 8, 7, 6],
}
df = pd.DataFrame(data)

# --- 2. صناديق الإحصائيات العلوية المتحدثة ديناميكياً ---
# (سيتم حسابها لاحقاً بناءً على نتائج البحث والفلترة)

# --- 3. حقول البحث المتقدم والفلاتر (حل مشكلة البحث القديم) ---
st.subheader("🔍 البحث المتقدم وفلترة البيانات بدقة")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
  search_container = st.selectbox(
      "اختر رقم الحاوية:", ["الكل"] + list(df["رقم الحاوية"].unique())
  )

with col_f2:
  search_code = st.text_input(
      "البحث برقم الكود (Code):", placeholder="اكتب الكود بدقة..."
  )

with col_f3:
  search_warehouse = st.text_input(
      "البحث برقم دخول المخزن:", placeholder="اكتب رقم المخزن بدقة..."
  )

# --- 4. تطبيق منطق الفلترة والبحث (دمج الكود القديم والجديد) ---
filtered_df = df.copy()

# أ) فلتر رقم الحاوية (من القائمة الجانبية أو المنسدلة)
if search_container != "الكل":
  filtered_df = filtered_df[
      filtered_df["رقم الحاوية"].astype(str).str.strip()
      == str(search_container).strip()
  ]

# ب) فلتر الكود (مع استخدام المطابقة الدقيقة لمنع جلب نتائج عشوائية خاطئة)
if search_code:
  code_query = search_code.strip().lower()
  filtered_df = filtered_df[
      filtered_df["Code"].astype(str).str.lower().str.strip() == code_query
  ]

# ج) فلتر رقم دخول المخزن (مطابقة دقيقة لمنع الأخطاء)
if search_warehouse:
  wh_query = search_warehouse.strip().lower()
  filtered_df = filtered_df[
      filtered_df["رقم دخول المخزن"].astype(str).str.lower().str.strip()
      == wh_query
  ]

# --- 5. حساب إجماليات الكروت بناءً على البيانات المصفاة فقط ---
total_orders = len(filtered_df)
total_pcs = filtered_df["القطع"].sum() if not filtered_df.empty else 0
total_cbm = filtered_df["CBM"].sum() if not filtered_df.empty else 0
total_weight = filtered_df["الوزن"].sum() if not filtered_df.empty else 0
total_cost = (
    (filtered_df["دفع الشركة"].sum() + filtered_df["دفع الزبون"].sum())
    if not filtered_df.empty
    else 0
)

# عرض الكروت الإحصائية العلوية
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
  st.metric(label="📋 إجمالي الطلبات", value=f"{total_orders}")
with m2:
  st.metric(label="📦 إجمالي القطع", value=f"{total_pcs}")
with m3:
  st.metric(label="📐 إجمالي CBM", value=f"{total_cbm:,.3f}")
with m4:
  st.metric(label="⚖️ إجمالي الوزن", value=f"{total_weight:,.2f} kg")
with m5:
  st.metric(label="💵 إجمالي التكلفة", value=f"${total_cost:,.2f}")

st.markdown("---")

# --- 6. أزرار التصدير وتحديث الجدول ---
col_btn1, col_btn2 = st.columns([1, 6])
with col_btn1:
  if not filtered_df.empty:
    csv_data = filtered_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Export Excel",
        data=csv_data,
        file_name="updated_logistics_report.csv",
        mime="text/csv",
    )

# --- 7. عرض جدول النتائج النهائي ---
st.subheader(f"📋 النتائج المعروضة ({len(filtered_df)} طلب)")
st.dataframe(filtered_df, use_container_width=True)

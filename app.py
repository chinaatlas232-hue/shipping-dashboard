import os
import pandas as pd
import streamlit as st

# 1. إعداد الصفحة وتوسيع المساحة
st.set_page_config(
    page_title="Logistics Admin Dashboard", page_icon="📦", layout="wide"
)

# 2. تنسيق الاستايل وتكبير الجداول والخطوط
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .block-container { max-width: 99% !important; padding-top: 1.5rem !important; }
    
    /* تكبير حجم الخط وارتفاع صفوف الجدول */
    [data-testid="stDataFrame"] div[role="grid"] {
        font-size: 15px !important;
    }
    [data-testid="stDataFrame"] div[role="row"] {
        min-height: 42px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 3. دالة تحميل وحفظ البيانات
DATA_FILE = "shipping_data.xlsx"


def load_data(uploaded_file):
  df = None
  if uploaded_file is not None:
    try:
      df = pd.read_excel(uploaded_file)
      df.to_excel(DATA_FILE, index=False)
      st.sidebar.success("تم حفظ الملف بنجاح ✔️")
    except Exception as e:
      st.sidebar.error(f"خطأ في قراءة الملف: {e}")

  if df is None and os.path.exists(DATA_FILE):
    try:
      df = pd.read_excel(DATA_FILE)
    except Exception:
      df = None

  if df is None:
    df = pd.DataFrame({
        "No": [1, 2, 3, 4, 5],
        "code": ["B12", "B12", "B12", "B1020", "B12"],
        "Shipping mark": ["B12-102", "B12-90", "B12-95", "B1020-15", "B12-93"],
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
            "Ladys Dress",
        ],
        "عدد الكارتون": [3, 1, 1, 3, 3],
        "الوزن": [128, 20, 66, 137, 124],
        "حجم": [0.513, 0.098, 0.383, 0.578, 0.384],
        "المكتب دفع": [25934.0, 13500.0, 9036.0, 12000.0, 5000.0],
        "Client Paid": [500.0, 300.0, 200.0, 150.0, 200.0],
        "رقم الحاوية": ["RQ6026", "RQ6026", "RQ6045", "RQ6045", "RQ6046"],
    })

  df.columns = df.columns.astype(str).str.strip()
  numeric_cols = [
      "المكتب دفع",
      "Client Paid",
      "عدد الكارتون",
      "الوزن",
      "حجم",
  ]
  for col in numeric_cols:
    if col in df.columns:
      df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

  return df


# 4. القائمة الجانبية وتجهيز الفلاتر
st.sidebar.title("🚢 إدارة اللوجستيات")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "📁 رفع ملف Excel جديد", type=["xlsx", "xls"]
)
df = load_data(uploaded_file)

# تعريف المتغير filtered_df أولاً
filtered_df = df.copy()

st.sidebar.markdown("### 🔍 الفلاتر الجانبية")
container_col = (
    "رقم الحاوية"
    if "رقم الحاوية" in df.columns
    else ("رقم الحاويات" if "رقم الحاويات" in df.columns else None)
)

if container_col:
  containers = ["الكل"] + sorted(
      df[container_col].dropna().astype(str).unique().tolist()
  )
  selected_container = st.sidebar.selectbox("🚢 اختر رقم الحاوية:", containers)
  if selected_container != "الكل":
    filtered_df = filtered_df[
        filtered_df[container_col].astype(str) == selected_container
    ]

st.sidebar.markdown("---")
st.sidebar.info("النظام يعمل بكفاءة ✔️")

# 5. عرض محتوى لوحة التحكم والجدول بأبعاد كبيرة
st.title("📊 لوحة التحكم الرئيسية")
st.markdown("---")

# فلتر الكود من القائمة الكاملة
if "code" in df.columns:
  all_codes = ["الكل"] + sorted(
      df["code"].dropna().astype(str).unique().tolist()
  )
  selected_code = st.selectbox(
      "🔍 تصفية إضافية برقم الكود (عرض جميع الأكواد):", all_codes
  )
  if selected_code != "الكل":
    filtered_df = filtered_df[filtered_df["code"].astype(str) == selected_code]

# عرض الجدول بحجم واسع وارتفاع كبير
st.dataframe(filtered_df, use_container_width=True, height=850)

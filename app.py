import os
import pandas as pd
import streamlit as st

# 1. إعداد الصفحة وتوسيع المساحة
st.set_page_config(
    page_title="Logistics Admin Dashboard", page_icon="📦", layout="wide"
)

# 2. تنسيق الاستايلات CSS
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .metric-card {
        padding: 16px; border-radius: 12px; color: white;
        text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .metric-title { font-size: 13px; margin-bottom: 6px; opacity: 0.9; font-weight: 600; }
    .metric-value { font-size: 20px; font-weight: bold; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 98% !important; }
    </style>
""",
    unsafe_allow_html=True,
)

# 3. تحميل البيانات
DATA_FILE = "shipping_data.xlsx"


def load_data(uploaded_file):
  df = None
  if uploaded_file is not None:
    try:
      df = pd.read_excel(uploaded_file)
      df.to_excel(DATA_FILE, index=False)
      st.sidebar.success("تم حفظ الملف الجديد بنجاح ✔️")
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


# 4. القائمة الجانبية واختيار الصفحة
st.sidebar.title("🚢 إدارة اللوجستيات")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "📁 رفع ملف Excel جديد", type=["xlsx", "xls"]
)
df = load_data(uploaded_file)

st.sidebar.markdown("### 🔍 الفلاتر الجانبية")
container_col = (
    "رقم الحاوية"
    if "رقم الحاوية" in df.columns
    else ("رقم الحاويات" if "رقم الحاويات" in df.columns else None)
)

selected_container = "الكل"
if container_col:
  containers = ["الكل"] + sorted(
      df[container_col].dropna().astype(str).unique().tolist()
  )
  selected_container = st.sidebar.selectbox("🚢 اختر رقم الحاوية:", containers)

filtered_df = df.copy()
if selected_container != "الكل" and container_col:
  filtered_df = filtered_df[
      filtered_df[container_col].astype(str) == selected_container
  ]

st.sidebar.markdown("---")

# **إضافة خيار التقارير في القائمة الجانبية**
page = st.sidebar.radio(
    "📌 القائمة الرئيسية",
    [
        "📊 لوحة التحكم (Dashboard)",
        "🚢 الشحنات والحاويات",
        "📦 الطلبات",
        "📈 واجهة التقارير",
    ],
)

st.sidebar.markdown("---")
st.sidebar.info("النظام يعمل بكفاءة ✔️")


def style_container_col(val):
  return "background-color: #fee2e2; color: #dc2626; font-weight: bold;"


# 5. عرض الصفحة المختارة
if page == "📊 لوحة التحكم (Dashboard)":
  st.title("📊 لوحة التحكم الرئيسية")
  st.markdown("---")

  if "code" in df.columns:
    all_codes = ["الكل"] + sorted(
        df["code"].dropna().astype(str).unique().tolist()
    )
    selected_code = st.selectbox("🔍 تصفية برقم الكود:", all_codes)
    if selected_code != "الكل":
      filtered_df = filtered_df[
          filtered_df["code"].astype(str) == selected_code
      ]

  st.dataframe(filtered_df, use_container_width=True, height=600)

elif page == "🚢 الشحنات والحاويات":
  st.title("🚢 إدارة الشحنات والحاويات")
  st.markdown("---")
  st.dataframe(filtered_df, use_container_width=True, height=600)

elif page == "📦 الطلبات":
  st.title("📦 جميع الطلبات المسجلة")
  st.markdown("---")
  st.dataframe(filtered_df, use_container_width=True, height=600)

# 6. واجهة التقارير الجانبية المحدثة
elif page == "📈 واجهة التقارير":
  st.title("📈 واجهة التقارير الشاملة")
  st.markdown("---")

  # تقارير سريعة بواسطة كروت المؤشرات
  c1, c2, c3, c4 = st.columns(4)
  with c1:
    st.metric(
        "إجمالي الشحنات / الطلبات",
        f"{len(filtered_df)} طلب",
    )
  with c2:
    st.metric(
        "إجمالي عدد الكراتين",
        f"{int(filtered_df['عدد الكارتون'].sum() if 'عدد الكارتون' in filtered_df else 0)} كارتون",
    )
  with c3:
    st.metric(
        "إجمالي الحجم CBM",
        f"{filtered_df['حجم'].sum() if 'حجم' in filtered_df else 0:.3f}",
    )
  with c4:
    st.metric(
        "إجمالي الوزن",
        f"{filtered_df['الوزن'].sum() if 'الوزن' in filtered_df else 0:,.1f} KG",
    )

  st.markdown("---")
  st.subheader("📊 ملخص الحاويات والأكواد")

  # ملخص إحصائي مبسط حسب الحاوية
  if container_col and container_col in filtered_df.columns:
    summary_df = (
        filtered_df.groupby(container_col)
        .agg({
            "عدد الكارتون": "sum",
            "حجم": "sum",
            "الوزن": "sum",
            "code": "count",
        })
        .reset_index()
        .rename(columns={"code": "عدد الأكواد المسجلة"})
    )

    st.dataframe(summary_df, use_container_width=True, height=400)

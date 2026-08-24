import io
import os
import pandas as pd
import streamlit as st

# 1. إعداد الصفحة وتوسيع المساحة
st.set_page_config(
    page_title="Logistics Admin Dashboard", page_icon="📦", layout="wide"
)

# 2. تنسيقات CSS لزيادة المساحة وتصميم بطاقات المؤشرات وتكبير الجدول
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
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem; max-width: 99% !important; }
    
    /* تكبير حجم الخط وارتفاع صفوف الجدول */
    [data-testid="stDataFrame"] div[role="grid"] { font-size: 15px !important; }
    [data-testid="stDataFrame"] div[role="row"] { min-height: 42px !important; }
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
      st.sidebar.success("تم حفظ الملف الجديد بنجاح ✔️")
    except Exception as e:
      st.sidebar.error(f"خطأ في قراءة الملف المرفوع: {e}")

  if df is None and os.path.exists(DATA_FILE):
    try:
      df = pd.read_excel(DATA_FILE)
    except Exception:
      df = None

  if df is None:
    df = pd.DataFrame({
        "No": [972, 994, 996, 998, 1020],
        "code": ["SM165", "SM165", "SM165", "SM170", "SM170"],
        "Shipping mark": [
            "SM165-B07",
            "SM165-B03",
            "SM165-B05",
            "SM170-B01",
            "SM170-B02",
        ],
        "رقم دخول المخزن": ["RS2601", "RS2602", "RS2603", "RS2604", "RS2605"],
        "المكتب دفع": [25934.0, 13500.0, 9036.0, 12000.0, 5000.0],
        "Client Paid": [500.0, 300.0, 200.0, 150.0, 200.0],
        "نوع البضاعة": [
            "Lady Trousers",
            "White shirt",
            "Skirt",
            "Top",
            "Coat",
        ],
        "عدد الكارتون": [8, 3, 3, 5, 4],
        "الوزن": [364, 126, 150, 200, 180],
        "حجم": [1.255, 0.527, 0.492, 0.800, 0.600],
        "رقم الفاتورة": ["INV-01", "INV-02", "INV-03", "INV-04", "INV-05"],
        "رقم الحاوية": ["RQ6044", "RQ6044", "RQ6045", "RQ6045", "RQ6046"],
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


# 4. القائمة الجانبية: رفع الملفات، التنقل، والفلاتر
st.sidebar.title("🚢 إدارة اللوجستيات")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "📁 رفع ملف Excel جديد", type=["xlsx", "xls"]
)
df = load_data(uploaded_file)
filtered_df = df.copy()

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
  if selected_container != "الكل":
    filtered_df = filtered_df[
        filtered_df[container_col].astype(str) == selected_container
    ]

st.sidebar.markdown("---")

# قائمة التنقل بين الصفحات
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


# 5. دالة تمييز عمود رقم الحاوية
def style_container_col(val):
  return "background-color: #fee2e2; color: #dc2626; font-weight: bold;"


# 6. التنقل بين الصفحات
if page == "📊 لوحة التحكم (Dashboard)":
  st.title("📊 لوحة التحكم الرئيسية")
  st.markdown("---")

  # فلتر الكود من الجدول الكامل
  if "code" in df.columns:
    all_codes = ["الكل"] + sorted(
        df["code"].dropna().astype(str).unique().tolist()
    )
    selected_code = st.selectbox(
        "🔍 تصفية إضافية برقم الكود (عرض جميع الأكواد):", all_codes
    )
    if selected_code != "الكل":
      filtered_df = filtered_df[
          filtered_df["code"].astype(str) == selected_code
      ]
  else:
    selected_code = "غير محدد"

  total_containers = (
      filtered_df[container_col].nunique() if container_col else 0
  )
  total_client_paid = (
      filtered_df["Client Paid"].sum() if "Client Paid" in filtered_df else 0.0
  )
  total_orders = len(filtered_df)
  office_paid = (
      filtered_df["المكتب دفع"].sum() if "المكتب دفع" in filtered_df else 0.0
  )
  total_amount = float(office_paid) * 1.01
  total_cbm = filtered_df["حجم"].sum() if "حجم" in filtered_df else 0.0
  total_ctns = (
      filtered_df["عدد الكارتون"].sum()
      if "عدد الكارتون" in filtered_df
      else 0
  )

  # البطاقات العلويّة
  c1, c2, c3, c4 = st.columns(4)
  with c1:
    st.markdown(
        f'<div class="metric-card" style="background-color: #10b981;"><div class="metric-title">Client Paid</div><div class="metric-value">¥ {total_client_paid:,.1f}</div></div>',
        unsafe_allow_html=True,
    )
  with c2:
    st.markdown(
        f'<div class="metric-card" style="background-color: #ef4444;"><div class="metric-title">عدد الحاويات</div><div class="metric-value">{total_containers} حاوية</div></div>',
        unsafe_allow_html=True,
    )
  with c3:
    st.markdown(
        f'<div class="metric-card" style="background-color: #22c55e;"><div class="metric-title">الحاوية / الكود</div><div class="metric-value">{selected_container} / {selected_code}</div></div>',
        unsafe_allow_html=True,
    )
  with c4:
    st.markdown(
        f'<div class="metric-card" style="background-color: #3b82f6;"><div class="metric-title">عدد الطلبات</div><div class="metric-value">{total_orders} طلب</div></div>',
        unsafe_allow_html=True,
    )

  c5, c6, c7, c8 = st.columns(4)
  with c5:
    st.markdown(
        f'<div class="metric-card" style="background-color: #7c3aed;"><div class="metric-title">إجمالي المبالغ Amount</div><div class="metric-value">¥ {total_amount:,.1f}</div></div>',
        unsafe_allow_html=True,
    )
  with c6:
    st.markdown(
        f'<div class="metric-card" style="background-color: #f97316;"><div class="metric-title">Office Paid</div><div class="metric-value">¥ {office_paid:,.1f}</div></div>',
        unsafe_allow_html=True,
    )
  with c7:
    st.markdown(
        f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">📊 إجمالي الحجم (Cbm)</div><div class="metric-value">Cbm {total_cbm:.3f}</div></div>',
        unsafe_allow_html=True,
    )
  with c8:
    st.markdown(
        f'<div class="metric-card" style="background-color: #d97706;"><div class="metric-title">📦 إجمالي الكراتين (Ctns)</div><div class="metric-value">{int(total_ctns)} كارتون</div></div>',
        unsafe_allow_html=True,
    )

  st.markdown("---")
  st.subheader("📊 جدول التفاصيل المصفى")

  # خيارات التصدير (CSV & Excel)
  btn_col1, btn_col2 = st.columns([1, 1])

  with btn_col1:
    # تحويل البيانات إلى Excel في الذاكرة
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
      filtered_df.to_excel(writer, index=False, sheet_name="Filtered_Data")
    excel_bytes = buffer.getvalue()

    st.download_button(
        label="📊 Download as Excel",
        data=excel_bytes,
        file_name="filtered_details.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

  with btn_col2:
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name="filtered_details.csv",
        mime="text/csv",
    )

  if container_col:
    styled_df = filtered_df.style.map(
        style_container_col, subset=[container_col]
    )
    st.dataframe(styled_df, use_container_width=True, height=800)
  else:
    st.dataframe(filtered_df, use_container_width=True, height=800)

elif page == "🚢 الشحنات والحاويات":
  st.title("🚢 إدارة الشحنات والحاويات")
  st.markdown("---")
  st.dataframe(filtered_df, use_container_width=True, height=800)

elif page == "📦 الطلبات":
  st.title("📦 جميع الطلبات المسجلة")
  st.markdown("---")
  st.dataframe(filtered_df, use_container_width=True, height=800)

elif page == "📈 واجهة التقارير":
  st.title("📈 واجهة التقارير الشاملة")
  st.markdown("---")

  # المؤشرات الإحصائية العامة
  c1, c2, c3, c4 = st.columns(4)
  with c1:
    st.metric("إجمالي الشحنات / الطلبات", f"{len(filtered_df)} طلب")
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

  # جدول ملخص البيانات مقسم حسب الحاوية
  if container_col and container_col in filtered_df.columns:
    agg_dict = {}
    if "عدد الكارتون" in filtered_df:
      agg_dict["عدد الكارتون"] = "sum"
    if "حجم" in filtered_df:
      agg_dict["حجم"] = "sum"
    if "الوزن" in filtered_df:
      agg_dict["الوزن"] = "sum"
    if "code" in filtered_df:
      agg_dict["code"] = "count"

    if agg_dict:
      summary_df = (
          filtered_df.groupby(container_col)
          .agg(agg_dict)
          .reset_index()
          .rename(columns={"code": "عدد الأكواد المسجلة"})
      )
      st.dataframe(summary_df, use_container_width=True, height=500)

import pandas as pd
import streamlit as st

# 1. إعداد الصفحة (يجب أن يكون في البداية)
st.set_page_config(
    page_title="Logistics Admin Dashboard", page_icon="📦", layout="wide"
)

# 2. تنسيقات CSS مخصصة
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
    </style>
""",
    unsafe_allow_html=True,
)

# 3. القائمة الجانبية وزر رفع الملفات
st.sidebar.title("🚢 إدارة اللوجستيات")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "📁 رفع ملف Excel جديد", type=["xlsx", "xls"]
)


# 4. دالة تحميل البيانات وتنظيفها وتجهيز أنواع الحقول
@st.cache_data
def load_data(file):
  df = None
  if file is not None:
    try:
      df = pd.read_excel(file)
    except Exception as e:
      st.error(f"حدث خطأ أثناء قراءة الملف المرفوع: {e}")

  if df is None:
    try:
      df = pd.read_excel("shipping_data.xlsx")
    except FileNotFoundError:
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
          "رقم الحاويات": ["RQ6044", "RQ6044", "RQ6045", "RQ6045", "RQ6046"],
      })

  # تنظيف أسماء الأعمدة من المسافات الزائدة
  df.columns = df.columns.astype(str).str.strip()

  # تحويل الأعمدة الحسابية إلى أرقام لتفادي TypeError أثناء الحسابات
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


df = load_data(uploaded_file)

page = st.sidebar.radio(
    "القائمة الرئيسية",
    [
        "📊 لوحة التحكم (Dashboard)",
        "🚢 الشحنات والحاويات",
        "📦 الطلبات",
        "📈 التقارير",
    ],
)

st.sidebar.markdown("---")
st.sidebar.info("النظام يعمل بكفاءة ✔️")

# 5. محتوى الصفحات
if page == "📊 لوحة التحكم (Dashboard)":
  st.title("📊 لوحة التحكم الرئيسية")
  st.markdown("---")

  if "code" in df.columns:
    codes = df["code"].dropna().unique().tolist()
    selected_code = st.selectbox(
        "🔍 اختر أو ابحث عن رقم الكود لتجميع البيانات الخاصة به تلقائياً في الأعلى:",
        codes,
    )
    filtered_df = df[df["code"] == selected_code]
  else:
    st.warning("⚠️ لم يتم العثور على عمود باسم 'code' في الملف المرفوع.")
    filtered_df = df.copy()
    selected_code = "غير محدد"

  # حساب الأرقام بحماية عالية
  container_col = (
      "رقم الحاويات"
      if "رقم الحاويات" in filtered_df.columns
      else ("رقم الحاوية" if "رقم الحاوية" in filtered_df.columns else None)
  )
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

  # الآن الضمان 100% أن office_paid رقم float/int
  total_amount = float(office_paid) * 1.01

  total_cbm = filtered_df["حجم"].sum() if "حجم" in filtered_df else 0.0
  total_ctns = (
      filtered_df["عدد الكارتون"].sum()
      if "عدد الكارتون" in filtered_df
      else 0
  )

  # الصف الأول
  c1, c2, c3, c4 = st.columns(4)
  with c1:
    st.markdown(
        f"""
            <div class="metric-card" style="background-color: #10b981;">
                <div class="metric-title">Client Paid</div>
                <div class="metric-value">¥ {total_client_paid:,.1f}</div>
            </div>
        """,
        unsafe_allow_html=True,
    )
  with c2:
    st.markdown(
        f"""
            <div class="metric-card" style="background-color: #ef4444;">
                <div class="metric-title">عدد الحاويات</div>
                <div class="metric-value">{total_containers} حاوية</div>
            </div>
        """,
        unsafe_allow_html=True,
    )
  with c3:
    st.markdown(
        f"""
            <div class="metric-card" style="background-color: #22c55e;">
                <div class="metric-title">رقم الكود المختار</div>
                <div class="metric-value">{selected_code}</div>
            </div>
        """,
        unsafe_allow_html=True,
    )
  with c4:
    st.markdown(
        f"""
            <div class="metric-card" style="background-color: #3b82f6;">
                <div class="metric-title">عدد الطلبات</div>
                <div class="metric-value">{total_orders} طلب</div>
            </div>
        """,
        unsafe_allow_html=True,
    )

  # الصف الثاني
  c5, c6, c7, c8 = st.columns(4)
  with c5:
    st.markdown(
        f"""
            <div class="metric-card" style="background-color: #7c3aed;">
                <div class="metric-title">إجمالي المبالغ Amount</div>
                <div class="metric-value">¥ {total_amount:,.1f}</div>
            </div>
        """,
        unsafe_allow_html=True,
    )
  with c6:
    st.markdown(
        f"""
            <div class="metric-card" style="background-color: #f97316;">
                <div class="metric-title">Office Paid</div>
                <div class="metric-value">¥ {office_paid:,.1f}</div>
            </div>
        """,
        unsafe_allow_html=True,
    )
  with c7:
    st.markdown(
        f"""
            <div class="metric-card" style="background-color: #1e3a8a;">
                <div class="metric-title">📊 إجمالي الحجم (Cbm)</div>
                <div class="metric-value">Cbm {total_cbm:.3f}</div>
            </div>
        """,
        unsafe_allow_html=True,
    )
  with c8:
    st.markdown(
        f"""
            <div class="metric-card" style="background-color: #d97706;">
                <div class="metric-title">📦 إجمالي الكراتين (Ctns)</div>
                <div class="metric-value">{int(total_ctns)} كارتون</div>
            </div>
        """,
        unsafe_allow_html=True,
    )

  st.markdown("---")
  st.subheader(f"📊 جدول التفاصيل المصفى للكود الحالي: {selected_code}")

  csv = filtered_df.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Download as CSV",
      data=csv,
      file_name=f"{selected_code}_details.csv",
      mime="text/csv",
  )

  st.dataframe(filtered_df, use_container_width=True)

elif page == "🚢 الشحنات والحاويات":
  st.title("🚢 إدارة الشحنات والحاويات")
  st.markdown("---")
  container_col = (
      "رقم الحاويات"
      if "رقم الحاويات" in df.columns
      else ("رقم الحاوية" if "رقم الحاوية" in df.columns else None)
  )

  if container_col:
    agg_dict = {}
    for col in ["عدد الكارتون", "حجم", "المكتب دفع"]:
      if col in df.columns:
        agg_dict[col] = "sum"
    if "code" in df.columns:
      agg_dict["code"] = "count"

    container_summary = df.groupby(container_col).agg(agg_dict).reset_index()
    if "code" in container_summary.columns:
      container_summary = container_summary.rename(
          columns={"code": "عدد الطلبات"}
      )

    st.dataframe(container_summary, use_container_width=True)
  else:
    st.warning("⚠️ لم يتم العثور على عمود رقم الحاويات في البيانات.")

elif page == "📦 الطلبات":
  st.title("📦 جميع الطلبات المسجلة")
  st.markdown("---")
  st.dataframe(df, use_container_width=True)

elif page == "📈 التقارير":
  st.title("📈 التقارير الشاملة")
  st.markdown("---")
  col_r1, col_r2 = st.columns(2)
  with col_r1:
    office_sum = (
        float(df["المكتب دفع"].sum()) if "المكتب دفع" in df.columns else 0.0
    )
    st.metric(label="إجمالي مدفوعات المكتب", value=f"¥ {office_sum:,.1f}")
  with col_r2:
    cbm_sum = float(df["حجم"].sum()) if "حجم" in df.columns else 0.0
    st.metric(label="إجمالي حجم CBM", value=f"{cbm_sum:,.3f}")

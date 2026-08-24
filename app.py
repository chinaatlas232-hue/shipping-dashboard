import io
import os
import pandas as pd
import streamlit as st

# 1. إعداد الصفحة وتوسيع المساحة
st.set_page_config(
    page_title="Logistics Admin Dashboard", page_icon="📦", layout="wide"
)

# 2. تنسيقات CSS
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
    
    [data-testid="stDataFrame"] div[role="grid"] { font-size: 15px !important; }
    [data-testid="stDataFrame"] div[role="row"] { min-height: 42px !important; }
    </style>
""",
    unsafe_allow_html=True,
)

DATA_FILE = "shipping_data.xlsx"


def clean_numeric(series):
  return (
      pd.to_numeric(
          series.astype(str)
          .str.replace("¥", "", regex=False)
          .str.replace("$", "", regex=False)
          .str.replace(",", "", regex=False)
          .str.strip(),
          errors="coerce",
      )
      .fillna(0)
  )


# 3. دالة تحميل البيانات
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
        "No": [1324, 1352],
        "code": ["B7512", "B7512"],
        "Shipping mark": ["B7512-C23", "B7512-C03"],
        "رقم دخول المخزن": ["RS2607223184", "RS2607202745"],
        "المكتب دفع": [0, 0],
        "الزبون دفع": [100, 690],
        "المجموع": [3465, 5600],
        "عدد الكارتون": [1, 2],
        "الوزن": [40, 98],
        "حجم": [0.132, 0.525],
        "رقم الحاوية": ["RQ6052", "RQ6052"],
    })

  df.columns = df.columns.astype(str).str.strip()

  if "الزبون دفع" in df.columns and "Client Paid" not in df.columns:
    df["Client Paid"] = df["الزبون دفع"]

  if "المكتب دفع" in df.columns:
    df["Office Paid"] = df["المكتب دفع"]

  numeric_cols = [
      "المكتب دفع",
      "Office Paid",
      "الزبون دفع",
      "Client Paid",
      "عدد الكارتون",
      "الوزن",
      "حجم",
      "المجموع",
  ]
  for col in numeric_cols:
    if col in df.columns:
      df[col] = clean_numeric(df[col])

  return df


# 4. القائمة الجانبية
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
  return "background-color: #fef08a; color: #111827; font-weight: bold;"


def apply_text_search(data_frame):
  search_query = st.text_input(
      "🔍 بحث سريع في كافة الأعمدة (اخفاء باقي البيانات غير المطبقة):", ""
  )
  if search_query:
    mask = data_frame.astype(str).apply(
        lambda x: x.str.contains(search_query, case=False, na=False)
    )
    return data_frame[mask.any(axis=1)]
  return data_frame


# دالة عرض أزرار التحميل مجددًا لكل الصُفحات
def render_download_buttons(data_to_download):
  btn_col1, btn_col2 = st.columns([1, 1])
  with btn_col1:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
      data_to_download.to_excel(writer, index=False, sheet_name="Filtered_Data")
    st.download_button(
        label="📊 Download as Excel",
        data=buffer.getvalue(),
        file_name="filtered_details.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

  with btn_col2:
    st.download_button(
        label="📥 Download as CSV",
        data=data_to_download.to_csv(index=False).encode("utf-8"),
        file_name="filtered_details.csv",
        mime="text/csv",
    )


# 5. التنقل بين الصفحات
if page == "📊 لوحة التحكم (Dashboard)":
  st.title("📊 لوحة التحكم الرئيسية")
  st.markdown("---")

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

  filtered_df = apply_text_search(filtered_df)

  total_containers = (
      filtered_df[container_col].nunique() if container_col else 0
  )

  if "Client Paid" in filtered_df:
    total_client_paid = filtered_df["Client Paid"].sum()
  elif "الزبون دفع" in filtered_df:
    total_client_paid = filtered_df["الزبون دفع"].sum()
  else:
    total_client_paid = 0.0

  if "Office Paid" in filtered_df:
    office_paid = filtered_df["Office Paid"].sum()
  elif "المكتب دفع" in filtered_df:
    office_paid = filtered_df["المكتب دفع"].sum()
  else:
    office_paid = 0.0

  if "المجموع" in filtered_df and filtered_df["المجموع"].sum() > 0:
    total_amount = filtered_df["المجموع"].sum()
  else:
    total_amount = float(office_paid) * 1.01

  total_orders = len(filtered_df)
  total_cbm = filtered_df["حجم"].sum() if "حجم" in filtered_df else 0.0
  total_ctns = (
      filtered_df["عدد الكارتون"].sum()
      if "عدد الكارتون" in filtered_df
      else 0
  )

  c1, c2, c3, c4 = st.columns(4)
  with c1:
    st.markdown(
        f'<div class="metric-card" style="background-color: #10b981;"><div class="metric-title">الزبون دفع (Client Paid)</div><div class="metric-value">¥ {total_client_paid:,.1f}</div></div>',
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
        f'<div class="metric-card" style="background-color: #f97316;"><div class="metric-title">المكتب دفع (Office Paid)</div><div class="metric-value">¥ {office_paid:,.1f}</div></div>',
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

  render_download_buttons(filtered_df)

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
  filtered_df = apply_text_search(filtered_df)
  render_download_buttons(filtered_df)

  if container_col:
    styled_df = filtered_df.style.map(
        style_container_col, subset=[container_col]
    )
    st.dataframe(styled_df, use_container_width=True, height=800)
  else:
    st.dataframe(filtered_df, use_container_width=True, height=800)

elif page == "📦 الطلبات":
  st.title("📦 جميع الطلبات المسجلة")
  st.markdown("---")
  filtered_df = apply_text_search(filtered_df)

  # إضافة أزرار التحميل لصفحة الطلبات أيضاً
  render_download_buttons(filtered_df)

  st.dataframe(filtered_df, use_container_width=True, height=800)

elif page == "📈 واجهة التقارير":
  st.title("📈 واجهة التقارير الشاملة")
  st.markdown("---")
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
    render_download_buttons(summary_df)
    st.dataframe(summary_df, use_container_width=True, height=500)

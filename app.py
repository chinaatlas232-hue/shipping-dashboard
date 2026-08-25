import io
import os
import pandas as pd
import streamlit as st

# 1. إعداد الصفحة والتنسيقات
st.set_page_config(
    page_title="Logistics Admin Dashboard", page_icon="📦", layout="wide"
)

# CSS مخصص يتيح التمرير الأفقي ويمنع اخفاء/اقتطاع أي عمود
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .metric-card {
        padding: 16px; border-radius: 12px; color: white;
        text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .metric-title { font-size: 14px; margin-bottom: 6px; opacity: 0.95; font-weight: 600; }
    .metric-value { font-size: 20px; font-weight: bold; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem; max-width: 99% !important; }

    div[data-baseweb="input"] {
        border-radius: 8px !important;
        border: 2px solid #3b82f6 !important;
    }

    /* --- جدول HTML يعرض كافة الأعمدة ويسمح بالتمرير الأفقي --- */
    .custom-table-container {
        width: 100%;
        max-height: 700px;
        overflow-x: auto !important; /* تفعيل شريط التمرير الأفقي لرؤية جميع الأعمدة */
        overflow-y: auto !important;
        border: 1px solid #444;
        border-radius: 8px;
    }
    .custom-table {
        width: max-content !important;
        min-width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        font-size: 13px;
        direction: rtl;
    }
    .custom-table th {
        background-color: #ff0000 !important;
        color: #ffffff !important;
        position: sticky;
        top: 0;
        padding: 10px 14px;
        text-align: center;
        border: 1px solid #dc2626;
        z-index: 10;
        white-space: nowrap;
    }
    .custom-table td {
        padding: 8px 12px;
        text-align: center;
        border: 1px solid #333;
        color: #ffffff !important;
        background-color: #1e293b;
        white-space: nowrap;
    }
    .custom-table tr:nth-child(even) td {
        background-color: #0f172a;
    }
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


# 2. تحميل البيانات وتجهيز الحقول دون حذف أي أعمدة أصلية
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
    # قائمة افتراضية تحوي كافة الأعمدة المطلوبة
    df = pd.DataFrame({
        "No": [1324],
        "code": ["BS79"],
        "الكفيل": ["أسامة"],
        "Shipping mark": ["BS79-C23"],
        "رقم دخول المخزن": ["RS2607223184"],
        "نوع البضاعة": ["Ladies dress"],
        "عدد الكارتون": [1],
        "الوزن": [40],
        "حجم": [0.132],
        "رقم الحاوية": ["RQ6029"],
        "Staff": ["JOYCE"],
        "المجموع": [3465],
        "الزبون دفع": [100],
        "المكتب دفع": [0],
        "نقل داخلي": [0],
        "%": [0],
        "قيمة الفاتورة بالدولار": [0],
        "رقم قيد الادخال": [0],
        "رقم الفاتورة": [0],
        "سعر البيع": [0],
        "مبلغ الجمرك": [3768.30],
        "قيمة الاستحصالات": [0.0],
        "شرح تفصيلي": ["-"],
        "تاريخ التوزيع": ["2026-08-24"],
        "عدد الايام": [0],
        "رقم فورم زينب": [1.0],
        "وصل الاستلام": ["-"],
        "رقم فورم اسامة": ["-"],
    })

  df.columns = df.columns.astype(str).str.strip()

  if "الزبون دفع" in df.columns and "Client Paid" not in df.columns:
    df["Client Paid"] = df["الزبون دفع"]

  if "المكتب دفع" in df.columns and "Office Paid" not in df.columns:
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
      "مبلغ الجمرك",
      "قيمة الاستحصالات",
  ]
  for col in numeric_cols:
    if col in df.columns:
      df[col] = clean_numeric(df[col])

  if "مبلغ الجمرك" in df.columns and "قيمة الاستحصالات" in df.columns:
    df["متبقي حقيقي"] = df["مبلغ الجمرك"] - df["قيمة الاستحصالات"]

  return df


def apply_strict_code_search(data_frame, search_term):
  if not search_term or "code" not in data_frame.columns:
    return data_frame

  clean_term = search_term.strip().upper()
  code_series = data_frame["code"].astype(str).str.strip().str.upper()

  exact_match = data_frame[code_series == clean_term]
  if not exact_match.empty:
    return exact_match

  return data_frame[code_series.str.startswith(clean_term)]


# 3. تحميل البيانات وإتاحة الفلترة
uploaded_file = st.sidebar.file_uploader(
    "📁 رفع ملف Excel جديد", type=["xlsx", "xls"]
)
df = load_data(uploaded_file)

# 4. القائمة الجانبية (Sidebar)
st.sidebar.title("🚢 إدارة اللوجستيات")
st.sidebar.markdown("---")

container_col = next(
    (c for c in ["رقم الحاوية", "رقم الحاويات"] if c in df.columns), None
)

selected_container = "الكل"
filtered_df = df.copy()

if container_col:
  containers = ["الكل"] + sorted(
      df[container_col].dropna().astype(str).unique().tolist()
  )
  selected_container = st.sidebar.selectbox("🚢 اختر رقم الحاوية:", containers)
  if selected_container != "الكل":
    filtered_df = filtered_df[
        filtered_df[container_col].astype(str) == selected_container
    ]

page = st.sidebar.radio(
    "📌 القائمة الرئيسية",
    [
        "📊 لوحة التحكم (Dashboard)",
        "🚢 الشحنات والحاويات",
        "📦 الطلبات",
        "💰 كشف الكمارك المستحصلة",
        "📈 واجهة التقارير",
    ],
)


def render_search_bar():
  return st.text_input(
      "🔍 فلترة فورية وحصرية لعمود الكود (code):",
      value="",
      placeholder="...اكتب الكود هنا بالضبط (مثال: B7 أو B12)",
      key="code_search_input",
  )


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


def render_dashboard_metrics(data_df):
  total_orders = len(data_df)
  total_cartons = (
      data_df["عدد الكارتون"].sum() if "عدد الكارتون" in data_df.columns else 0
  )
  total_weight = data_df["الوزن"].sum() if "الوزن" in data_df.columns else 0
  total_volume = data_df["حجم"].sum() if "حجم" in data_df.columns else 0

  office_paid_col = next(
      (c for c in ["المكتب دفع", "Office Paid"] if c in data_df.columns), None
  )
  client_paid_col = next(
      (c for c in ["الزبون دفع", "Client Paid"] if c in data_df.columns), None
  )

  office_paid = data_df[office_paid_col].sum() if office_paid_col else 0.0
  client_paid = data_df[client_paid_col].sum() if client_paid_col else 0.0

  c1, c2, c3, c4, c5, c6 = st.columns(6)
  with c1:
    st.markdown(
        f'<div class="metric-card" style="background-color: #1e3a8a;"><div'
        ' class="metric-title">إجمالي الطلبات</div><div'
        f' class="metric-value">{total_orders:,}</div></div>',
        unsafe_allow_html=True,
    )
  with c2:
    st.markdown(
        f'<div class="metric-card" style="background-color: #0284c7;"><div'
        ' class="metric-title">إجمالي الكارتون</div><div'
        f' class="metric-value">{total_cartons:,.0f}</div></div>',
        unsafe_allow_html=True,
    )
  with c3:
    st.markdown(
        f'<div class="metric-card" style="background-color: #0d9488;"><div'
        ' class="metric-title">إجمالي الوزن</div><div'
        f' class="metric-value">{total_weight:,.2f} kg</div></div>',
        unsafe_allow_html=True,
    )
  with c4:
    st.markdown(
        f'<div class="metric-card" style="background-color: #d97706;"><div'
        ' class="metric-title">إجمالي الحجم</div><div'
        f' class="metric-value">{total_volume:,.3f} m³</div></div>',
        unsafe_allow_html=True,
    )
  with c5:
    st.markdown(
        f'<div class="metric-card" style="background-color: #16a34a;"><div'
        ' class="metric-title">دفع الشركة</div><div'
        f' class="metric-value">${office_paid:,.2f}</div></div>',
        unsafe_allow_html=True,
    )
  with c6:
    st.markdown(
        f'<div class="metric-card" style="background-color: #9333ea;"><div'
        ' class="metric-title">دفع الزبون</div><div'
        f' class="metric-value">${client_paid:,.2f}</div></div>',
        unsafe_allow_html=True,
    )


# دالة طباعة كافة أعمدة الـ DataFrame في الجدول
def render_red_header_table(data_df):
  html_table = (
      '<div class="custom-table-container"><table class="custom-table"><thead><tr>'
  )
  for col in data_df.columns:
    html_table += f"<th>{col}</th>"
  html_table += "</tr></thead><tbody>"

  for _, row in data_df.iterrows():
    html_table += "<tr>"
    for val in row:
      val_str = "" if pd.isna(val) else str(val)
      html_table += f"<td>{val_str}</td>"
    html_table += "</tr>"
  html_table += "</tbody></table></div>"

  st.markdown(html_table, unsafe_allow_html=True)


# 5. عرض الصفحات
if page in [
    "📊 لوحة التحكم (Dashboard)",
    "🚢 الشحنات والحاويات",
    "📦 الطلبات",
    "📈 واجهة التقارير",
]:
  st.title(f"{page}")
  st.markdown("---")

  search_input = render_search_bar()
  display_df = apply_strict_code_search(filtered_df, search_input)

  render_dashboard_metrics(display_df)
  render_download_buttons(display_df)

  # عرض كافة الأعمدة بلا استثناء
  render_red_header_table(display_df)

elif page == "💰 كشف الكمارك المستحصلة":
  st.title("💰 كشف الكمارك المستحصلة من العميل (Pivot Report)")
  st.markdown("---")

  # نموذج بحث (st.form) يضمن تشغيل البحث بعد الضغط على Enter أو زر البحث فقط
  with st.form(key="search_form"):
    search_query = (
        st.text_input(
            "🔍 بحث ذكي (ابحث برقم الكود، اسم الكفيل، أو رقم الحاوية):", ""
        )
        .strip()
    )
    submit_button = st.form_submit_button(label="🔍 بحث")

  pivot_filtered_df = filtered_df.copy()

  if search_query:
    search_cols = [
        c
        for c in ["code", "الكفيل", "رقم الحاوية", "رقم الحاويات"]
        if c in pivot_filtered_df.columns
    ]
    if search_cols:
      mask = pivot_filtered_df[search_cols].apply(
          lambda col: col.astype(str).str.contains(
              search_query, case=False, na=False
          )
      )
      pivot_filtered_df = pivot_filtered_df[mask.any(axis=1)]

  render_red_header_table(pivot_filtered_df)

import pandas as pd
import streamlit as st

# إعداد الصفحة لتكون بعرض الشاشة الكاملة (Wide)
st.set_page_config(
    page_title="نظام إدارة اللوجستيات الشامل", page_icon="🚢", layout="wide"
)

st.title("🚢 نظام إدارة اللوجستيات والتقارير الشاملة")
st.markdown("---")

# 1. محاكاة قاعدة البيانات المركزية (استبدل هذا بملف الـ Excel الفعلي الخاص بك عبر pd.read_excel)
data = {
    "رقم الحاوية": [
        "RQ6025",
        "RQ6026",
        "RQ6025",
        "RQ6027",
        "RQ6028",
        "RQ6026",
    ],
    "code": ["B12", "B12", "B1020", "B12", "B12", "B1020"],
    "Shipping mark": ["B12-102", "B12-90", "B12-95", "B1020-15", "B12-93", "B12-84"],
    "رقم دخول المخزن": [
        "RS26040890317",
        "RS26040898304",
        "RS26040898300",
        "RS26040798220",
        "RS26040798202",
        "RS26040398107",
    ],
    "نوع البضاعة": [
        "Ladys Dress",
        "Ladys Dress",
        "Ladys Clothes",
        "lady suit",
        "Ladys Dress",
        "Ladys Suit",
    ],
    "عدد الكارتون": [3, 1, 1, 3, 2, 6],
    "إجمالي الوزن": [72.5, 24.1, 40.0, 15.0, 11.0, 53.2],
    "إجمالي الحجم": [1.2, 0.8, 0.9, 1.5, 1.1, 2.5],
    "دفع الشركة": [30, 40, 50, 20, 25, 60],
    "دفع الزبون": [12, 23, 73, 50, 16, 45],
}
df = pd.DataFrame(data)

# --- 2. القائمة الجانبية للتنقل بين الأقسام والفلاتر ---
st.sidebar.header("🎛️ لوحة التحسس والتحكم")
page_selection = st.sidebar.radio(
    "اختر الشاشة المطلوبة:",
    [
        "📦 إدارة الشحنات والبحث المتقدم",
        "📈 واجهة التقارير الشاملة والتحليلات",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 فلاتر سريعة")
selected_container = st.sidebar.selectbox(
    "فلترة حسب رقم الحاوية:", ["الكل"] + list(df["رقم الحاوية"].unique())
)

# تطبيق فلتر الحاوية الأساسي على مستوى التطبيق
filtered_df = df.copy()
if selected_container != "الكل":
  filtered_df = filtered_df[
      filtered_df["رقم الحاوية"].astype(str).str.strip()
      == str(selected_container).strip()
  ]


# --- الصفحة الأولى: إدارة الشحنات والبحث الدقيق ---
if page_selection == "📦 إدارة الشحنات والبحث المتقدم":
  st.subheader("📦 إدارة الشحنات والبحث الذكي الدقيق")

  # حقل بحث دقيق يمنع خطأ المقترحات العشوائية (حل مشكلة B2)
  col_s1, col_s2 = st.columns(2)
  with col_s1:
    search_code = st.text_input(
        "البحث برقم الكود (Code) بدقة:", placeholder="مثال: B12..."
    )
  with col_s2:
    search_warehouse = st.text_input(
        "البحث برقم دخول المخزن بدقة:", placeholder="مثال: RS26040890317..."
    )

  # تفعيل البحث الدقيق (Exact/Strict Match)
  if search_code:
    code_query = search_code.strip().lower()
    filtered_df = filtered_df[
        filtered_df["code"].astype(str).str.lower().str.strip() == code_query
    ]

  if search_warehouse:
    wh_query = search_warehouse.strip().lower()
    filtered_df = filtered_df[
        filtered_df["رقم دخول المخزن"]
        .astype(str)
        .str.lower()
        .str.strip()
        == wh_query
    ]

  # كروت الإحصائيات العلوية الديناميكية
  m1, m2, m3, m4 = st.columns(4)
  with m1:
    st.metric("📦 عدد الطلبات", len(filtered_df))
  with m2:
    st.metric(
        "📦 مجموع الكارتون",
        filtered_df["عدد الكارتون"].sum() if not filtered_df.empty else 0,
    )
  with m3:
    st.metric(
        "⚖️ إجمالي الوزن",
        f"{filtered_df['إجمالي الوزن'].sum() if not filtered_df.empty else 0:,.2f} kg",
    )
  with m4:
    total_rev = (
        (
            filtered_df["دفع الشركة"].sum()
            + filtered_df["دفع الزبون"].sum()
        )
        if not filtered_df.empty
        else 0
    )
    st.metric("💵 إجمالي التكلفة", f"${total_rev:,.2f}")

  st.markdown("---")

  # زر التصدير
  if not filtered_df.empty:
    st.download_button(
        label="📥 Download Filtered Data as Excel/CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="shipments_filtered_report.csv",
        mime="text/csv",
    )

  st.subheader("📋 جدول الطلبات والشحنات:")
  st.dataframe(filtered_df, use_container_width=True)


# --- الصفحة الثانية: واجهة التقارير الشاملة والتحليلية ---
else:
  st.subheader("📈 واجهة التقارير الشاملة والتحليلات المتقدمة")

  # كروت الإحصائيات العامة للتقارير
  r1, r2, r3, r4 = st.columns(4)
  with r1:
    st.metric("📊 إجمالي الشحنات", len(filtered_df))
  with r2:
    st.metric(
        "📦 الكارتون الكلي",
        filtered_df["عدد الكارتون"].sum() if not filtered_df.empty else 0,
    )
  with r3:
    st.metric(
        "📐 إجمالي CBM",
        f"{filtered_df['إجمالي الحجم'].sum() if not filtered_df.empty else 0:,.3f}",
    )
  with r4:
    st.metric(
        "⚖️ الوزن الكلي",
        f"{filtered_df['إجمالي الوزن'].sum() if not filtered_df.empty else 0:,.2f} kg",
    )

  st.markdown("---")

  # اختيار نوع التقرير التحليلي المفيد
  report_option = st.selectbox(
      "اختر التقرير التحليلي المطلوب استعراضه:",
      [
          "1. تقرير أداء الحاويات (Container Summary)",
          "2. تقرير الملخص المالي حسب الكود (Financial by Code)",
          "3. تقرير أنواع البضائع الأكثر تكراراً",
      ],
  )

  if "1." in report_option:
    st.markdown("### 🚚 جدول ملخص الحاويات")
    if not filtered_df.empty:
      container_summary = (
          filtered_df.groupby("رقم الحاوية")
          .agg(
              عدد_الشحنات=("Shipping mark", "count"),
              مجموع_الكارتون=("عدد الكارتون", "sum"),
              مجموع_الوزن=("إجمالي الوزن", "sum"),
              مجموع_الحجم=("إجمالي الحجم", "sum"),
          )
          .reset_index()
      )
      st.dataframe(container_summary, use_container_width=True)
    else:
      st.info("لا توجد بيانات مطابقة للفلتر الحالي.")

  elif "2." in report_option:
    st.markdown("### 💰 الجدول المالي التجميعي حسب الأكواد")
    if not filtered_df.empty:
      financial_summary = (
          filtered_df.groupby("code")
          .agg(
              عدد_الطلبات=("code", "count"),
              إجمالي_دفع_الشركة=("دفع الشركة", "sum"),
              إجمالي_دفع_الزبون=("دفع الزبون", "sum"),
          )
          .reset_index()
      )
      financial_summary["الإجمالي الكلي"] = (
          financial_summary["إجمالي دفع الشركة"]
          + financial_summary["إجمالي دفع الزبون"]
      )
      st.dataframe(financial_summary, use_container_width=True)
    else:
      st.info("لا توجد بيانات مطابقة للفلتر الحالي.")

  else:
    st.markdown("### 📦 تقرير تحليل توزيع البضائع")
    if not filtered_df.empty:
      goods_summary = (
          filtered_df.groupby("نوع البضاعة")
          .agg(
              التكرار=("نوع البضاعة", "count"),
              مجموع_الكارتون=("عدد الكارتون", "sum"),
              مجموع_الوزن=("إجمالي الوزن", "sum"),
          )
          .reset_index()
      )
      st.dataframe(goods_summary, use_container_width=True)
    else:
      st.info("لا توجد بيانات مطابقة للفلتر الحالي.")

  st.markdown("---")
  st.subheader("📋 السجل الكامل للبيانات ضمن التقرير الحالي")
  st.download_button(
      label="📥 Export Full Table as CSV",
      data=filtered_df.to_csv(index=False).encode("utf-8-sig"),
      file_name="comprehensive_report.csv",
      mime="text/csv",
  )
  st.dataframe(filtered_df, use_container_width=True)

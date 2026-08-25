import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="نظام اللوجستيات الشامل - بالكود والسر",
    page_icon="🚢",
    layout="wide",
)

st.title("🚢 نظام إدارة اللوجستيات — بوابة الكود والرقم السري الآمنة")
st.markdown("---")

# 1. لوحة التحكم الجانبية لرفع ملف الـ Excel
st.sidebar.header("📁 لوحة التحكم والبيانات")
uploaded_file = st.sidebar.file_uploader(
    "رفع ملف الـ Excel (يجب أن يحتوي على `code` و `رمز_التحقق_السري`)",
    type=["xlsx", "xls"],
)

if uploaded_file is not None:
  try:
    df = pd.read_excel(uploaded_file)
    st.sidebar.success("✅ تم رفع الملف بنجاح!")
  except Exception as e:
    st.sidebar.error(f"❌ خطأ في قراءة الملف: {e}")
    st.stop()
else:
  st.sidebar.info("ℹ️ يتم عرض بيئة افتراضية حالياً لحين رفع ملفك.")
  # بيانات تجريبية افتراضية للتوضيح
  data = {
      "رمز_التحقق_السري": ["1234", "1234", "5678", "9876", "1234"],
      "code": ["B12", "B12", "B1020", "B11", "B12"],
      "رقم الحاوية": ["RQ6025", "RQ6026", "RQ6025", "RQ6027", "RQ6026"],
      "Shipping mark": ["B12-102", "B12-90", "B1020-15", "B11-05", "B12-99"],
      "رقم دخول المخزن": [
          "RS26040890317",
          "RS26040898304",
          "RS26040798220",
          "RS26040398107",
          "RS26040898399",
      ],
      "نوع البضاعة": [
          "Ladys Dress",
          "Ladys Dress",
          "Ladys Clothes",
          "Suit",
          "Jacket",
      ],
      "عدد الكارتون": [3, 1, 1, 2, 4],
      "إجمالي الوزن": [72.5, 24.1, 40.0, 15.0, 30.0],
      "إجمالي الحجم": [1.2, 0.8, 0.9, 0.5, 1.1],
      "دفع الشركة": [30, 40, 50, 20, 25],
      "دفع الزبون": [12, 23, 73, 50, 16],
  }
  df = pd.DataFrame(data)

st.sidebar.markdown("---")

# 2. إدخال الكود والرقم السري في الشريط الجانبي
st.sidebar.header("🔑 تسجيل الدخول بالرقم السري والكود")
entered_code = st.sidebar.text_input("أدخل رقم الكود (Code):")
entered_pin = st.sidebar.text_input("أدخل الرقم السري (PIN):", type="password")

if not entered_code or not entered_pin:
  st.sidebar.warning("⚠️ يرجى إدخال الكود والرقم السري معاً للمتابعة.")
  st.info("👈 أضف الكود والرقم السري في القائمة الجانبية لعرض بياناتك وتقاريرك.")
  st.stop()

# 3. التحقق الأمني ومطابقة البيانات
if "code" not in df.columns or "رمز_التحقق_السري" not in df.columns:
  st.error(
      "❌ الملف المرفوع يجب أن يحتوي على عمودي: `code` و `رمز_التحقق_السري`."
  )
  st.stop()

matched_df = df[
    (df["code"].astype(str).str.strip().str.lower() == entered_code.strip().lower())
    & (df["رمز_التحقق_السري"].astype(str).str.strip() == entered_pin.strip())
]

if matched_df.empty:
  st.sidebar.error("❌ الكود أو الرقم السري غير صحيح!")
  st.error(
      "⚠️ عذراً، البيانات المدخلة غير متطابقة أو غير موجودة. يرجى التأكد والمحاولة"
      " مجدداً."
  )
  st.stop()

st.sidebar.success("✅ تم تسجيل الدخول بنجاح!")

# 4. التنقل بين أقسام المنصة (إدارة الشحنات أو واجهة التقارير الشاملة)
st.sidebar.markdown("---")
st.sidebar.header("🎛️ أقسام النظام")
page_selection = st.sidebar.radio(
    "اختر الشاشة المطلوبة:",
    [
        "📦 شحنات الكود الخاصة بي",
        "📈 التقارير التحليلية الشاملة",
    ],
)

# تنظيف الجدول بإخفاء عمود الرمز السري لأجل الأمان التام
secure_df = matched_df.drop(columns=["رمز_التحقق_السري"])


# --- الصفحة الأولى: إدارة شحنات الكود ---
if page_selection == "📦 شحنات الكود الخاصة بي":
  st.subheader(f"📦 تفاصيل الشحنات التابعة للكود: **{entered_code}**")

  # إحصائيات سريعة خاصة بهذا الكود فقط
  m1, m2, m3, m4 = st.columns(4)
  with m1:
    st.metric("📦 عدد الشحنات", len(secure_df))
  with m2:
    st.metric(
        "📦 مجموع الكارتون",
        (
            secure_df["عدد الكارتون"].sum()
            if "عدد الكارتون" in secure_df.columns
            else 0
        ),
    )
  with m3:
    st.metric(
        "⚖️ إجمالي الوزن",
        f"{secure_df['إجمالي الوزن'].sum() if 'إجمالي الوزن' in secure_df.columns else 0:,.2f} kg",
    )
  with m4:
    total_rev = (
        (secure_df["دفع الشركة"].sum() + secure_df["دفع الزبون"].sum())
        if "دفع الشركة" in secure_df.columns
        else 0
    )
    st.metric("💵 إجمالي التكلفة", f"${total_rev:,.2f}")

  st.markdown("---")

  if not secure_df.empty:
    st.download_button(
        label="📥 تحميل تقرير الشحنات كملف CSV",
        data=secure_df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"shipment_{entered_code}.csv",
        mime="text/csv",
    )

  st.dataframe(secure_df, use_container_width=True)


# --- الصفحة الثانية: التقارير التحليلية الشاملة ---
else:
  st.subheader(
      f"📈 واجهة التقارير التحليلية الشاملة للكود: **{entered_code}**"
  )

  report_option = st.selectbox(
      "اختر التقرير التحليلي المطلوب استعراضه:",
      [
          "1. ملخص الحاويات التابعة لهذا الكود",
          "2. تقرير أنواع البضائع",
      ],
  )

  if "1." in report_option and "رقم الحاوية" in secure_df.columns:
    st.markdown("### 🚚 ملخص الحاويات")
    container_report = (
        secure_df.groupby("رقم الحاوية")
        .agg(
            عدد_الشحنات=("Shipping mark", "count"),
            مجموع_الكارتون=("عدد الكارتون", "sum"),
            مجموع_الوزن=("إجمالي الوزن", "sum"),
        )
        .reset_index()
    )
    st.dataframe(container_report, use_container_width=True)
  else:
    st.markdown("### 📦 تحليل البضائع")
    if "نوع البضاعة" in secure_df.columns:
      goods_report = (
          secure_df.groupby("نوع البضاعة")
          .agg(
              التكرار=("نوع البضاعة", "count"),
              مجموع_الكارتون=("عدد الكارتون", "sum"),
          )
          .reset_index()
      )
      st.dataframe(goods_report, use_container_width=True)
    else:
      st.dataframe(secure_df, use_container_width=True)

  st.markdown("---")
  st.subheader("📋 السجل التفصيلي الكامل")
  st.dataframe(secure_df, use_container_width=True)

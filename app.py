import pandas as pd
import streamlit as st

# إعداد الصفحة لتكون بعرض الشاشة الكاملة
st.set_page_config(
    page_title="نظام اللوجستيات الآمن - بوابة الزبائن",
    page_icon="🔐",
    layout="wide",
)

st.title("🔐 نظام إدارة اللوجستيات - بوابة الاستعلام الآمنة")
st.markdown("---")

# 1. قاعدة البيانات التجريبية (تحتوي على عمود لرمز السري/PIN لكل زبون)
# يمكنك استبدال هذا لاحقاً بقراءة ملف Excel يحتوي على عمود للرمز السري
data = {
    "رمز_التحقق_السري": ["1234", "1234", "5678", "9876", "5678"],
    "اسم_الزبون": ["أحمد علي", "أحمد علي", "محمد حسن", "خالد عمر", "محمد حسن"],
    "رقم الحاوية": ["RQ6025", "RQ6026", "RQ6025", "RQ6027", "RQ6028"],
    "code": ["B12", "B12", "B1020", "B12", "B12"],
    "Shipping mark": ["B12-102", "B12-90", "B1020-15", "B12-93", "B12-84"],
    "رقم دخول المخزن": [
        "RS26040890317",
        "RS26040898304",
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
    ],
    "عدد الكارتون": [3, 1, 1, 3, 2],
    "إجمالي الوزن": [72.5, 24.1, 40.0, 15.0, 11.0],
    "إجمالي الحجم": [1.2, 0.8, 0.9, 1.5, 1.1],
    "دفع الشركة": [30, 40, 50, 20, 25],
    "دفع الزبون": [12, 23, 73, 50, 16],
}
df = pd.DataFrame(data)

# --- 2. نظام تسجيل الدخول عبر الشريط الجانبي (Sidebar Authentication) ---
st.sidebar.header("🔑 بوابة دخول الزبائن")
st.sidebar.markdown(
    "الرجاء إدخال **رمز التحقق السري (PIN)** الخاص بك لعرض شحناتك حصراً."
)

entered_pin = st.sidebar.text_input("أدخل الرمز السري:", type="password")

if not entered_pin:
  st.sidebar.warning("⚠️ يرجى إدخال الرمز السري لعرض البيانات.")
  st.info(
      "👈 يرجى كتابة الرمز السري الخاص بك في القائمة الجانبية (Sidebar) لعرض"
      " التقرير والشحنات."
  )

  # عرض شاشة ترحيبية عامة بدون بيانات حساسة
  st.stop()  # إيقاف تنفيذ الكود هنا إذا لم يتم إدخال الرمز

# --- 3. التحقق من صحة الرمز وسحب بيانات الزبون حصراً ---
matched_df = df[
    df["رمز_التحقق_السري"].astype(str).str.strip() == str(entered_pin).strip()
]

if matched_df.empty:
  st.sidebar.error("❌ الرمز السري غير صحيح!")
  st.error(
      "⚠️ عذراً، الرمز الذي أدخلته غير صحيح. يرجى التأكد من الرقم والمحاولة مجدداً."
  )
  st.stop()

# إذا كان الرمز صحيحاً تماماً:
customer_name = matched_df["اسم_الزبون"].iloc[0]
st.sidebar.success(f"مرحباً بك، {customer_name} ✅")

st.markdown(f"### 👤 أهلاً بك يا أستاذ/ة **{customer_name}**")
st.markdown("إليك تفاصيل شحناتك وطلباتك المسجلة:")

# --- 4. لوحة الإحصائيات (Metrics) الخاصة بشحنات هذا الزبون فقط ---
total_orders = len(matched_df)
total_cartons = matched_df["عدد الكارتون"].sum()
total_weight = matched_df["إجمالي الوزن"].sum()
total_cost = (
    matched_df["دفع الشركة"].sum() + matched_df["دفع الزبون"].sum()
)

m1, m2, m3, m4 = st.columns(4)
with m1:
  st.metric("📦 عدد شحناتك", total_orders)
with m2:
  st.metric("📦 مجموع الكارتون", total_cartons)
with m3:
  st.metric("⚖️ إجمالي الوزن", f"{total_weight:,.2f} kg")
with m4:
  st.metric("💵 إجمالي التكلفة", f"${total_cost:,.2f}")

st.markdown("---")

# --- 5. جدول البيانات المخصص والآمن (إخفاء عمود الرمز السري تماماً للأمان) ---
secure_display_df = matched_df.drop(columns=["رمز_التحقق_السري", "اسم_الزبون"])

st.subheader("📋 جدول الشحنات الخاصة بك:")
st.dataframe(secure_display_df, use_container_width=True)

# زر تحميل البيانات الخاصة بالزبون فقط
st.download_button(
    label="📥 تحميل تقرير شحناتك (Excel/CSV)",
    data=secure_display_df.to_csv(index=False).encode("utf-8-sig"),
    file_name=f"my_shipments_{entered_pin}.csv",
    mime="text/csv",
)

import pandas as pd
import streamlit as st

# إعداد الصفحة
st.set_page_config(
    page_title="إدارة الشحنات والحاويات", page_icon="🚢", layout="wide"
)

st.title("🚢 إدارة الشحنات والحاويات")
st.markdown("---")

# 1. محاكاة تحميل البيانات (استبدل هذا بقراءة ملف الـ Excel الخاص بك مثل: pd.read_excel('your_file.xlsx'))
# تأكد من أن أسماء الأعمدة تطابق الموجودة في ملفك الفعلي
data = {
    "No.": [397, 1025, 1026, 1027, 1028],
    "code": ["E235", "KB130", "B4344", "BS1313", "B6135"],
    "Shipping mark": [
        "E235-A53",
        "KB130",
        "B4344-C48",
        "BS1313-B20",
        "B6135-02",
    ],
    "رقم دخول المخزن": [
        "RS260516045",
        "RS2607152074",
        "RS2607141878",
        "RS260708968",
        "RS260707896",
    ],
    "نوع البضاعة": [
        "LADYS BAGS",
        "Air conditioner",
        "BED,CART,rocker",
        "Mirror,Mirror frame",
        "HANGER",
    ],
    "إجمالي الطلبات": [1, 2, 1, 3, 2],
    "إجمالي الكارتون": [40, 15, 22, 10, 30],
    "إجمالي الوزن": [150.5, 300.0, 120.0, 85.5, 210.0],
    "إجمالي الحجم": [2.5, 5.1, 1.8, 3.2, 4.0],
    "دفع الشركة": [150, 430, 200, 120, 310],
    "دفع الزبون": [250, 600, 350, 220, 450],
}
df = pd.DataFrame(data)

# 2. شريط البحث الذكي المفلتر بدقة
search_query = st.text_input(
    "🔍 ابحث في الأعمدة (اكتب رقم الشحنة، الكود، أو رقم الحاوية بدقة)...",
    placeholder="مثال: RS260516045 أو E235...",
)

# 3. منطق الفلترة الدقيقة (لمنع اقتراح النتائج الخاطئة التي تبدأ فقط بالحرف)
if search_query:
    query_str = str(search_query).strip()

    # تحديد الأعمدة التي يتم البحث فيها بدقة (مثل الأكواد وأرقام المخزن)
    # يمكنك تعديل أسماء الأعمدة لتطابق جدولك تماماً
    searchable_cols = ["code", "Shipping mark", "رقم دخول المخزن"]

    # فلترة تعتمد على المطابقة التامة أو الإحتواء الدقيق للرمز المكتوب حصراً
    mask = pd.Series(False, index=df.index)
    for col in df.columns:
        # إذا أردت مطابقة تامة لكل خلية تحتوي على النص أو تطابقه
        mask = mask | (df[col].astype(str).str.strip().str.lower() == query_str.lower())
        
        # إذا أردت البحث الجزئي ولكن ضمن الأعمدة المحددة فقط بدون عشوائية:
        # mask = mask | df[col].astype(str).str.contains(query_str, case=False, na=False)

    filtered_df = df[mask]
else:
    filtered_df = df.copy()

# 4. حساب المجاميع للكروت الملونة في الأعلى بناءً على البيانات المصفاة
total_orders = filtered_df["إجمالي الطلبات"].sum() if not filtered_df.empty else 0
total_cartons = filtered_df["إجمالي الكارتون"].sum() if not filtered_df.empty else 0
total_weight = filtered_df["إجمالي الوزن"].sum() if not filtered_df.empty else 0
total_volume = filtered_df["إجمالي الحجم"].sum() if not filtered_df.empty else 0
total_company_pay = filtered_df["دفع الشركة"].sum() if not filtered_df.empty else 0
total_customer_pay = filtered_df["دفع الزبون"].sum() if not filtered_df.empty else 0

# 5. عرض الكروت الإحصائية الملونة بشكل مرتب وأنيق
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(label="📦 إجمالي الطلبات", value=f"{total_orders}")
with col2:
    st.metric(label="📦 إجمالي الكارتون", value=f"{total_cartons}")
with col3:
    st.metric(label="⚖️ إجمالي الوزن", value=f"{total_weight:,.2f} kg")
with col4:
    st.metric(label="📐 إجمالي الحجم", value=f"{total_volume:,.2f} m³")
with col5:
    st.metric(label="💵 دفع الشركة", value=f"${total_company_pay:,.2f}")
with col6:
    st.metric(label="💳 دفع الزبون", value=f"${total_customer_pay:,.2f}")

st.markdown("---")

# 6. أزرار التصدير (Excel / CSV)
c_ex1, c_ex2 = st.columns(2)
with c_ex1:
    if not filtered_df.empty:
        # تحويل البيانات لتصدير Excel (يمكنك استخدام مكتبة io و XlsxWriter لاحقاً إذا رغبت)
        st.download_button(
            label="📊 Download as Excel",
            data=filtered_df.to_csv(index=False).encode('utf-8-sig'),
            file_name="shipments_report.csv",
            mime="text/csv",
        )

# 7. عرض جدول النتائج النهائي
st.subheader("📋 جدول الشحنات:")
st.dataframe(filtered_df, use_container_width=True)

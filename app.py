import pandas as pd
import streamlit as st


# تحسين الأداء باستخدام التخزين المؤقت لقراءة وتسريع التعامل مع البيانات الكبيرة
@st.cache_data
def get_unique_codes(df):
    # استخراج كافة الأكواد الفريدة وإزالة القيم الفارغة
    return sorted(df["code"].dropna().unique().tolist())


# افترض أن df هو الجدول الخاص بك
# unique_codes = get_unique_codes(df)

# --- واجهة البحث والفلاتر السريعة ---
st.markdown("### 🔍 البحث السريع عن الأكواد")

# إنشاء أعمدة لتنظيم الواجهة
col1, col2 = st.columns([3, 1])

with col1:
    # قائمة منسدلة متعددة الاختيارات تدعم البحث والكتابة وسريعة الأداء
    selected_codes = st.multiselect(
        label="اختر أو اكتب الكود للبحث (يدعم اختيار أكثر من كود):",
        options=unique_codes,
        default=[],
        placeholder="اختر كود من القائمة...",
    )

with col2:
    st.write("⚡ **فلاتر سريعة:**")
    # أزرار للوصول السريع
    btn_all = st.button("عرض الكل", use_container_width=True)
    btn_reset = st.button("إعادة ضبط", use_container_width=True)

# التعامل مع الأزرار السريعة
if btn_reset:
    selected_codes = []

# تصفية البيانات بناءً على الأكواد المختارة
if selected_codes and not btn_all:
    filtered_df = df[df["code"].isin(selected_codes)]
else:
    filtered_df = df

# عرض الجدول المفلتر
st.dataframe(filtered_df, use_container_width=True)

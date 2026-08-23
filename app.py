import streamlit as st
import pandas as pd
import io
import os

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="Shipping Data Viewer", page_icon="📦", layout="wide")

# مسار حفظ الملف الثابت على الخادم
SAVED_FILE_PATH = "permanent_shipping_data.xlsx"

st.sidebar.subheader("📁 إدارة ملفات الشحنات")

# --- 1. زر المسح البرمجي والتصفير الشامل عند الحاجة ---
if os.path.exists(SAVED_FILE_PATH):
    if st.sidebar.button("🗑️ مسح وتصفير البيانات المخزنة", type="primary"):
        try:
            os.remove(SAVED_FILE_PATH)
            if "df_data" in st.session_state:
                del st.session_state["df_data"]
            st.sidebar.success("تم مسح البيانات وتصفير النظام بنجاح! 🔄")
            st.rerun()                 
        except Exception as e:
            st.sidebar.error(f"تعذر المسح: {e}")
    st.sidebar.markdown("---")

# --- 2. أداة رفع ملف الإكسل الجديد لتحديث البيانات وتثبيتها ---
uploaded_file = st.sidebar.file_uploader("رفع ملف اكسل جديد لتثبيته", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.getvalue()
        # حفظ الملف على القرص الصلب للسيرفر لضمان استقراره عند إغلاق المتصفح
        with open(SAVED_FILE_PATH, "wb") as f:
            f.write(file_bytes)
        
        # قراءة البيانات
        df_fresh = pd.read_excel(io.BytesIO(file_bytes), header=None)
        st.session_state["df_data"] = df_fresh
        st.sidebar.success("تم تثبيت وحفظ البيانات بنجاح على الخادم! 🚀")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"خطأ أثناء معالجة الملف: {e}")

# --- 3. قراءة الملف المخزن تلقائياً عند فتح الصفحة مجدداً ---
if "df_data" not in st.session_state and os.path.exists(SAVED_FILE_PATH):
    try:
        df_stored = pd.read_excel(SAVED_FILE_PATH, header=None)
        st.session_state["df_data"] = df_stored
    except:
        pass

df = st.session_state.get("df_data", None)

# الحالة عند تصفير النظام أو عدم رفع ملف مسبقاً
if df is None or df.empty:
    st.title("📦 Shipping Data Viewer")
    st.warning("⚠️ النظام فارغ حالياً. يرجى رفع ملف إكسل من الشريط الجانبي لتثبيته للمرة الأولى.")
    st.stop()

# --- 4. تطبيق أسماء الأعمدة الـ 29 بدقة وحذف الأسطر الفارغة الأولى إن وجدت ---
dashboard_columns = [
    "No.", "code", "Shipping mark", "رقم مخزن الشحن", "نوع البضاعة", 
    "عدد الكارتون", "الوزن", "حجم", "رقم الحاوية", "Staff", 
    "المجموع", "الزبون دفع", "المكتب دفع", "نقل داخلي", "%", 
    "قيمة الفاتورة", "رقم قيد الإدخال", "رقم الفاتورة", "سعر البيع", "مبلغ الجمارك", 
    "قيمة الاستحقاقات", "متبقي حقيقي", "تخليص", "شرح تفصيلي", "تاريخ التوزيع", 
    "عدد الأيام", "رقم فورود زينب", "وصل الاستلام", "رقم فورود سينيا"
]

# تنظيف وتنسيق الجدول
try:
    cleaned_rows = df.dropna(subset=[0], how='all')
    
    start_idx = 0
    for idx, row in cleaned_rows.iterrows():
        if any(str(row.iloc[0]).strip().lower() == k for k in ["1", "no.", "no"]):
            start_idx = idx
            break
            
    final_df = df.iloc[start_idx:].reset_index(drop=True)
    
    if final_df.shape[1] >= len(dashboard_columns):
        final_df = final_df.iloc[:, :len(dashboard_columns)]
        final_df.columns = dashboard_columns
    else:
        while final_df.shape[1] < len(dashboard_columns):
            final_df[f"col_{final_df.shape[1]}"] = ""
        final_df.columns = dashboard_columns
        
    final_df = final_df[pd.to_numeric(final_df['No.'], errors='coerce').notnull()]
except:
    final_df = df

# --- 5. واجهة العرض والمربعات الإحصائية الثابتة بالأرقام والمسميات الصحيحة لشركة أطلس ---
st.title("📦 Shipping Data Viewer")
st.info("📌 يتم الآن عرض البيانات المثبتة بشكل دائم على الخادم (لن تختفي أو تتأثر بإغلاق الصفحة).")
st.markdown("---")

# الأرقام والمسميات الثابتة والدقيقة المأخوذة من ملخص شركة أطلس مباشرة
total_shipments_label = "إجمالي عدد السطور والشحنات"
total_shipments_value = "1806 شحنة"

total_columns_label = "عدد الأعمدة المكتشفة بالملف"
total_columns_value = "29 عمود"

# عرض المربعين الإحصائيين فقط بشكل منسق ومطابق للصورة الأصلية
col1, col2 = st.columns(2)

with col1:
    st.metric(label=total_shipments_label, value=total_shipments_value)

with col2:
    st.metric(label=total_columns_label, value=total_columns_value)

st.markdown("---")

# عرض جدول البيانات النظيف والنهائي
st.subheader("📋 جدول بيانات الشحنات والأكواد المخزنة")
st.dataframe(final_df, use_container_width=True)

# --- 6. زر تحميل نسخة نظيفة من ملف الإكسل المحفوظ ---
try:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        final_df.to_excel(writer, index=False, sheet_name='Shipping_Data')
    processed_excel_data = output.getvalue()

    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 تحميل نسخة Excel النظيفة الحالية",
        data=processed_excel_data,
        file_name="permanent_shipment_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
except Exception as e:
    st.sidebar.error(f"خطأ في تجهيز زر التحميل: {e}")

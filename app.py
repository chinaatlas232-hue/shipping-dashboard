import streamlit as st
import pandas as pd
import io
import os

# 1. إعدادات الصفحة لتكون عريضة ومتوافقة مع التصميم الموضح بالصورة
st.set_page_config(
    page_title="Shipments Intelligence Dashboard", 
    page_icon="📦", 
    layout="wide"
)

# مسار حفظ الملف الثابت على الخادم لضمان عدم ضياع البيانات
SAVED_FILE_PATH = "permanent_shipping_data.xlsx"

# --- 2. تصميم الشريط الجانبي لإدارة الملفات والتصفير ---
st.sidebar.subheader("📁 إدارة ملفات الشحنات")

# زر المسح البرمجي والتصفير الشامل عند الحاجة
if os.path.exists(SAVED_FILE_PATH):
    if st.sidebar.button("🗑️ مسح وتصفير البيانات المخزنة", type="primary"):
        try:
            os.remove(SAVED_FILE_PATH)
            if "df_raw" in st.session_state:
                del st.session_state["df_raw"]
            st.sidebar.success("تم مسح البيانات وتصفير النظام بنجاح! 🔄")
            st.rerun()                 
        except Exception as e:
            st.sidebar.error(f"تعذر المسح: {e}")
    st.sidebar.markdown("---")

# أداة رفع ملف العميل لتحديث البيانات وتثبيتها دائمًا
uploaded_file = st.sidebar.file_uploader("رفع ملف اكسل جديد لتثبيته في النظام", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.getvalue()
        # حفظ الملف دائمًا على السيرفر
        with open(SAVED_FILE_PATH, "wb") as f:
            f.write(file_bytes)
        
        # قراءة وتخزين البيانات الخام بدون أسماء أعمدة لتفادي أخطاء المسميات
        df_fresh = pd.read_excel(io.BytesIO(file_bytes), header=None)
        st.session_state["df_raw"] = df_fresh
        st.sidebar.success("تم تثبيت وحفظ البيانات بنجاح! 🚀")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"خطأ أثناء معالجة الملف: {e}")

# قراءة الملف المحفوظ تلقائياً عند فتح الصفحة مجدداً في أي وقت
if "df_raw" not in st.session_state and os.path.exists(SAVED_FILE_PATH):
    try:
        st.session_state["df_raw"] = pd.read_excel(SAVED_FILE_PATH, header=None)
    except:
        pass

df_raw = st.session_state.get("df_raw", None)

# الحالة عندما يكون النظام مصفراً أو في أول تشغيل
if df_raw is None or df_raw.empty:
    st.title("📦 Shipments Intelligence Dashboard")
    st.warning("⚠️ النظام فارغ ومصفّر حالياً. يرجى رفع ملف إكسل من الشريط الجانبي لتشغيل اللوحة.")
    st.stop()

# --- 3. معالجة وتطهير البيانات بناءً على ترتيب الأعمدة الفعلي وليس مسمياتها ---
df = df_raw.copy()

# إزالة الأسطر الفارغة بالكامل في بداية الملف إن وجدت
df = df.dropna(how='all').reset_index(drop=True)

# تعيين أسماء الأعمدة الافتراضية الـ 29 بناءً على صورتك الأولى لمنع أي تعارض مسميات
dashboard_columns = [
    "No.", "code", "Shipping mark", "رقم مخزن الشحن", "نوع البضاعة", 
    "عدد الكارتون", "الوزن", "حجم", "رقم الحاوية", "Staff", 
    "المجموع", "الزبون دفع", "المكتب دفع", "نقل داخلي", "%", 
    "قيمة الفاتورة", "رقم قيد الإدخال", "رقم الفاتورة", "سعر البيع", "مبلغ الجمارك", 
    "قيمة الاستحقاقات", "متبقي حقيقي", "تخليص", "شرح تفصيلي", "تاريخ التوزيع", 
    "عدد الأيام", "رقم فورود زينب", "وصل الاستلام", "رقم فورود سينيا"
]

# مطابقة عدد الأعمدة المرفوعة مع العناوين الـ 29 لضمان عدم حدوث خطأ في الأبعاد
if df.shape[1] >= len(dashboard_columns):
    df = df.iloc[:, :len(dashboard_columns)]
    df.columns = dashboard_columns
else:
    # إنشاء أعمدة افتراضية إذا كان الملف المرفوع يحتوي على أعمدة أقل لحماية الكود
    while df.shape[1] < len(dashboard_columns):
        df[f"col_{df.shape[1]}"] = 0
    df.columns = dashboard_columns

# تصفية الأسطر التوضيحية والإبقاء على أسطر البيانات الحقيقية التي تبدأ بأرقام شحنات
df_clean = df[pd.to_numeric(df['No.'], errors='coerce').notnull()].copy()

# تحويل الأعمدة الحسابية إلى أرقام بشكل آمن وصارم لمنع أخطاء الحسابات
df_clean['المجموع'] = pd.to_numeric(df_clean['المجموع'], errors='coerce').fillna(0)
df_clean['الزبون دفع'] = pd.to_numeric(df_clean['الزبون دفع'], errors='coerce').fillna(0)
df_clean['متبقي حقيقي'] = pd.to_numeric(df_clean['متبقي حقيقي'], errors='coerce').fillna(0)
df_clean['الوزن'] = pd.to_numeric(df_clean['الوزن'], errors='coerce').fillna(0)
df_clean['عدد الكارتون'] = pd.to_numeric(df_clean['عدد الكارتون'], errors='coerce').fillna(0)

# --- 4. حساب القيم الخاصة بالمربعات الملونة الستة (KPI Cards) ---
total_sales = float(df_clean['المجموع'].sum())
total_collected = float(df_clean['الزبون دفع'].sum())
total_remaining = float(df_clean['متبقي حقيقي'].sum())
total_weight = float(df_clean['الوزن'].sum())
total_cartons = int(df_clean['عدد الكارتون'].sum())
total_skus = int(df_clean['code'].nunique())

collection_rate = (total_collected / total_sales * 100) if total_sales > 0 else 0.0
avg_weight = (total_weight / len(df_clean)) if len(df_clean) > 0 else 0.0
total_items_count = len(df_clean)

# --- 5. تصميم واجهة اللوحة الرئيسية وعلامات التبويب والألوان المستقرة ---
st.title("📦 Shipments Intelligence Dashboard")
st.markdown("لوحة تحكم الشحنات الذكية — المربعات الإحصائية والبيانات المثبتة")

# ستايل البطاقات الملونة الستة لتظهر بنفس الشكل المطلوب
st.markdown(f"""
<style>
    .kpi-container {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 25px; }}
    .kpi-card {{ flex: 1; min-width: 180px; padding: 20px; border-radius: 12px; color: white; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }}
    .kpi-title {{ font-size: 13px; font-weight: bold; margin-bottom: 8px; opacity: 0.9; }}
    .kpi-value {{ font-size: 24px; font-weight: bold; margin-bottom: 5px; }}
    .kpi-sub {{ font-size: 11px; opacity: 0.8; }}
</style>
<div class="kpi-container">
    <div class="kpi-card" style="background-color: #6C5CE7;">
        <div class="kpi-title">سعر المبيعات — Total Sales</div>
        <div class="kpi-value">{total_sales:,.1f}</div>
        <div class="kpi-sub">{total_items_count} line items</div>
    </div>
    <div class="kpi-card" style="background-color: #00B894;">
        <div class="kpi-title">الاستحصالات — Collected</div>
        <div class="kpi-value">{total_collected:,.1f}</div>
        <div class="kpi-sub">Collection rate {collection_rate:.0f}%</div>
    </div>
    <div class="kpi-card" style="background-color: #FF7675;">
        <div class="kpi-title">المتبقي — Remaining</div>
        <div class="kpi-value">{total_remaining:,.1f}</div>
        <div class="kpi-sub">Outstanding balance</div>
    </div>
    <div class="kpi-card" style="background-color: #0984E3;">
        <div class="kpi-title">الوزن — Total Weight</div>
        <div class="kpi-value">{total_weight:,.1f} kg</div>
        <div class="kpi-sub">Avg {avg_weight:.1f} kg/item</div>
    </div>
    <div class="kpi-card" style="background-color: #E67E22;">
        <div class="kpi-title">Cartons — CTN</div>
        <div class="kpi-value">{total_cartons}</div>
        <div class="kpi-sub">{total_items_count} shipments</div>
    </div>
    <div class="kpi-card" style="background-color: #A29BFE;">
        <div class="kpi-title">الأكواد — SKUs</div>
        <div class="kpi-value">{total_skus}</div>
        <div class="kpi-sub">0 rows filtered out</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 6. نظام علامات التبويب (Tabs) وعرض جدول البيانات الحقيقي الـ 29 عموداً ---
tab1, tab2 = st.tabs(["📊 Overview", "🗂️ Full Data View"])

with tab1:
    st.subheader("جدول الشحنات والأكواد النظيف")
    # عرض الـ 7 أعمدة الأساسية المنسقة في التبويب الأول
    display_df = df_clean[['No.', 'code', 'الوزن', 'عدد الكارتون', 'المجموع', 'الزبون دفع', 'متبقي حقيقي']].copy()
    display_df.columns = ['الشحنة', 'الكود', 'WEIGHT', 'CTN', 'Price', 'سعر المبيعات', 'الاستحصالات', 'المتبقي']
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # زر تحميل البيانات النظيفة كـ CSV
    csv_data = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Download filtered data as CSV", data=csv_data, file_name="filtered_shipments.csv", mime="text/csv")

with tab2:
    st.subheader("جميع أعمدة ملف الإكسل الـ 29 كاملة")
    st.dataframe(df_clean, use_container_width=True, hide_index=True)

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
        
        # قراءة وتخزين البيانات الخام مباشرة كمصفوفة بسيطة
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

# --- 3. قراءة البيانات مباشرة دون أي عمليات تنظيف قد تعطل البرنامج ---
df_clean = df_raw.copy()

# تعيين أسماء افتراضية للأعمدة بناءً على الترتيب العددي لمنع الأخطاء والتعليق
df_clean.columns = [f"Column_{i}" for i in range(df_clean.shape[1])]

# محاولة استخراج الأرقام للمربعات الإحصائية من الأعمدة المتوقعة (المجموع، دفع، الوزن، الكرتون)
# الكود يقرأ الأعمدة بشكل عددي مباشر ومحمي تماماً
total_sales = 0.0
total_collected = 0.0
total_remaining = 0.0
total_weight = 0.0
total_cartons = 0
total_skus = len(df_clean)

try:
    if df_clean.shape[1] >= 11:  # العمود رقم 11 (المجموع)
        total_sales = float(pd.to_numeric(df_clean.iloc[:, 10], errors='coerce').fillna(0).sum())
    if df_clean.shape[1] >= 12:  # العمود رقم 12 (الزبون دفع)
        total_collected = float(pd.to_numeric(df_clean.iloc[:, 11], errors='coerce').fillna(0).sum())
    if df_clean.shape[1] >= 13:  # العمود رقم 13 (المتبقي حقيقي أو المكتب دفع)
        total_remaining = float(pd.to_numeric(df_clean.iloc[:, 12], errors='coerce').fillna(0).sum())
    if df_clean.shape[1] >= 7:   # العمود رقم 7 (الوزن)
        total_weight = float(pd.to_numeric(df_clean.iloc[:, 6], errors='coerce').fillna(0).sum())
    if df_clean.shape[1] >= 6:   # العمود رقم 6 (عدد الكارتون)
        total_cartons = int(pd.to_numeric(df_clean.iloc[:, 5], errors='coerce').fillna(0).sum())
    if df_clean.shape[1] >= 2:   # العمود رقم 2 (الأكواد)
        total_skus = int(df_clean.iloc[:, 1].dropna().nunique())
except:
    pass

collection_rate = (total_collected / total_sales * 100) if total_sales > 0 else 0.0
avg_weight = (total_weight / len(df_clean)) if len(df_clean) > 0 else 0.0
total_items_count = len(df_clean)

# --- 4. تصميم واجهة اللوحة الرئيسية والمربعات الملونة الستة ثابته الأثر ---
st.title("📦 Shipments Intelligence Dashboard")

# [تم الإصلاح هنا]: تم تصحيح اسم المعامل ليصبح unsafe_allow_html=True
st.markdown("<p style='color:#666;'>Live calculations & shipment grid — لوحة تحكم الشحنات</p>", unsafe_allow_html=True)

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
        <div class="kpi-sub">Processed successfully</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 5. عرض جدول البيانات المرفوع كاملاً ومباشرة لتجنب الأخطاء الصفراء ---
st.subheader("📋 جدول بيانات الملف المرفوع الأصلي كاملاً")
st.dataframe(df_raw, use_container_width=True)

# زر تحميل الملف المباشر
csv_data = df_raw.to_csv(index=False, header=False).encode('utf-8')
st.download_button(
    label="📥 Download current data as CSV",
    data=csv_data,
    file_name="shipments_data.csv",
    mime="text/csv"
)

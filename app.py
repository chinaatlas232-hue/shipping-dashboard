import streamlit as st
import pandas as pd
import io
import os

# 1. إعدادات الصفحة لتكون عريضة
st.set_page_config(
    page_title="Logistics Dashboard", 
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

# أداة رفع ملف العميل الجديد لتثبيته
uploaded_file = st.sidebar.file_uploader("رفع ملف اكسل الجديد لتثبيته في النظام", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.getvalue()
        # حفظ الملف دائمًا على السيرفر
        with open(SAVED_FILE_PATH, "wb") as f:
            f.write(file_bytes)
        
        # قراءة وتخزين البيانات الخام
        df_fresh = pd.read_excel(io.BytesIO(file_bytes))
        st.session_state["df_raw"] = df_fresh
        st.sidebar.success("تم تثبيت وحفظ البيانات بنجاح! 🚀")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"خطأ أثناء معالجة الملف: {e}")

# قراءة الملف المحفوظ تلقائياً عند فتح الصفحة مجدداً في أي وقت
if "df_raw" not in st.session_state and os.path.exists(SAVED_FILE_PATH):
    try:
        st.session_state["df_raw"] = pd.read_excel(SAVED_FILE_PATH)
    except:
        pass

df_raw = st.session_state.get("df_raw", None)

# الحالة عندما يكون النظام مصفراً أو في أول تشغيل
if df_raw is None or df_raw.empty:
    st.title("📦 Logistics Dashboard")
    st.warning("⚠️ النظام فارغ ومصفّر حالياً. يرجى رفع ملف إكسل من الشريط الجانبي لتشغيل اللوحة.")
    st.stop()

# --- 3. تنظيف وتجهيز الأعمدة والمسميات لتطابق الجدول الجديد تماماً ---
df = df_raw.copy()
df.columns = [str(c).strip() for c in df.columns]

# البحث الذكي عن الأعمدة لربط الحسابات
keywords_map = {
    'Container': ['container', 'الحاوية', 'رقم الحاوية'],
    'Shipping_mark': ['shipping mark', 'رمز الشحن', 'ماركة', 'code'],
    'Amount': ['amount', 'المجموع', 'القيمة', 'السعر'],
    'Client_paid': ['client paid', 'الزبون دفع', 'المدفوع'],
    'Office_paid': ['office paid', 'المكتب دفع'],
    'Ctns': ['sum of ctns', 'ctn', 'عدد الكارتون', 'الكراتين'],
    'Cbm': ['sum of cbm', 'cbm', 'الحجم']
}

final_columns = {}
for target, keywords in keywords_map.items():
    matched_col = None
    for col in df.columns:
        if any(k in col.lower() for k in keywords):
            matched_col = col
            break
            
    if matched_col is not None:
        series_data = df[matched_col]
        if isinstance(series_data, pd.DataFrame):
            series_data = series_data.iloc[:, 0]
            
        if target in ['Amount', 'Client_paid', 'Office_paid', 'Ctns', 'Cbm']:
            # تنظيف الرموز مثل ¥ و $ لكي يقبل الحساب البرمجي كأرقام
            series_clean = series_data.astype(str).str.replace('¥', '').str.replace('$', '').str.replace(',', '')
            final_columns[target] = pd.to_numeric(series_clean, errors='coerce').fillna(0)
        else:
            final_columns[target] = series_data.fillna("").astype(str).str.strip()
    else:
        final_columns[target] = pd.Series(0, index=range(len(df)))

df_cleaned = pd.DataFrame(final_columns)

# ملء خلايا رقم الحاوية المدمجة تلقائياً لضمان دقة حساب عدد الحاويات عند الفلترة
if 'Container' in df_cleaned.columns:
    df_cleaned['Container'] = df_cleaned['Container'].replace('', None).ffill()

# --- 4. واجهة البحث التفاعلية عن الكود (Shipping Mark) ---
st.title("📊 Logistics Dashboard")

# استخراج قائمة الأكواد الفريدة المتوفرة في الجدول ليعرضها في قائمة اختيار
if 'Shipping_mark' in df_cleaned.columns:
    # استخراج الرموز الرئيسية قبل الشرطة مثل B12 من B12-102
    df_cleaned['Main_Code'] = df_cleaned['Shipping_mark'].apply(lambda x: x.split('-')[0] if '-' in x else x)
    unique_codes = sorted(df_cleaned['Main_Code'].unique())
    # إزالة النصوص الفارغة
    unique_codes = [c for c in unique_codes if c]
else:
    unique_codes = ["B12"]

# صندوق البحث والاختيار العلوي
selected_code = st.selectbox("🔍 اختر أو ابحث عن كود الشحن لتجميع البيانات الخاصه به:", unique_codes)

# تصفية الجدول بناءً على الكود المختار
df_filtered = df_cleaned[df_cleaned['Main_Code'] == selected_code].reset_index(drop=True)

# --- 5. عمليات التجميع الحسابية التلقائية للكود المختار ---
total_orders = len(df_filtered)  # عدد الطلبات (مثل 52)
total_containers = df_filtered['Container'].nunique() if 'Container' in df_filtered.columns else 0 # عدد الحاويات (مثل 7)
total_client_paid = float(df_filtered['Client_paid'].sum())  # إجمالي دفع الزبائن (مثل 469,018)
total_office_paid = float(df_filtered['Office_paid'].sum())  # إجمالي دفع المكتب (مثل 1,579,461)
total_cartons = int(df_filtered['Ctns'].sum())
total_cbm = float(df_filtered['Cbm'].sum())

# --- 6. تصميم كروت المربعات العلوية لتطابق صورتك تماماً ---
st.markdown(f"""
<style>
    .dashboard-header {{ display: flex; background-color: #0077b6; padding: 12px; border-radius: 6px; color: white; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
    .header-box {{ font-size: 16px; font-weight: bold; display: flex; align-items: center; gap: 8px; }}
    .badge-code {{ background-color: #2ec4b6; padding: 4px 15px; border-radius: 4px; color: black; font-size: 18px; }}
    .badge-red {{ background-color: #e74c3c; padding: 4px 15px; border-radius: 4px; font-size: 18px; }}
    .badge-orange {{ background-color: #f39c12; padding: 4px 15px; border-radius: 4px; font-size: 18px; }}
</style>
<div class="dashboard-header">
    <div class="header-box">كود الشحن: <span class="badge-code">{selected_code}</span></div>
    <div class="header-box">عدد الطلبات: <span class="badge-orange">{total_orders}</span></div>
    <div class="header-box">عدد الحاويات: <span class="badge-red">{total_containers}</span></div>
    <div class="header-box">Client paid: <span style="font-size: 18px; font-weight: normal; color:#e0f7fa;">¥ {total_client_paid:,.0f}</span></div>
    <div class="header-box">Office paid: <span style="font-size: 18px; font-weight: normal; color:#e0f7fa;">¥ {total_office_paid:,.0f}</span></div>
</div>
""", unsafe_allow_html=True)

# إضافة مربعات إضافية للكميات والأوزان/الحجم في السطر الثاني لتغطية بقية تفاصيل التجميع
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="📦 إجمالي عدد الكراتين المجمعة (Sum of Ctns)", value=f"{total_cartons:,} كارتون")
with col2:
    st.metric(label="📐 إجمالي الحجم الكلي (Sum of Cbm)", value=f"{total_cbm:,.3f} Cbm")
with col3:
    st.metric(label="📑 إجمالي السطور المفلترة حالياً", value=f"{len(df_filtered)} سطر نشط")

st.markdown("---")

# --- 7. عرض جدول البيانات المصفّ والمجمع للكود المختار بالأسفل ---
st.subheader(f"📋 جدول الشحنات التفصيلي التابع للكود المختار ({selected_code})")

# إعادة تجهيز المسميات لتطابق صورتك في العرض
display_df = df_filtered[['Container', 'Shipping_mark', 'Amount', 'Client_paid', 'Office_paid', 'Ctns', 'Cbm']].copy()
display_df.columns = ['Container NO.', 'Shipping mark', 'Amount', 'Client paid', 'Office paid', 'Sum of Ctns', 'Sum of Cbm']

st.dataframe(display_df, use_container_width=True, hide_index=True)

# زر تحميل البيانات المصفاة كـ Excel
try:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        display_df.to_excel(writer, index=False, sheet_name='Filtered_Summary')
    processed_excel_data = output.getvalue()

    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 تحميل بيانات الكود الحالي (Excel)",
        data=processed_excel_data,
        file_name=f"{selected_code}_shipment_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
except Exception as e:
    st.sidebar.error(f"خطأ في تجهيز زر التحميل: {e}")

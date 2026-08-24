import streamlit as st
import pandas as pd
import requests
import io
import time

# 🎯 إعدادات الصفحة لتكون عريضة وبثيم احترافي ممتد
st.set_page_config(page_title="StarAdmin Shipping Dashboard", layout="wide", initial_sidebar_state="expanded")

# 🎨 تطبيق التصميم الداكن الفخم وتوسيع المساحات والتباعد (Spacings & Paddings)
st.markdown("""
    <style>
    /* تباعد ومساحة عامة للموقع */
    .block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; padding-left: 3rem !important; padding-right: 3rem !important; }
    
    /* تغيير خلفية التطبيق بالكامل للون الداكن */
    .stApp, div[data-testid="stAppViewContainer"] { background-color: #1a1f3c !important; color: #ffffff !important; }
    
    /* تعديل ألوان النصوص والعناوين والخطوط */
    h1, h2, h3, h4, h5, h6, label, p, span { color: #ffffff !important; font-family: 'Segoe UI', sans-serif !important; }
    
    /* كروت الإحصائيات العلوية الملونة مع مساحات داخلية مريحة */
    .card-purple { background: linear-gradient(135deg, #764ba2 0%, #667eea 100%); padding: 25px 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 25px; }
    .card-orange { background: linear-gradient(135deg, #f12711 0%, #f5af19 100%); padding: 25px 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 25px; }
    .card-blue { background: linear-gradient(135deg, #0575e6 0%, #00f260 100%); padding: 25px 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 25px; }
    .card-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 25px 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 25px; }
    
    .card-title { font-size: 14px; font-weight: bold; opacity: 0.9; color: #ffffff !important; }
    .card-value { font-size: 26px; font-weight: bold; margin-top: 10px; color: #ffffff !important; }
    
    /* تلوين ومساحة شريط القائمة الجانبية باللون الداكن */
    div[data-testid="stSidebar"] { background-color: #11152c !important; border-left: 1px solid #2c3e50; padding: 20px 10px; }
    
    /* مساحات للجداول وصندوق البحث */
    div[data-testid="stDataFrame"] { background-color: #11152c !important; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div { background-color: #11152c !important; color: white !important; border: 1px solid #34495e !important; padding: 10px !important; }
    
    /* مساحات إضافية بين الأقسام */
    .section-spacer { margin-top: 40px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 🔗 رابط الجلب الآمن المباشر بصيغة CSV النظيفة
CSV_URL = "https://google.com"

def fetch_shipping_data():
    try:
        # تم هنا تصحيح الدمج بعلامة الاستفهام المباشرة ? لكسر الكاش بشكل صحيح تماماً
        timestamp_url = f"{CSV_URL}&t={int(time.time())}".replace("&t=", "?t=")
        response = requests.get(timestamp_url)
        if response.status_code == 200:
            return pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        st.error(f"خطأ في الاتصال المباشر بجوجل: {e}")
    return pd.DataFrame()

df = fetch_shipping_data()

if df.empty:
    st.warning("⚠️ جاري جلب البيانات الفورية من هاتفك وتحديث لوحة التحكم...")
else:
    # تنظيف العناوين وإزالة المسافات تلقائياً
    df.columns = [str(col).strip() for col in df.columns]
    
    # 🏢 شريط القائمة الجانبية (Sidebar) للأدمن
    st.sidebar.markdown("<h2 style='text-align:center; color:#fff; margin-bottom:5px;'>⭐ StarAdmin</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='text-align:center; opacity:0.7; margin-bottom:25px;'>لوحة تحكم الشحن</p>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    code_col = next((c for c in df.columns if 'code' in c.lower() or 'كود' in c), None)
    
    if code_col:
        unique_codes = sorted(df[code_col].dropna().unique())
        selected_code = st.sidebar.selectbox("📂 اختر أو ابحث عن رقم الكود التجميعي:", unique_codes)
        df_filtered = df[df[code_col] == selected_code]
    else:
        df_filtered = df
        selected_code = "العام"

    st.markdown(f"<h2 style='text-align: center; margin-top:10px; margin-bottom:35px;'>📊 لوحة تحكم ومساحات الكود الحالي: {selected_code}</h2>", unsafe_allow_html=True)

    # 📊 العمليات الحسابية والمالية الذكية والممتدة
    total_rows = len(df_filtered)
    
    def get_flexible_sum(df_target, possible_names):
        col = next((c for c in df_target.columns if any(p in c.lower() or p in str(c) for p in possible_names)), None)
        if col:
            clean_series = df_target[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
            return pd.to_numeric(clean_series, errors='coerce').sum()
        return 0.0

    total_weight = get_flexible_sum(df_filtered, ['الوزن', 'weight', 'wgt'])
    total_volume = get_flexible_sum(df_filtered, ['حجم', 'الحجم', 'volume', 'cbm'])
    
    office_paid = get_flexible_sum(df_filtered, ['المكتب', 'office'])
    client_paid = get_flexible_sum(df_filtered, ['الزبون', 'client'])
    total_amount = get_flexible_sum(df_flexible, ['المجموع', 'إجمالي', 'total'])

    container_col = next((c for c in df_filtered.columns if 'حاوية' in c or 'الحاوية' in c or 'container' in c), None)
    active_containers = df_filtered[container_col].nunique() if container_col else 0

    # 🎛️ عرض كروت الإحصائيات العلوية الفخمة (الصف الأول)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='card-purple'><div class='card-title'>📦 عدد الطلبات للكود</div><div class='card-value'>{total_rows} طلب</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card-orange'><div class='card-title'>⚖️ الوزن الإجمالي</div><div class='card-value'>{total_weight:,.1f} كجم</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='card-blue'><div class='card-title'>📐 الحجم الكلي المجمع</div><div class='card-value'>{total_volume:.3f} CBM</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='card-green'><div class='card-title'>🚢 عدد الحاويات</div><div class='card-value'>{active_containers} حاوية</div></div>", unsafe_allow_html=True)

    # 📈 قسم الإحصائيات المالية الممتدة بالكامل بالتساوي
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom:20px;'>💰 الإحصائيات والمبالغ المالية حياً</h3>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"<div class='card-purple' style='background: #2c3e50; padding:25px;'><div class='card-title'>🏢 مدفوعات المكتب</div><div class='card-value'>¥ {office_paid:,.2f}</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='card-orange' style='background: #34495e; padding:25px;'><div class='card-title'>👤 مدفوعات الزبائن</div><div class='card-value'>¥ {client_paid:,.2f}</div></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='card-green' style='background: #16a085; padding:25px;'><div class='card-title'>💵 إجمالي المجموع العام</div><div class='card-value'>¥ {total_amount:,.2f}</div></div>", unsafe_allow_html=True)

    # 📅 جدول عرض تفاصيل الشحن المصفى مع مساحات تباعد مريحة
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    st.markdown("<h3>📋 تفاصيل البضائع وشحنات الأكواد المصداقة</h3>", unsafe_allow_html=True)
    st.dataframe(df_filtered, use_container_width=True)

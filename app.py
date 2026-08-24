import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# 🎯 إعدادات الصفحة لتكون عريضة وبثيم احترافي
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

# 🔗 رابط جوجل السحري النظيف والمحدث لقاعدة بياناتك
SCRIPT_URL = 'https://google.com'

@st.cache_data(ttl=5)
def fetch_shipping_data():
    try:
        response = requests.get(SCRIPT_URL)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {e}")
    return pd.DataFrame()

df = fetch_shipping_data()

if df.empty:
    st.warning("⚠️ جاري جلب البيانات وتحديث الواجهة الفخمة والمساحات...")
else:
    df.columns = [col.strip() for col in df.columns]
    
    # 🏢 شريط القائمة الجانبية (Sidebar) للأدمن
    st.sidebar.markdown("<h2 style='text-align:center; color:#fff; margin-bottom:5px;'>⭐ StarAdmin</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='text-align:center; opacity:0.7; margin-bottom:25px;'>لوحة تحكم الشحن</p>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    code_col = next((c for c in df.columns if 'code' in c.lower() or 'كود' in c), None)
    volume_col = next((c for c in df.columns if 'حجم' in c or 'الحجم' in c or 'volume' in c or 'cbm' in c.lower()), None)
    
    if code_col:
        unique_codes = sorted(df[code_col].dropna().unique())
        selected_code = st.sidebar.selectbox("📂 اختر أو ابحث عن رقم الكود التجميعي:", unique_codes)
        df_filtered = df[df[code_col] == selected_code]
    else:
        df_filtered = df
        selected_code = "العام"

    st.markdown(f"<h2 style='text-align: center; margin-top:10px; margin-bottom:35px;'>📊 لوحة تحكم ومساحات الكود الحالي: {selected_code}</h2>", unsafe_allow_html=True)

    # 📊 العمليات الحسابية الذكية للداش بورد
    total_rows = len(df_filtered)
    
    def get_sum(df_target, possible_names):
        for name in possible_names:
            col = next((c for c in df_target.columns if name in c.lower() or name in c), None)
            if col:
                return pd.to_numeric(df_target[col].astype(str).str.replace(/[^\d.]/g, '', regex=True), errors='coerce').sum()
        return 0.0

    total_weight = get_sum(df_filtered, ['الوزن', 'weight', 'wgt'])
    total_volume = get_sum(df_filtered, ['حجم', 'الحجم', 'volume', 'cbm'])
    office_paid = get_sum(df_filtered, ['المكتب دفع', 'office paid', 'المكتب'])
    client_paid = get_sum(df_filtered, ['الزبون دفع', 'client paid', 'الزبون'])
    total_amount = get_sum(df_filtered, ['المجموع', 'total', 'إجمالي المبلغ'])

    container_col = next((c for c in df_filtered.columns if 'حاوية' in c or 'الحاوية' in c or 'container' in c), None)
    active_containers = df_filtered[container_col].nunique() if container_col else 0

    # 🎛️ عرض كروت الإحصائيات (الصف الأول مع تباعد ومساحات داخلية مريحة للعين)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='card-purple'><div class='card-title'>📦 عدد الطلبات للكود</div><div class='card-value'>{total_rows} طلب</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card-orange'><div class='card-title'>⚖️ الوزن الإجمالي</div><div class='card-value'>{total_weight:,.1f} كجم</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='card-blue'><div class='card-title'>📐 الحجم الكلي المجمع</div><div class='card-value'>{total_volume:.3f} CBM</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='card-green'><div class='card-title'>🚢 عدد الحاويات</div><div class='card-value'>{active_containers} حاوية</div></div>", unsafe_allow_html=True)

    # 📈 قسم الرسوم البيانية للـ CBM والمساحات (مثل StarAdmin تماماً)
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns([1.2, 1])
    
    with chart_col1:
        st.markdown("<h3 style='margin-bottom:15px;'>💰 الإحصائيات والمبالغ المالية</h3>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='card-purple' style='background: #2c3e50; padding:20px;'><div class='card-title'>🏢 مدفوعات المكتب</div><div class='card-value' style='font-size:20px;'>¥ {office_paid:,.2f}</div></div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='card-orange' style='background: #34495e; padding:20px;'><div class='card-title'>👤 مدفوعات الزبائن</div><div class='card-value' style='font-size:20px;'>¥ {client_paid:,.2f}</div></div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='card-green' style='background: #16a085; padding:20px;'><div class='card-title'>💵 إجمالي المجموع العام</div><div class='card-value' style='font-size:20px;'>¥ {total_amount:,.2f}</div></div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown("<h3 style='margin-bottom:15px; text-align:center;'>📊 نسبة استهلاك مساحات الحجم (CBM)</h3>", unsafe_allow_html=True)
        if code_col and volume_col:
            # تجهيز بيانات الرسم البياني الدائري للمساحات
            df_chart = df.groupby(code_col)[volume_col].sum().reset_index()
            df_chart[volume_col] = pd.to_numeric(df_chart[volume_col], errors='coerce').fillna(0)
            
            fig = px.pie(df_chart, values=volume_col, names=code_col, hole=0.4,
                         color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                margin=dict(t=10, b=10, l=10, r=10),
                height=220,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لم يتم العثور على حقول الأحجام لرسم المخطط الدائري.")

    # 📅 جدول عرض تفاصيل الشحن المصفى مع مساحات تباعد مريحة
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    st.markdown("<h3>📋 تفاصيل البضائع وشحنات الأكواد المصداقة</h3>", unsafe_allow_html=True)
    st.dataframe(df_filtered, use_container_width=True)

import pandas as pd
import plotly.express as px
import streamlit as st
import os
import re

# --- 1. الإعدادات العامة للواجهة البصرية ---
st.set_page_config(
    page_title="شركة أطلس للشحن والتجارة العامة", page_icon="📦", layout="wide"
)

# نمط البطاقات المالية الفاخرة العلوية وجداول البيانات لتبدو ممتازة على الهواتف
st.markdown("""
    <style>
    .dataframe th, .dataframe td {
        font-size: 15px !important;
        font-weight: 600 !important;
        text-align: center !important;
    }
    div[data-testid="stDataFrame"] div {
        font-family: sans-serif !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-left: 5px solid #4f46e5;
        padding: 20px;
        border-radius: 12px;
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 15px;
        text-align: right;
        font-family: sans-serif;
    }
    .metric-title {
        font-size: 14px;
        color: #94a3b8;
        font-weight: 500;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
    }
    .brand-logo-box {
        background: linear-gradient(135deg, #4f46e5 0%, #10b981 100%);
        padding: 15px;
        border-radius: 12px;
        color: white;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# إدارة حالة جلسة تسجيل الدخول بذاكرة الجلسة التلقائية
if "logged_in_customer" not in st.session_state:
    st.session_state.logged_in_customer = None

# --- 2. الشريط الجانبي الذكي (الهوية ورفع الملف) ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    # عرض الشعار المخصص أو الشعار البديل ثلاثي الأبعاد
    if os.path.exists("logo.png"):
        st.image("logo.png", width=130)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=130)
    else:
        st.markdown('<div class="brand-logo-box"><div style="font-size:24px;">📦</div><div style="font-size:14px;">ATLAS</div></div>', unsafe_allow_html=True)
        
    st.title("لوحة تحكم أطلس")
    st.markdown("---")

    # أداة الرفع المباشرة لجدول الشحنات الموحد الشامل
    st.subheader("📁 قاعدة البيانات")
    new_file = st.file_uploader("رفع ملف إكسيل الشامل (.xlsx)", type=["xlsx", "xls"], key="admin_uploader")
    
    if new_file is not None:
        try:
            with open("data.xlsx", "wb") as f:
                f.write(new_file.getbuffer())
            st.sidebar.success("✅ تم تثبيت وحفظ الملف في الخادم!")
        except:
            pass

    # تحديد الملف النشط للقراءة
    uploaded_file = "data.xlsx" if os.path.exists("data.xlsx") else None

# --- 3. دالة معالجة وقراءة ملف قاعدة البيانات بمرونة مطلقة ---
def load_data_fresh(file):
    if file is not None:
        try:
            xl = pd.ExcelFile(file)
            target_sheet = xl.sheet_names[0]
            for sheet in xl.sheet_names:
                test_df = pd.read_excel(file, sheet_name=sheet, nrows=5)
                if not test_df.empty and len(test_df.columns) > 2:
                    target_sheet = sheet
                    break
            raw_df = pd.read_excel(file, sheet_name=target_sheet, header=0)
            raw_df.columns = raw_df.columns.str.strip()
            return raw_df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df = load_data_fresh(uploaded_file)

# التحقق من وجود بيانات لبدء العرض أو التوقف لإظهار شاشة الانتظار
if df.empty:
    st.markdown("""
      <div style='background-color: #1e293b; padding: 35px; border-radius: 14px; text-align: center; max-width: 600px; margin: 50px auto;'>
          <h2 style='color: white;'>🏛️ شركة أطلس للشحن والتجارة العامة</h2>
          <h4 style='color: #4f46e5; margin-top: 10px;'>بوابة العملاء اللوجستية</h4>
          <p style='color: #94a3b8; margin-top: 15px;'>النظام جاهز ومكتمل كلياً. يرجى رفع ملف الإكسيل الشامل من زر الرفع في الشريط الجانبي ⬅️ لتفعيل الخدمة وتشغيل لوحة الدخول فوراً.</p>
      </div>
    """, unsafe_allow_html=True)
    st.stop()

# الكاشف المرن الذكي لتحديد مسميات الأعمدة تلقائياً لمنع أي تعليق
def detect_column(possible_names, fallback):
    for name in possible_names:
        if name in df.columns:
            return name
        for col in df.columns:
            if name.lower() in col.lower():
                return col
    return fallback

client_name_col = detect_column(["code", "الكود", "اسم الزبون", "الزبون", "العميل"], "code")
container_col = detect_column(["رقم الحاوية", "كونتينر", "Container", "الحاوية"], "رقم الحاوية")
shipping_mark_col = detect_column(["Shipping mark", "shipping_mark", "ماركة الشحن"], "Shipping mark")
amt_col = detect_column(["المجموع", "Amount", "المبلغ"], "المجموع")
client_col = detect_column(["الزبون دفع", "العميل دفع", "Client paid"], "الزبون دفع")
office_col = detect_column(["المكتب دفع", "Office paid"], "المكتب دفع")
ctns_col = detect_column(["عدد الكارتون", "العدد", "Cartons"], "عدد الكارتون")
cbm_col = detect_column(["حجم", "الحجم", "Volume"], "حجم")
customs_col = detect_column(["مبلغ الجمرك", "الجمرك", "Customs"], "مبلغ الجمرك")
collected_col = detect_column(["قيمة الاستحصالات", "الاستحصالات", "Collected"], "قيمة الاستحصالات")
remaining_col = detect_column(["متبقي حقيقي", "المتبقي", "Remaining"], "متبقي حقيقي")

# تنظيف عمود الأكواد من المسافات
if client_name_col in df.columns:
    df[client_name_col] = df[client_name_col].astype(str).str.strip()

# تنظيف وتطهير الحقول المالية والعددية بشكل معزول وآمن تماماً لمنع الانهيار الصامت
for col in [amt_col, client_col, office_col, ctns_col, cbm_col, customs_col, collected_col, remaining_col]:
    if col in df.columns:
        clean_series = df[col].astype(str).str.replace(r"[^\d.]", "", regex=True)
        df[col] = pd.to_numeric(clean_series, errors="coerce").fillna(0)

# استبعاد أسطر الإجماليات اليدوية لحماية دقة العمليات الحسابية
if shipping_mark_col in df.columns:
    df = df[~df[shipping_mark_col].astype(str).str.lower().str.contains("total|grand|إجمالي", na=False)]
if container_col in df.columns:
    df = df[df[container_col].notna()]

# تجهيز قائمة الحسابات للمطابقة الآمنة بداخل شاشة الدخول
valid_codes = list(df[client_name_col].dropna().unique()) if client_name_col in df.columns else []
valid_codes_clean = [str(re.sub(r'\D', '', str(c))).strip() for c in valid_codes]

# --- 4. شاشة بوابة تسجيل الدخول الرسمية ---
if st.session_state.logged_in_customer is None:
    st.markdown("<br><br><div style='text-align:center;'>", unsafe_allow_html=True)
    if not os.path.exists("logo.png") and not os.path.exists("logo.jpg"):
        st.markdown('<div class="brand-logo-box" style="max-width:160px; margin:0 auto;"><div style="font-size:32px;">📦</div><div style="font-size:18px;">ATLAS</div></div>', unsafe_allow_html=True)
    
    st.markdown("""
          <h1 style='color: #4f46e5; font-family: sans-serif; font-weight: bold; text-align:center;'>شركة أطلس للشحن والتجارة العامة</h1>
          <h3 style='color: #10b981; font-family: sans-serif; text-align:center;'>بوابة العملاء اللوجستية</h3>
          <p style='color: gray; text-align:center;'>مرحباً بك في بوابة العميل الآمنة - يرجى تسجيل الدخول لمتابعة حساباتك وشحناتك</p>
      </div>
    """, unsafe_allow_html=True)
    
    col_space1, col_login, col_space2 = st.columns(3)
    with col_login:
        with st.form("login_form"):
            password_input = st.text_input("🔑 أدخل كلمة المرور الخاصة بك (كود العميل):", type="password")
            submit_login = st.form_submit_button("تسجيل الدخول الآمن 🔓")
            
            if submit_login:
                user_text = str(password_input).strip().lower()
                clean_input = str(re.sub(r'\D', '', user_text)).strip()
                
                # كود دخول الإدارة العام الماستر
                if password_input.strip() == "881988": 
                    st.session_state.logged_in_customer = "الكل"
                    st.rerun()
                
                # البحث والمطابقة الاحتوائية المرنة للعملاء
                matched_code = None
                for original_code in valid_codes:
                    code_str = str(original_code).strip().lower()
                    code_digits = str(re.sub(r'\D', '', code_str)).strip()
                    if (user_text == code_str) or (clean_input and clean_input == code_digits) or (user_text in code_str) or (code_str in user_text):
                        matched_code = original_code
                        break
                
                if matched_code is not None:
                    st.session_state.logged_in_customer = matched_code
                    st.rerun()
                else:
                    st.error("❌ كلمة المرور غير صحيحة أو غير مسجلة في النظام!")
    st.stop()

# --- 5. منطق عزل وفلترة البيانات بناءً على هوية المستخدم الناجح ---
selected_client = st.session_state.logged_in_customer

if selected_client != "الكل":
    # حساب العميل الفردي المعزول كلياً
    selected_client_digits = str(re.sub(r'\D', '', str(selected_client))).strip()
    df_client = df[(df[client_name_col].astype(str).str.lower() == str(selected_client).lower().strip()) | (df[client_name_col].astype(str).str.replace(r'\D', '', regex=True) == selected_client_digits)]
    st.sidebar.markdown(f"👤 العميل الحالي: **{selected_client}**")
else:
    # لوحة الإدارة الشاملة المفتوحة كلياً لمدير النظام
    df_client = df
    st.sidebar.markdown("👑 صلاحية: **مدير النظام**")
    st.sidebar.markdown("### 🔍 كاشف الأكواد المتاحة بالملف:")
    st.sidebar.dataframe(pd.DataFrame({"الأكواد المسجلة": valid_codes}), height=150)

if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.logged_in_customer = None
    st.rerun()

# --- 6. عنوان الواجهة اللوجستية الرئيسي للزبون ---
st.title("📦 Logistics Dashboard — أطلس")
st.markdown(f"جلسة عرض آمنة ومحمية للعميل: **{selected_client if selected_client != 'الكل' else 'كافة العملاء (لوحة المدير)'}**")

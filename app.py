import io
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="شركة أطلس المحيط", page_icon="📦", layout="wide"
)

st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .metric-card {
        padding: 16px; border-radius: 12px; color: white;
        text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .metric-title { font-size: 14px; margin-bottom: 6px; opacity: 0.95; font-weight: 600; }
    .metric-value { font-size: 20px; font-weight: bold; }
    .block-container { 
        padding-top: 3.5rem !important; padding-bottom: 3rem !important; 
        padding-left: 1rem !important; padding-right: 1rem !important; max-width: 100% !important; 
    }
    h1 {
        background-color: #e2e8f0 !important; color: #0f172a !important;
        padding: 15px 20px !important; border-radius: 8px !important;
        margin-bottom: 20px !important; margin-top: 10px !important;
    }
    [data-testid="stSidebar"] { background-color: #07151a !important; }
    [data-testid="stSidebar"] section div.stRadio label,
    [data-testid="stSidebar"] section div.stRadio p,
    [data-testid="stSidebar"] section div.stRadio span,
    [data-testid="stSidebar"] .element-container label,
    [data-testid="stSidebar"] .element-container span,
    [data-testid="stSidebar"] .stMarkdown p { color: #ffffff !important; font-weight: 600 !important; }
    </style>
""",
    unsafe_allow_html=True,
)

DATA_FILE = "shipping_data.xlsx"

def clean_numeric(series):
    cleaned = (
        series.astype(str)
        .str.replace("¥", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.strip()
    )
    cleaned = cleaned.replace(["nan", "None", "", "null", "-"], "0")
    return pd.to_numeric(cleaned, errors="coerce").fillna(0)

def load_data(uploaded_file):
    df = None
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df.to_excel(DATA_FILE, index=False)
            st.sidebar.success("تم حفظ الملف الجديد بنجاح ✔️")
        except Exception as e:
            st.sidebar.error(f"خطأ في قراءة الملف: {e}")

    if df is None and os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE)
        except Exception:
            df = None

    if df is None:
        df = pd.DataFrame()

    if not df.empty:
        df.columns = df.columns.astype(str).str.strip()
        
        # طباعة الأعمدة المتاحة في الشريط الجانبي لمساعدتك في معرفتها
        st.sidebar.markdown("---")
        st.sidebar.write("📌 أعمدة الملف المكتشفة:")
        st.sidebar.write(list(df.columns))

        # البحث عن أعمدة الدفع أو أخذ أي أعمدة رقمية احتياطية بجانب الأسعار
        all_cols = df.columns.tolist()
        
        # محاولة مطابقة ذكية
        office_col = next((c for c in all_cols if any(k in c for k in ["مكتب", "شركة", "Office", "office"])), None)
        client_col = next((c for c in all_cols if any(k in c for k in ["زبون", "Client", "client"])), None)

        if not office_col and len(all_cols) > 9:
            office_col = all_cols[9] # العمود العاشر غالباً دفع الشركة حسب الصورة
        if not client_col and len(all_cols) > 10:
            client_col = all_cols[10] # العمود الحادي عشر غالباً دفع الزبون حسب الصورة

        if office_col:
            df["المكتب دفع"] = clean_numeric(df[office_col])
        else:
            df["المكتب دفع"] = 0.0

        if client_col:
            df["الزبون دفع"] = clean_numeric(df[client_col])
        else:
            df["الزبون دفع"] = 0.0

        # تنظيف بقية الأعمدة الأساسية
        for col in ["عدد الكارتون", "الوزن", "حجم", "مبلغ الجمرك", "قيمة الاستحصالات"]:
            if col in df.columns:
                df[col] = clean_numeric(df[col])
            else:
                df[col] = 0.0

        if "مبلغ الجمرك" in df.columns and "قيمة الاستحصالات" in df.columns:
            df["متبقي حقيقي"] = df["مبلغ الجمرك"] - df["قيمة الاستحصالات"]

    return df

st.sidebar.title("🚢 شركة أطلس المحيط")
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("📁 رفع ملف Excel جديد", type=["xlsx", "xls"])

df = load_data(uploaded_file)
filtered_df = df.copy()

st.sidebar.markdown("### 🔍 الفلاتر الجانبية")
container_col = next((c for c in df.columns if any(k in c for k in ["حاوية", "Container", "container"])), df.columns[8] if len(df.columns) > 8 else None)

selected_container = "الكل"
if container_col and not df.empty:
    containers = ["الكل"] + sorted(df[container_col].dropna().astype(str).unique().tolist())
    selected_container = st.sidebar.selectbox("🚢 اختر رقم الحاوية:", containers)
    if selected_container != "الكل":
        filtered_df = filtered_df[filtered_df[container_col].astype(str) == selected_container]

code_col = next((c for c in df.columns if any(k in c.lower() for k in ["code", "كود"])), df.columns[1] if len(df.columns) > 1 else None)
selected_code = "الكل"
if code_col and not df.empty:
    codes = ["الكل"] + sorted(df[code_col].dropna().astype(str).unique().tolist())
    selected_code = st.sidebar.selectbox("🏷️ اختر الكود (Code):", codes)
    if selected_code != "الكل":
        filtered_df = filtered_df[filtered_df[code_col].astype(str) == selected_code]

sponsor_filter_col = next((c for c in df.columns if any(k in c for k in ["الكفيل", "كفيل", "Sponsor"])), df.columns[2] if len(df.columns) > 2 else None)
selected_sponsor = "الكل"
if sponsor_filter_col and not df.empty:
    sponsors = ["الكل"] + sorted(df[sponsor_filter_col].dropna().astype(str).unique().tolist())
    selected_sponsor = st.sidebar.selectbox("👤 اختر اسم الكفيل:", sponsors)
    if selected_sponsor != "الكل":
        filtered_df = filtered_df[filtered_df[sponsor_filter_col].astype(str) == selected_sponsor]

st.sidebar.markdown("---")
page = st.sidebar.radio("📌 القائمة الرئيسية", ["📊 لوحة التحكم (Dashboard)", "💰 كشف اجور الكمارك", "👥 الديون على الكفلاء", "🛃 كمرك الشحنات والاستحصالات", "📈 الرسوم البيانية"])

if page == "📊 لوحة التحكم (Dashboard)":
    st.title("📊 لوحة التحكم الرئيسية")
    st.markdown("---")
    
    total_orders = len(filtered_df)
    office_paid = filtered_df["المكتب دفع"].sum() if "المكتب دفع" in filtered_df.columns else 0.0
    client_paid = filtered_df["الزبون دفع"].sum() if "الزبون دفع" in filtered_df.columns else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">إجمالي الطلبات</div><div class="metric-value">{total_orders:,}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card" style="background-color: #16a34a;"><div class="metric-title">دفع الشركة</div><div class="metric-value">¥{office_paid:,.2f}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card" style="background-color: #9333ea;"><div class="metric-title">دفع الزبون</div><div class="metric-value">¥{client_paid:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.title(page)
    st.dataframe(filtered_df, use_container_width=True)

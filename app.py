import pandas as pd
import streamlit as st
import os

# --- إعداد الصفحة الأساسية والمبسطة جداً من الصفر ---
st.set_page_config(page_title="شركة أطلس للشحن", layout="wide")

st.title("📦 لوحة عرض شحنات شركة أطلس")
st.markdown("---")

# --- أداة رفع وتثبيت الملف بشكل دائم في خادم الموقع ---
st.sidebar.header("📁 إدارة قاعدة البيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف الإكسيل (.xlsx)", type=["xlsx", "xls"])

if uploaded_file is not None:
    # 🌟 ميزة التثبيت الأبدي: حفظ نسخة حقيقية داخل السيرفر لمنع الاختفاء عند إغلاق الصفحة 🌟
    try:
        with open("data.xlsx", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.sidebar.success("✅ تم حفظ وتثبيت الملف في الخادم بنجاح!")
    except Exception as e:
        st.sidebar.error(f"خطأ في الحفظ: {e}")

# قراءة الملف الثابت والمخزن داخل السيرفر تلقائياً
active_file = "data.xlsx" if os.path.exists("data.xlsx") else None

if active_file is None:
    st.warning("⚠️ الموقع جاهز ونظيف تماماً. يرجى رفع ملف الإكسيل من القائمة الجانبية ⬅️ ليتم حفظه وتثبيته وعرضه للجميع.")
else:
    try:
        # قراءة الشيت والبيانات الصافية حياً ومباشراً من الملف المخزن
        df = pd.read_excel(active_file)
        
        # تنظيف مسافات مسميات الأعمدة تلقائياً لمنع أي أخطاء
        df.columns = df.columns.str.strip()
        
        # --- عرض الإحصائيات العددية السريعة المبسطة ---
        st.subheader("📊 ملخص الشحنات الحالي")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("إجمالي عدد السطور والشحنات", f"{len(df)} شحنة")
        with col2:
            st.metric("عدد الأعمدة المكتشفة بالملف", f"{len(df.columns)} عمود")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- عرض الجدول الأم الكامل المفتوح دائماً والمثبت 100% ---
        st.subheader("📋 جدول البيانات الشامل والكامل")
        st.dataframe(df, use_container_width=True, height=550)
        
        # زر سريع وبسيط لتحميل كشف الحساب
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(label="📥 تحميل التقرير الحالي كملف (CSV)", data=csv_data, file_name="Atlas_Logistics_Report.csv", mime="text/csv")
        
    except Exception as e:
        st.error(f"❌ تعذر عرض الملف حالياً بسبب: {e}")
        st.info("💡 نصيحة للتشغيل: يرجى التأكد من رفع ملف إكسيل سليم ولا يحتوي على دمج خلايا معقد في السطر الأول.")

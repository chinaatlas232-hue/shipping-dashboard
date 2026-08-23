import streamlit as st
import pandas as pd
import io
import os

st.title("لوحة معالجة وتثبيت ملفات إكسل الشحنات")

# مسار حفظ الملف الثابت على الخادم لضمان عدم ضياعه عند إغلاق المتصفح
SAVED_FILE_PATH = "permanent_shipping_data.xlsx"

# 1. أداة رفع الملفات
uploaded_file = st.file_uploader("قم برفع نسخة جديدة من ملف الإكسل لتحديث البيانات:", type=["xlsx", "xls"])

# 2. إذا قام المستخدم برفع ملف جديد، يتم حفظه فوراً على الخادم واستبدال القديم
if uploaded_file is not None:
    with open(SAVED_FILE_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("تم رفع النسخة الجديدة وحفظها بنجاح على الخادم!")
    # إعادة تحميل الصفحة البرمجية لتحديث البيانات فوراً
    st.rerun()

# 3. التحقق من وجود ملف محفوظ مسبقاً لعرضه (سواء أغلقت الصفحة أو فتحتها)
if os.path.exists(SAVED_FILE_PATH):
    try:
        # قراءة الملف المحفوظ ثابت الأثر
        df = pd.read_excel(SAVED_FILE_PATH, header=None)
        
        st.info("📌 يتم الآن عرض البيانات المثبتة والمخزنة مسبقاً على الخادم.")
        
        # معاينة البيانات الأصلية
        st.subheader("معاينة الملف الحالي:")
        st.dataframe(df.head(15), use_container_width=True)
        
        # تنظيف وحذف الجدول السفلي (الاحتفاظ بأول 6 أسطر للملخص)
        cleaned_df = df.iloc[0:6, :]
        
        st.subheader("البيانات الحالية بعد مسح الجدول السفلي:")
        st.dataframe(cleaned_df, use_container_width=True)
        
        # تجهيز تحميل الملف النظيف للمستخدم الحالي أو أي مستخدم يفتح الرابط
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            cleaned_df.to_excel(writer, index=False, header=False, sheet_name='Summary')
        
        processed_data = output.getvalue()
        
        st.download_button(
            label="تحميل ملف الإكسل المعدل الحالي 📥",
            data=processed_data,
            file_name="cleaned_shipping_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف المثبت: {e}")
else:
    st.warning("⚠️ لا توجد بيانات مثبتة حالياً. يرجى رفع ملف إكسل للمرة الأولى لتثبيته في النظام.")

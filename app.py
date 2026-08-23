import streamlit as st
import pandas as pd
import io

st.title("لوحة معالجة وتعديل ملفات إكسل الشحنات")

# 1. تحديث أداة الرفع لتقبل ملفات الإكسل فقط
uploaded_file = st.file_uploader("قم برفع ملف الإكسل هنا", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # 2. قراءة ملف الإكسل بدون عناوين أعمدة مسبقة لتفادي مشاكل الدمج
        df = pd.read_excel(uploaded_file, header=None)
        
        st.success("تم رفع الملف بنجاح!")
        
        # 3. عرض البيانات الأصلية المرفوعة للمعاينة
        st.subheader("معاينة البيانات الأصلية:")
        st.dataframe(df.head(15), use_container_width=True)
        
        # 4. تنظيف وحذف الجدول السفلي
        # بناءً على الصورة الأولى، ملخص الشحنات يقع في الأسطر الأولى (أول 5 إلى 6 أسطر تقريباً)
        # سنقوم بالاحتفاظ بأول 6 أسطر فقط وحذف الباقي (الجدول الطويل)
        cleaned_df = df.iloc[0:6, :]
        
        st.subheader("البيانات بعد مسح صندوق الجدول السفلي:")
        st.dataframe(cleaned_df, use_container_width=True)
        
        # 5. تجهيز ملف الإكسل الجديد للتحميل
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # حفظ بدون كشاف الأسطر (index) وبدون العناوين التلقائية (header)
            cleaned_df.to_excel(writer, index=False, header=False, sheet_name='Summary')
        
        processed_data = output.getvalue()
        
        # 6. زر تحميل ملف الإكسل النظيف
        st.download_button(
            label="تحميل ملف الإكسل المعدل 📥",
            data=processed_data,
            file_name="cleaned_shipping_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
else:
    st.info("بانتظار رفع ملف إكسل لبدء عملية التنظيف والمسح.")

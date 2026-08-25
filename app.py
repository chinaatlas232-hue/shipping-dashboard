import streamlit as st
import pandas as pd

# 1. قراءة ملف البيانات أولاً (تأكد من وضع اسم ملفك الصحيح هنا)
df = pd.read_excel('your_file.xlsx') 
# أو إذا كان ملف CSV: df = pd.read_csv('your_file.csv')

# --- الشريط الجانبي والفلاتر ---
st.sidebar.title("🔍 الفلاتر الجانبية")

# 2. فلتر رقم الحاوية
container_options = ["الكل"] + list(df["رقم الحاوية"].dropna().unique())
selected_container = st.sidebar.selectbox("🚢 اختر رقم الحاوية:", container_options)

# 3. فلتر الكود (المدمج)
code_options = ["الكل"] + list(df["code"].dropna().unique())
selected_code = st.sidebar.selectbox("🏷️ اختر الكود (Code):", code_options)


# --- تطبيق الفلاتر على البيانات ---
filtered_df = df.copy()

if selected_container != "الكل":
    filtered_df = filtered_df[filtered_df["رقم الحاوية"] == selected_container]

if selected_code != "الكل":
    filtered_df = filtered_df[filtered_df["code"] == selected_code]


# --- الحسابات والواجهات ---
total_orders = len(filtered_df)
total_cartons = filtered_df["عدد الكارتون"].sum()
total_weight = filtered_df["الوزن"].sum()
total_volume = filtered_df["حجم"].sum()
total_company_pay = filtered_df["المجموع"].sum() 
total_customer_pay = filtered_df["الزبون دفع"].sum()

# باقي كود الواجهة والجدول الخاص بك...

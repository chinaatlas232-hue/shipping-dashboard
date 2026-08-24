import os
import pandas as pd
import streamlit as st

# اسم الملف الثابت الذي سيتم حفظ البيانات فيه على السيرفر
DATA_FILE = "shipping_data.xlsx"


# --- دالة تحميل البيانات وحفظها دائماً ---
def load_data(uploaded_file):
  # 1. إذا قام المستخدم برفع ملف جديد، احفظه على السيرفر مكان الملف القديم
  if uploaded_file is not None:
    with open(DATA_FILE, "wb") as f:
      f.write(uploaded_file.getbuffer())
    st.sidebar.success("تم حفظ الملف الجديد بنجاح ✔️")

  # 2. قراءة الملف من السيرفر إذا كان موجوداً
  if os.path.exists(DATA_FILE):
    try:
      df = pd.read_excel(DATA_FILE)
    except Exception as e:
      st.error(f"حدث خطأ أثناء قراءة الملف المحفوظ: {e}")
      df = None
  else:
    df = None

  # 3. إذا لم يوجد ملف محلي أو مرفوع، استخدم البيانات الافتراضية
  if df is None:
    df = pd.DataFrame({
        "No": [972, 994, 996, 998, 1020],
        "code": ["SM165", "SM165", "SM165", "SM170", "SM170"],
        "Shipping mark": [
            "SM165-B07",
            "SM165-B03",
            "SM165-B05",
            "SM170-B01",
            "SM170-B02",
        ],
        "رقم دخول المخزن": ["RS2601", "RS2602", "RS2603", "RS2604", "RS2605"],
        "المكتب دفع": [25934.0, 13500.0, 9036.0, 12000.0, 5000.0],
        "Client Paid": [500.0, 300.0, 200.0, 150.0, 200.0],
        "نوع البضاعة": [
            "Lady Trousers",
            "White shirt",
            "Skirt",
            "Top",
            "Coat",
        ],
        "عدد الكارتون": [8, 3, 3, 5, 4],
        "الوزن": [364, 126, 150, 200, 180],
        "حجم": [1.255, 0.527, 0.492, 0.800, 0.600],
        "رقم الفاتورة": ["INV-01", "INV-02", "INV-03", "INV-04", "INV-05"],
        "رقم الحاويات": ["RQ6044", "RQ6044", "RQ6045", "RQ6045", "RQ6046"],
    })

  # تنظيف أسماء الأعمدة والأرقام
  df.columns = df.columns.astype(str).str.strip()
  numeric_cols = [
      "المكتب دفع",
      "Client Paid",
      "عدد الكارتون",
      "الوزن",
      "حجم",
  ]
  for col in numeric_cols:
    if col in df.columns:
      df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

  return df


# في الشريط الجانبي
uploaded_file = st.sidebar.file_uploader(
    "📁 رفع ملف Excel جديد (سيتم حفظه بصفة دائمة)",
    type=["xlsx", "xls"],
)

# قراءة البيانات المحدثة
df = load_data(uploaded_file)

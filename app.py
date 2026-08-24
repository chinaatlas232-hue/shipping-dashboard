# --- دالة تحميل البيانات المحدثة ---
@st.cache_data
def load_data(file):
  if file is not None:
    try:
      df = pd.read_excel(file)
      # إزالة المسافات الزائدة من أسماء الأعمدة تلقائياً
      df.columns = df.columns.str.strip()
      return df
    except Exception as e:
      st.error(f"حدث خطأ أثناء قراءة الملف المرفوع: {e}")

  try:
    df = pd.read_excel("shipping_data.xlsx")
    df.columns = df.columns.str.strip()
    return df
  except FileNotFoundError:
    # البيانات الافتراضية
    return pd.DataFrame({
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
        "نوع البضاعة": ["Lady Trousers", "White shirt", "Skirt", "Top", "Coat"],
        "عدد الكارتون": [8, 3, 3, 5, 4],
        "الوزن": [364, 126, 150, 200, 180],
        "حجم": [1.255, 0.527, 0.492, 0.800, 0.600],
        "رقم الفاتورة": ["INV-01", "INV-02", "INV-03", "INV-04", "INV-05"],
        "رقم الحاويات": ["RQ6044", "RQ6044", "RQ6045", "RQ6045", "RQ6046"],
    })


df = load_data(uploaded_file)

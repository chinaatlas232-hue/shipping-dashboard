# 2. تحميل البيانات وتصحيح قراءة الأعمدة بدقة
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
        df = pd.DataFrame(columns=[
            "No", "code", "Shipping mark", "رقم دخول المخزن", "نوع البظاعة",
            "عدد الكارتون", "الوزن", "حجم", "رقم الحاوية", "Staff", "المجموع",
            "الزبون دفع", "المكتب دفع", "مبلغ الجمرك", "قيمة الاستحصالات", "الكفيل"
        ])

    # تنظيف أسماء الأعمدة لإزالة المسافات الزائدة
    df.columns = df.columns.astype(str).str.strip()

    # التأكد من مطابقة أسماء أعمدة الدفع تماماً لما هو موجود في ملفك
    if "الزبون دفع" not in df.columns:
        for col in df.columns:
            if "زبون" in col and "دفع" in col:
                df["الزبون دفع"] = df[col]
                break

    if "المكتب دفع" not in df.columns:
        for col in df.columns:
            if "مكتب" in col and "دفع" in col:
                df["المكتب دفع"] = df[col]
                break

    # ضبط متغيرات المتابعة باللغة الإنجليزية إن لزم الأمر
    df["Client Paid"] = df["الزبون دفع"] if "الزبون دفع" in df.columns else 0
    df["Office Paid"] = df["المكتب دفع"] if "المكتب دفع" in df.columns else 0

    numeric_cols = [
        "المكتب دفع", "Office Paid", "الزبون دفع", "Client Paid",
        "عدد الكارتون", "الوزن", "حجم", "المجموع", "مبلغ الجمرك", "قيمة الاستحصالات"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = clean_numeric(df[col])

    if "مبلغ الجمرك" in df.columns and "قيمة الاستحصالات" in df.columns:
        df["متبقي حقيقي"] = df["مبلغ الجمرك"] - df["قيمة الاستحصالات"]

    return df

# --- تحضير الأكواد لتسريع الأداء (توضع قبل شريط البحث) ---
@st.cache_data
def get_search_codes(dataframe):
    if "code" in dataframe.columns:
        # تحويل الأكواد لنصوص سريعة البحث وإزالة التكرار
        return sorted(dataframe["code"].dropna().astype(str).unique().tolist())
    return []


# جلب قائمة الأكواد من جدول البيانات الخاص بك (تأكد من اسم df)
code_options = get_search_codes(df)

# --- شريط البحث القائمة المنسدلة (في نفس مكان شريطك القديم) ---
search_query = st.multiselect(
    "🔍 بحث سريع في كافة الأعمدة (إخفاء باقي البيانات غير المطابقة):",
    options=code_options,
    default=[],
    placeholder="اختر أو اكتب الكود للبحث...",
)

# --- تصفية الجدول بناءً على خيارات القائمة ---
if search_query:
    # فلترة الجدول بناءً على الأكواد المختارة من القائمة
    filtered_df = df[df["code"].astype(str).isin(search_query)]
else:
    # عرض الجدول كاملاً عند عدم اختيار شيء
    filtered_df = df

# عرض جدول البيانات بنفس متغيرك الأصلي
st.dataframe(filtered_df, use_container_width=True)

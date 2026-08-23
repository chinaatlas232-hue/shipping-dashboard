import streamlit as st

# تضمين مكتبة Font Awesome للحصول على الأيقونات (الرموز الداخلية لرموز الأموال، الوزن، الحجم)
st.markdown(
    '<link rel="stylesheet" href="https://cloudflare.com">',
    unsafe_allow_html=True
)

# دالة مخصصة لإنشاء البطاقات الملونة مع الأيقونات والنصوص الفرعية
def create_kpi_card(bg_color, icon_class, title, value, sub_text):
    card_html = f"""
    <div style="
        background-color: {bg_color}; 
        padding: 20px; 
        border-radius: 12px; 
        color: white; 
        font-family: sans-serif;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 14px; font-weight: 500;">{title}</span>
            <i class="{icon_class}" style="font-size: 24px; opacity: 0.9;"></i>
        </div>
        <div style="font-size: 28px; font-weight: bold; margin-bottom: 5px;">{value}</div>
        <div style="font-size: 12px; opacity: 0.8;">{sub_text}</div>
    </div>
    """
    return st.markdown(card_html, unsafe_allow_html=True)

# إنشاء 6 أعمدة متطابقة مع التصميم المعروض في الصورة
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    create_kpi_card(
        bg_color="#6366f1",         # لون بنفسجي مزرق
        icon_class="fa-solid fa-money-bill-wave", # أيقونة الأموال/المبيعات
        title="سعر المبيعات - Total Sales",
        value="3,211.2",
        sub_text="4 line items"
    )

with col2:
    create_kpi_card(
        bg_color="#10b981",         # لون أخضر
        icon_class="fa-solid fa-circle-check", # أيقونة التحقق/المحصلات
        title="المحصلات - Collected",
        value="0.0",
        sub_text="Collection rate 0%"
    )

with col3:
    create_kpi_card(
        bg_color="#ef4444",         # لون أحمر
        icon_class="fa-solid fa-hourglass-half", # أيقونة المتبقي
        title="المتبقي - Remaining",
        value="3,211.2",
        sub_text="Outstanding balance"
    )

with col4:
    create_kpi_card(
        bg_color="#06b6d4",         # لون أزرق فاتح (Cyan)
        icon_class="fa-solid fa-weight-hanging", # أيقونة الوزن
        title="الوزن - Total Weight",
        value="356.8 kg",
        sub_text="Avg 89.2 kg/item"
    )

with col5:
    create_kpi_card(
        bg_color="#f59e0b",         # لون برتقالي
        icon_class="fa-solid fa-box", # أيقونة الكرتونة/الحجم
        title="Cartons - CTN",
        value="7",
        sub_text="2 shipments"
    )

with col6:
    create_kpi_card(
        bg_color="#8b5cf6",         # لون بنفسجي فاتح
        icon_class="fa-solid fa-barcode", # أيقونة الكود/الباركود
        title="الكود - SKUs",
        value="4",
        sub_text="0 rows filtered out"
    )

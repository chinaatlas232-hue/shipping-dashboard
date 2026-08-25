st.markdown("""
    <style>
    /* اللون الأساسي للتطبيق كما كان */
    .main { background-color: #0e1117; }
    
    .metric-card {
        padding: 16px; border-radius: 12px; color: white;
        text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .metric-title { font-size: 14px; margin-bottom: 6px; opacity: 0.95; font-weight: 600; }
    .metric-value { font-size: 20px; font-weight: bold; }
    
    /* زيادة المسافة العلوية لمنع اقتطاع العناوين */
    .block-container { 
        padding-top: 3.5rem !important; 
        padding-bottom: 3rem !important; 
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
        max-width: 100% !important; 
    }

    /* تخصيص هيدر الصفحة (العنوان الرئيسي) بخلفية رصاصي فاتح وهوامش مناسبة */
    h1 {
        background-color: #e2e8f0 !important;
        color: #0f172a !important;
        padding: 15px 20px !important;
        border-radius: 8px !important;
        margin-bottom: 20px !important;
        margin-top: 10px !important;
    }

    [data-testid="stTextInput"] label {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #1f2937 !important;
    }

    [data-testid="stDataFrame"] {
        margin-bottom: 35px !important;
        width: 100% !important;
    }
    
    /* تغيير لون الشريط الجانبي فقط إلى رصاي طوخ (Deep Slate / Dark Petrol) مع الحفاظ على النصوص بيضاء */
    [data-testid="stSidebar"] {
        background-color: #07151a !important;
    }
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {
        color: #f1f5f9 !important;
    }
    
    ::-webkit-scrollbar {
        width: 10px !important;
        height: 10px !important;
    }
    ::-webkit-scrollbar-track {
        background: #f1f5f9 !important;
        border-radius: 5px !important;
        margin: 5px !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #f87171 !important;
        border-radius: 4px !important;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #ef4444 !important;
    }
    </style>
""", unsafe_allow_html=True)

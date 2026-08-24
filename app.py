st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    
    /* بطاقات الإحصائيات */
    .metric-card {
        padding: 16px; border-radius: 12px; color: white;
        text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .metric-title { font-size: 14px; margin-bottom: 6px; opacity: 0.95; font-weight: 600; }
    .metric-value { font-size: 20px; font-weight: bold; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem; max-width: 99% !important; }

    [data-testid="stTextInput"] label {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #1f2937 !important;
    }

    /* مربع رفع الملفات باللون الأزرق الفاتح */
    [data-testid="stFileUploader"] {
        background-color: #e0f2fe !important;
        border: 2px dashed #38bdf8 !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }

    /* 🔹 قائمة اختيار رقم الحاوية باللون الأزرق الفاتح 🔹 */
    [data-testid="stSelectbox"] > div > div {
        background-color: #e0f2fe !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 8px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

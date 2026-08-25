# 1. تحديث تنسيق CSS ليعمل التمرير الأفقي والرأسي بشكل ممتاز
st.markdown(
    """
    <style>
    .custom-table-container {
        width: 100%;
        max-height: 700px;
        overflow-x: auto !important; /* تفعيل التمرير الأفقي لجميع الأعمدة */
        overflow-y: auto !important;
        border: 1px solid #444;
        border-radius: 8px;
    }
    .custom-table {
        width: max-content !important; /* منع ضغط الأعمدة وتوفير مساحة لكل عمود */
        min-width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        font-size: 13px;
        direction: rtl;
    }
    .custom-table th {
        background-color: #ff0000 !important;
        color: #ffffff !important;
        position: sticky;
        top: 0;
        padding: 10px 14px;
        text-align: center;
        border: 1px solid #dc2626;
        z-index: 10;
        white-space: nowrap; /* منع التفاف عناوين الأعمدة */
    }
    .custom-table td {
        padding: 8px 12px;
        text-align: center;
        border: 1px solid #333;
        color: #ffffff !important; /* الكتابة باللون الأبيض النص الناصع */
        background-color: #1e293b;
        white-space: nowrap; /* إظهار محتوى الخلايا كاملاً دون اقتطاع */
    }
    .custom-table tr:nth-child(even) td {
        background-color: #0f172a;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 2. دالة عرض الجدول لضمان ترتيب وعرض كافة أعمدة ملف الـ Excel الأصلية
def render_red_header_table(data_df):
  # عرض كافة الأعمدة الموجودة في DataFrame دون حذف
  html_table = (
      '<div class="custom-table-container"><table class="custom-table"><thead><tr>'
  )
  for col in data_df.columns:
    html_table += f"<th>{col}</th>"
  html_table += "</tr></thead><tbody>"

  for _, row in data_df.iterrows():
    html_table += "<tr>"
    for val in row:
      # استبدال nan بنص فارغ للتنسيق
      val_str = "" if pd.isna(val) else str(val)
      html_table += f"<td>{val_str}</td>"
    html_table += "</tr>"
  html_table += "</tbody></table></div>"

  st.markdown(html_table, unsafe_allow_html=True)

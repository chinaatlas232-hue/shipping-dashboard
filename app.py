# دالة العرض المصلحة بالكامل (استبدل هذه الدالة في كودك)
def render_formatted_dataframe(df_to_render, height=700):
  # 1. إعداد التنسيق التلقائي للأرقام ورمز العملة بدون تعديل القيم الأصلية
  col_config = {}

  for col in df_to_render.columns:
    if col == "عدد الكارتون":
      col_config[col] = st.column_config.NumberColumn(format="%d")
    elif col in [
        "المجموع",
        "الزبون دفع",
        "المكتب دفع",
        "Client Paid",
        "Office Paid",
        "مبلغ الجمرك",
        "قيمة الاستحصالات",
        "متبقي حقيقي",
    ]:
      col_config[col] = st.column_config.NumberColumn(format="¥%.2f")
    elif col in ["الوزن", "حجم"]:
      col_config[col] = st.column_config.NumberColumn(format="%.2f")

  # 2. تطبيق الألوان خلف النص فقط دون تغيير أو مسح القيم
  def style_columns(data):
    styles = pd.DataFrame("", index=data.index, columns=data.columns)

    # خلفية وردية مخصصة لأعمدة المبالغ المالية
    chinese_style = (
        "background-color: #ffe4e6 !important; color: #9f1239 !important;"
        " font-weight: bold;"
    )
    for target_col in [
        "المجموع",
        "الزبون دفع",
        "المكتب دفع",
        "Client Paid",
        "Office Paid",
    ]:
      if target_col in data.columns:
        styles[target_col] = chinese_style

    if "code" in data.columns:
      styles["code"] = (
          "background-color: #fef9c3 !important; color: #854d0e !important;"
          " font-weight: bold;"
      )

    if "حجم" in data.columns:
      styles["حجم"] = (
          "background-color: #fef2f2 !important; color: #dc2626 !important;"
          " font-weight: bold;"
      )

    return styles

  # 3. عرض الجدول
  st.dataframe(
      df_to_render.style.apply(style_columns, axis=None),
      column_config=col_config,
      use_container_width=True,
      height=height,
  )

st.markdown("---")
st.subheader(f"📊 جدول التفاصيل المصفى للكود الحالي: {selected_code}")

csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download as CSV",
    data=csv,
    file_name=f"{selected_code}_details.csv",
    mime="text/csv",
)


# دالة التنسيق بأسلوب الخلية (مباشرة وواضحة)
def style_container_col(val):
  return "background-color: #fca5a5; color: #7f1d1d; font-weight: bold;"


# تحديد اسم العمود الموجود في البيانات
container_col_name = (
    "رقم الحاوية"
    if "رقم الحاوية" in filtered_df.columns
    else ("رقم الحاويات" if "رقم الحاويات" in filtered_df.columns else None)
)

if container_col_name:
  styled_df = filtered_df.style.map(
      style_container_col, subset=[container_col_name]
  )
  st.dataframe(styled_df, use_container_width=True, height=650)
else:
  st.dataframe(filtered_df, use_container_width=True, height=650)

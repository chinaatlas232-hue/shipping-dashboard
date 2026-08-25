if pivot_code_col and pivot_container_col and pivot_value_col:
            # استخدام البيانات الأصلية (df) بدلاً من الفلاتر الجانبية لضمان ظهور جميع الحاويات في الجدول
            base_pivot_df = df.copy()
            
            # تطبيق فلتر الكود أو الكفيل الحالي إذا تم اختياره من القائمة الجانبية لتحديد القيمة، أو تركها شاملة
            if selected_code != "الكل":
                base_pivot_df = base_pivot_df[base_pivot_df[pivot_code_col].astype(str) == selected_code]
            if selected_sponsor != "الكل" and "الكفيل" in base_pivot_df.columns:
                base_pivot_df = base_pivot_df[base_pivot_df["الكفيل"].astype(str) == selected_sponsor]

            main_pivot = base_pivot_df.pivot_table(index=pivot_code_col, columns=pivot_container_col, values=pivot_value_col, aggfunc="sum", fill_value=0)
            
            # التأكد من عدم اختفاء الأعمدة إذا كانت النتائج فارغة
            if not main_pivot.empty:
                main_pivot["Grand Total"] = main_pivot.sum(axis=1)
                main_pivot.loc["Grand Total"] = main_pivot.sum(axis=0)

                formatted_pivot = main_pivot.map(lambda val: f"${val:,.0f}" if val > 0 else "")
                
                def style_pivot_cells(row):
                    styles = []
                    for val in row:
                        if val == "" or val == "$0":
                            styles.append('background-color: #f8fafc; color: #cbd5e1;')
                        else:
                            styles.append('background-color: #fce7f3; color: #000000; font-weight: bold;')
                    return styles

                styled_matrix = formatted_pivot.style.apply(style_pivot_cells, axis=1)
                matrix_height = max(300, min(len(main_pivot) * 35 + 50, 1200))
                st.dataframe(styled_matrix, use_container_width=True, height=matrix_height)
            else:
                st.warning("لا توجد بيانات مطابقة لهذا الاختيار.")
        else:
            st.warning("الأعمدة المطلوبة غير متوفرة بالكامل.")

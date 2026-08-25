elif page == "⏳ اعمار الديون للعملاء":
    st.title("⏳ اعمار الديون للعملاء (Aging Report)")
    st.markdown("---")
    st.markdown("### 📋 جدول اعمار الديون (توزيع المتبقي حسب الحاويات والأكواد)");

    aging_code_col = next((c for c in ["code", "الكود", "كود"] if c in filtered_df.columns), None)
    aging_container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in filtered_df.columns), None)
    aging_days_col = "عدد الايام" if "عدد الايام" in filtered_df.columns else None

    if aging_code_col and aging_container_col and "متبقي حقيقي" in filtered_df.columns:
        base_aging_df = filtered_df.copy()

        # استخراج كافة أعمدة الأيام أو الحاويات الفرعية لتكون أعمدة الجدول (Column Labels)
        pivot_col_target = aging_days_col if aging_days_col else aging_container_col
        
        # إنشاء هيكل شجري يجمع البيانات بحيث تكون الحاوية (أو الأيام) هي المستوى الأساسي وتحتوي على الأكواد
        tree_aging_rows = []
        
        # حساب المجموع الكلي لكل عمود
        all_col_values = sorted(base_aging_df[pivot_col_target].dropna().unique().tolist())
        
        # تجميع البيانات حسب الحاوية الرئيسية (أو الأيام) ثم الكود الفرعي
        grouped_containers = base_aging_df.groupby(aging_container_col, dropna=False)

        grand_totals_dict = {col: 0.0 for col in all_col_values}
        grand_total_sum = 0.0

        for container_val, container_group in grouped_containers:
            container_str = str(container_val).strip() if pd.notna(container_val) else "غير محدد"
            
            # حساب مجاميع صف الحاوية الرئيسية لكل عمود
            container_col_sums = {}
            container_total = 0.0
            for col in all_col_values:
                sub_val = container_group[container_group[pivot_col_target] == col]["متبقي حقيقي"].sum()
                container_col_sums[col] = sub_val
                container_total += sub_val
                grand_totals_dict[col] += sub_val
                grand_total_sum += sub_val

            # صف الأب الرئيسي (الحاوية مع رمز الإغلاق/التوسيع ➕)
            parent_row = {
                "Row Labels": f"➕ الحاوية: {container_str}",
                "is_parent": True
            }
            for col in all_col_values:
                parent_row[str(col)] = container_col_sums[col]
            parent_row["Grand Total"] = container_total
            tree_aging_rows.append(parent_row)

            # صفوف الأبناء (الأكواد التابعة لهذه الحاوية)
            for code_val, code_group in container_group.groupby(aging_code_col, dropna=False):
                code_str = str(code_val).strip() if pd.notna(code_val) else ""
                code_col_sums = {}
                code_total = 0.0
                for col in all_col_values:
                    c_val = code_group[code_group[pivot_col_target] == col]["متبقي حقيقي"].sum()
                    code_col_sums[col] = c_val
                    code_total += c_val

                child_row = {
                    "Row Labels": f"    ↳ {code_str}",
                    "is_parent": False
                }
                for col in all_col_values:
                    child_row[str(col)] = code_col_sums[col]
                child_row["Grand Total"] = code_total
                tree_aging_rows.append(child_row)

        # إضافة صف المجموع الكلي (Grand Total)
        grand_row = {
            "Row Labels": "Grand Total",
            "is_parent": False
        }
        for col in all_col_values:
            grand_row[str(col)] = grand_totals_dict[col]
        grand_row["Grand Total"] = grand_total_sum
        tree_aging_rows.append(grand_row)

        aging_display_df = pd.DataFrame(tree_aging_rows)
        
        # إعادة ترتيب الأعمدة لتكون Row Labels أولاً ثم الأعمدة الفرعية ثم Grand Total
        cols_order = ["Row Labels"] + [str(c) for c in all_col_values] + ["Grand Total"]
        aging_display_df = aging_display_df[[c for c in cols_order if c in aging_display_df.columns]]

        # حفظ مؤشر الأبناء والآباء للتنسيق
        is_parent_list = aging_display_df["is_parent"].tolist()
        matrix_df = aging_display_df.drop(columns=["is_parent"])

        # تنسيق القيم المالية (عرض القيمة إذا كانت أكبر من صفر، وإلا ترك الخلية فارغة تماماً نظيفة مثل إكسل)
        formatted_matrix = matrix_df.copy()
        for col in formatted_matrix.columns:
            if col != "Row Labels":
                formatted_matrix[col] = formatted_matrix[col].apply(
                    lambda val: f"${val:,.0f}" if isinstance(val, (int, float)) and val > 0 else ""
                )

        def style_aging_tree(row):
            idx = row.name
            label = str(row["Row Labels"])
            
            if label == "Grand Total":
                return ['background-color: #f1f5f9; color: #000000; font-weight: bold;'] * len(row)
            elif is_parent_list[idx]:
                # لون مميز لصفوف الحاويات الرئيسية المغلقة (الأب)
                return ['background-color: #e2e8f0; color: #0f172a; font-weight: bold;'] * len(row)
            else:
                # صفوف الأكواد الفرعية (الأبناء)
                return ['background-color: #ffffff; color: #1e293b;'] * len(row)

        styled_aging_matrix = formatted_matrix.style.apply(style_aging_tree, axis=1)

        render_download_buttons(matrix_df)

        aging_height = max(300, min(len(formatted_matrix) * 35 + 50, 1200))
        st.dataframe(styled_aging_matrix, use_container_width=True, height=aging_height)
    else:
        st.warning("الأعمدة المطلوبة (الكود، رقم الحاوية، أو المتبقي الحقيقي) غير متوفرة بالكامل في البيانات الحالية.")

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

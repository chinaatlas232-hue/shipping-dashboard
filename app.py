elif page == "aging":
    st.title("⏳ تقرير أعمار الديون (Aging Report)")
    st.markdown("---")
    st.markdown("### 📋 جدول تحليلي يوزع المتبقي الحقيقي حسب الكود ورقم الحاوية وأيام التأخير")

    aging_df = filtered_df.copy()
    code_field = next((c for c in ["code", "الكود", "كود"] if c in aging_df.columns), None)
    
    if not aging_df.empty and "رقم الحاوية" in aging_df.columns and "عدد الايام" in aging_df.columns and "متبقي حقيقي" in aging_df.columns:
        
        # تحويل عمود عدد الأيام إلى أرقام صحيحة لإزالة الأصفار والكسور العشرية
        aging_df["عدد الايام"] = pd.to_numeric(aging_df["عدد الايام"], errors="coerce").fillna(0).astype(int)
        
        index_cols = [code_field, "رقم الحاوية"] if code_field else ["رقم الحاوية"]
        
        aging_pivot = aging_df.pivot_table(
            index=index_cols,
            columns="عدد الايام",
            values="متبقي حقيقي",
            aggfunc="sum",
            fill_value=0
        )

        aging_pivot["Grand Total"] = aging_pivot.sum(axis=1)
        aging_grand_total = aging_pivot.sum(axis=0)
        
        if code_field:
            aging_pivot.loc[("Grand Total", "")] = aging_grand_total
        else:
            aging_pivot.loc["Grand Total"] = aging_grand_total

        formatted_aging = aging_pivot.copy()
        for col in formatted_aging.columns:
            formatted_aging[col] = formatted_aging[col].apply(
                lambda val: f"${val:,.0f}" if isinstance(val, (int, float)) and val > 0 else ("$0" if val == 0 else ("" if isinstance(val, (int, float)) else val))
            )

        def style_aging_cells(row):
            styles = []
            is_total_row = False
            
            # التحقق إذا كان السطر الحالي هو صف المجموع الكلي
            idx_val = row.name
            if idx_val == "Grand Total" or (isinstance(idx_val, tuple) and idx_val[0] == "Grand Total"):
                is_total_row = True
                
            for val in row:
                if is_total_row:
                    styles.append('background-color: #e2e8f0; color: #0f172a; font-weight: bold; text-align: center;')
                elif val == "" or val == "$0":
                    styles.append('background-color: #f8fafc; color: #cbd5e1; text-align: center;')
                else:
                    styles.append('background-color: #ffffff; color: #000000; font-weight: bold; text-align: center;')
            return styles

        styled_aging_matrix = formatted_aging.style.apply(style_aging_cells, axis=1)
        render_download_buttons(aging_pivot.reset_index())
        
        aging_height = max(300, min(len(aging_pivot) * 35 + 50, 1200))
        st.markdown(styled_aging_matrix.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.warning("عذراً، الأعمدة الأساسية المطلوبة غير متوفرة بالكامل في البيانات الحالية.")

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

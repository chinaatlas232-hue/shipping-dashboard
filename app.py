elif page == "sponsors":
    st.title("👥 الديون على الكفلاء")
    st.markdown("---")
    
    if "الكفيل" in filtered_df.columns and not filtered_df.empty:
        col_customs = "مبلغ الجمرك" if "مبلغ الجمرك" in filtered_df.columns else filtered_df.columns[0]
        col_collected = "قيمة الاستحصالات" if "قيمة الاستحصالات" in filtered_df.columns else filtered_df.columns[0]
        col_remaining = "متبقي حقيقي" if "متبقي حقيقي" in filtered_df.columns else filtered_df.columns[0]
        col_count = "No" if "No" in filtered_df.columns else filtered_df.columns[0]

        sponsor_summary = filtered_df.groupby("الكفيل").agg(
            total_customs=(col_customs, "sum"),
            total_collected=(col_collected, "sum"),
            total_remaining=(col_remaining, "sum"),
            total_orders=(col_count, "count")
        ).reset_index()

        st.markdown("### 📋 ملخص المبالغ لكل كفيل")
        
        for index, row in sponsor_summary.iterrows():
            sponsor_name = row["الكفيل"]
            s_customs = row["total_customs"]
            s_collected = row["total_collected"]
            s_remaining = row["total_remaining"]
            s_orders = row["total_orders"]
            
            card_bg = "#1e3a8a"
            if "لم تصل بعد" in str(sponsor_name):
                card_bg = "#b45309"
            
            st.markdown(f"""
                <div style="background-color: {card_bg}; padding: 15px; border-radius: 10px; color: white; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="margin: 0 0 10px 0; font-size: 18px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 5px; color: #ffffff !important;">👤 الكفيل: {sponsor_name}</h3>
                    <div style="display: flex; justify-content: space-between; font-size: 15px; text-align: center; color: #ffffff !important;">
                        <div>📦 الطلبات: <b style="color: #ffffff;">{s_orders:,}</b></div>
                        <div>💰 الجمرك: <b style="color: #ffffff;">${s_customs:,.2f}</b></div>
                        <div>✅ المسدد: <b style="color: #ffffff;">${s_collected:,.2f}</b></div>
                        <div>⏳ المتبقي: <b style="color: #ffffff;">${s_remaining:,.2f}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("### 📊 جدول تفصيلي بملخص الكفلاء (Pivot Table)")
        
        pivot_code_col = next((c for c in ["code", "الكود", "كود"] if c in filtered_df.columns), None)
        pivot_container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in filtered_df.columns), None)
        pivot_value_col = "مبلغ الجمرك" if "مبلغ الجمرك" in filtered_df.columns else None

        if pivot_code_col and pivot_container_col and pivot_value_col:
            base_pivot_df = df.copy()
            
            if selected_code != "الكل":
                base_pivot_df = base_pivot_df[base_pivot_df[pivot_code_col].astype(str) == selected_code]
            if selected_sponsor != "الكل" and "الكفيل" in base_pivot_df.columns:
                base_pivot_df = base_pivot_df[base_pivot_df["الكفيل"].astype(str) == selected_sponsor]

            pivot_table_df = base_pivot_df.pivot_table(
                index=pivot_code_col,
                columns=pivot_container_col,
                values=pivot_value_col,
                aggfunc="sum",
                fill_value=0
            )

            pivot_table_df["Grand Total"] = pivot_table_df.sum(axis=1)
            grand_total_row = pivot_table_df.sum(axis=0)
            pivot_table_df.loc["Grand Total"] = grand_total_row

            new_columns = []
            for col in pivot_table_df.columns:
                if col == "Grand Total":
                    new_columns.append(col)
                    continue
                
                sub_df = base_pivot_df[base_pivot_df[pivot_container_col].astype(str) == str(col)]
                is_not_arrived = False
                if not sub_df.empty and "الكفيل" in sub_df.columns:
                    sponsors_in_col = sub_df["الكفيل"].astype(str).unique()
                    if any("لم تصل بعد" in str(s) for s in sponsors_in_col):
                        is_not_arrived = True
                
                bg_color = "#fef08a" if is_not_arrived else "#bbf7d0"
                html_col_name = f'<div style="background-color: {bg_color}; padding: 4px 8px; border-radius: 4px; color: black; font-weight: bold; text-align: center;">{col}</div>'
                new_columns.append(html_col_name)

            pivot_table_df.columns = new_columns

            # إخفاء القيم التي تساوي صفر تماماً وجعلها نصاً فارغاً
            formatted_pivot = pivot_table_df.map(
                lambda val: f"${val:,.0f}" if isinstance(val, (int, float)) and val > 0 else ""
            )
            
            def style_pivot_cells(val):
                if val == "":
                    return 'background-color: #f8fafc; color: transparent;'
                return 'background-color: #fce7f3; color: #000000; font-weight: bold;'

            styled_matrix = formatted_pivot.style.map(style_pivot_cells)

            matrix_height = max(300, min(len(pivot_table_df) * 35 + 50, 1200))
            st.markdown(styled_matrix.to_html(escape=False), unsafe_allow_html=True)
        else:
            st.warning("الأعمدة المطلوبة لإنشاء جدول البايفت غير متوفرة بالكامل.")

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

elif page == "aging":
    st.title("⏳ تقرير أعمار الديون (Aging Report)")
    st.markdown("---")
    st.markdown("### 📋 جدول تحليلي يوزع المتبقي الحقيقي حسب الكود ورقم الحاوية وأيام التأخير")

    aging_df = filtered_df.copy()
    code_field = next((c for c in ["code", "الكود", "كود"] if c in aging_df.columns), None)
    
    if not aging_df.empty and "رقم الحاوية" in aging_df.columns and "عدد الايام" in aging_df.columns and "متبقي حقيقي" in aging_df.columns:
        
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
                lambda val: f"${val:,.0f}" if isinstance(val, (int, float)) and val > 0 else ""
            )

        def style_aging_cells(row):
            styles = []
            is_total_row = False
            idx_val = row.name
            if idx_val == "Grand Total" or (isinstance(idx_val, tuple) and idx_val[0] == "Grand Total"):
                is_total_row = True
                
            for val in row:
                if is_total_row:
                    styles.append('background-color: #e2e8f0; color: #0f172a; font-weight: bold; text-align: center;')
                elif val == "":
                    styles.append('background-color: #f8fafc; color: transparent; text-align: center;')
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

elif page == "📈 واجهة التقارير":
    st.title("📈 واجهة التقارير الشاملة حسب الكفيل")
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
            # إنشاء جدول متعدد الأبعاد أو جدول تفصيلي مطابق للأصل
            piv_customs = filtered_df.pivot_table(index=pivot_code_col, columns=pivot_container_col, values="مبلغ الجمرك", aggfunc="sum", fill_value=0)
            piv_collected = filtered_df.pivot_table(index=pivot_code_col, columns=pivot_container_col, values="قيمة الاستحصالات", aggfunc="sum", fill_value=0)
            piv_remaining = filtered_df.pivot_table(index=pivot_code_col, columns=pivot_container_col, values="متبقي حقيقي", aggfunc="sum", fill_value=0)

            # دمج الجداول بجوار بعضها تماماً مثل تصميم إكسل في الصورة
            pivot_table_df = pd.concat([piv_customs, piv_collected, piv_remaining], axis=1, keys=["مبلغ الجمرك", "قيمة الاستحصالات", "متبقي حقيقي"])
            
            # إعادة تشكيل الأعمدة لتتوافق مع العرض المدمج
            pivot_table_df.columns = [f"{col[1]}" for col in pivot_table_df.columns]
            
            # إزالة التكرار أو ضبط المجاميع الكلية
            total_row = filtered_df.groupby(pivot_code_col)[["مبلغ الجمرك", "قيمة الاستحصالات", "متبقي حقيقي"]].sum()
            
            # بناء جدول مبسط مطابق للشكل تماماً مع المجموع الكلي
            main_pivot = filtered_df.pivot_table(index=pivot_code_col, columns=pivot_container_col, values=pivot_value_col, aggfunc="sum", fill_value=0)
            main_pivot["Grand Total"] = main_pivot.sum(axis=1)
            main_pivot.loc["Grand Total"] = main_pivot.sum(axis=0)

            formatted_pivot = main_pivot.map(lambda val: f"${val:,.0f}" if val > 0 else "")
            
            def style_pivot_cells(val):
                if val == "" or val == "$0":
                    return 'background-color: #f8fafc; color: #cbd5e1;'
                return 'background-color: #fce7f3; color: #000000; font-weight: bold;'

            styled_matrix = formatted_pivot.style.map(style_pivot_cells)
            
            styled_matrix = styled_matrix.set_table_styles([
                {'selector': 'th.row_heading', 'props': [('color', '#000000'), ('font-weight', 'bold'), ('background-color': '#f1f5f9')]},
                {'selector': 'th.col_heading', 'props': [('color', '#000000'), ('font-weight', 'bold'), ('background-color': '#f1f5f9')]},
                {'selector': 'td', 'props': [('color', '#000000'), ('text-align', 'center')]}
            ], overwrite=False)
            
            matrix_height = max(300, min(len(main_pivot) * 35 + 50, 1200))
            st.dataframe(styled_matrix, use_container_width=True, height=matrix_height)
        else:
            st.warning("الأعمدة المطلوبة غير متوفرة بالكامل.")
            summary_height = max(300, min(len(sponsor_summary) * 35 + 50, 1200))
            st.dataframe(sponsor_summary, use_container_width=True, height=summary_height)
    else:
        st.warning("لا توجد بيانات متاحة لعرض التقارير حالياً.")
    
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

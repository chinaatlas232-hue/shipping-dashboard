import io
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Logistics Admin Dashboard", page_icon="📦", layout="wide"
)

# تنسيق الخط وحجمه (16px + Bold)
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem; max-width: 99% !important; }
    
    [data-testid="stDataFrame"] div[role="grid"] { 
        font-size: 16px !important; 
        font-weight: bold !important;
    }
    [data-testid="stDataFrame"] div[role="row"] { 
        min-height: 48px !important; 
    }
    </style>
""",
    unsafe_allow_html=True,
)

DATA_FILE = "shipping_data.xlsx"


def clean_numeric(series):
  return (
      pd.to_numeric(
          series.astype(str)
          .str.replace("¥", "", regex=False)
          .str.replace("$", "", regex=False)
          .str.replace(",", "", regex=False)
          .str.strip(),
          errors="coerce",
      )
      .fillna(0)
  )


def load_data():
  if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
  else:
    df = pd.DataFrame()

  df.columns = df.columns.astype(str).str.strip()

  for col in ["مبلغ الجمرك", "قيمة الاستحصالات"]:
    if col in df.columns:
      df[col] = clean_numeric(df[col])
    else:
      df[col] = 0.0

  df["متبقي حقيقي"] = df["مبلغ الجمرك"] - df["قيمة الاستحصالات"]
  return df


df = load_data()

st.title("💰 كشف الحساب التجميعي (Pivot Report)")
st.markdown("---")

search_code = st.text_input(
    "🔍 حصراً لتصفية الجدول (Code) ابحث عن كود الزبون:", ""
)

filtered_df = df.copy()

if search_query := search_code.strip():
  if "code" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["code"]
        .astype(str)
        .str.contains(search_query, case=False, na=False)
    ]

tree_rows = []

if not filtered_df.empty:
  grand_customs = filtered_df["مبلغ الجمرك"].sum()
  grand_collections = filtered_df["قيمة الاستحصالات"].sum()
  grand_remaining = filtered_df["متبقي حقيقي"].sum()

  # التحقق من اسم عمود الحاويات
  container_col = next(
      (c for c in ["رقم الحاوية", "رقم الحاويات"] if c in filtered_df.columns),
      None,
  )
  sponsor_col = "الكفيل" if "الكفيل" in filtered_df.columns else None

  # التجميع حسب الكفيل والكود معاً لمنع التداخل بين الحاويات المختلفة
  group_cols = []
  if sponsor_col:
    group_cols.append(sponsor_col)
  if "code" in filtered_df.columns:
    group_cols.append("code")

  if group_cols:
    grouped_parents = filtered_df.groupby(group_cols, dropna=False)

    for group_keys, parent_group in grouped_parents:
      # تحديد المسمى رئيسي
      if isinstance(group_keys, tuple):
        s_val, c_val = group_keys[0], group_keys[1]
        label_text = f"➖ {c_val} (الكفيل: {s_val})" if pd.notna(s_val) else f"➖ {c_val}"
      else:
        label_text = f"➖ {group_keys}"

      sum_customs = parent_group["مبلغ الجمرك"].sum()
      sum_collections = parent_group["قيمة الاستحصالات"].sum()
      sum_remaining = parent_group["متبقي حقيقي"].sum()

      # إضافة الصف الرئيسي للزبون/الكفيل
      tree_rows.append({
          "Row Labels": label_text,
          "Sum of مبلغ الجمرك": f"${sum_customs:,.2f}",
          "Sum of قيمة الاستحصالات": f"${sum_collections:,.2f}",
          "Sum of متبقي حقيقي": f"${sum_remaining:,.0f}",
      })

      # إضافة صفوف الحاويات التابعة لهذا الكفيل فقط
      if container_col:
        for container, c_group in parent_group.groupby(
            container_col, dropna=False
        ):
          c_customs = c_group["مبلغ الجمرك"].sum()
          c_collections = c_group["قيمة الاستحصالات"].sum()
          c_remaining = c_group["متبقي حقيقي"].sum()

          tree_rows.append({
              "Row Labels": f"    ↳ {container}",
              "Sum of مبلغ الجمرك": f"${c_customs:,.2f}",
              "Sum of قيمة الاستحصالات": f"${c_collections:,.2f}",
              "Sum of متبقي حقيقي": f"${c_remaining:,.0f}",
          })

  # إضافة الإجمالي العام
  tree_rows.append({
      "Row Labels": "Grand Total",
      "Sum of مبلغ الجمرك": f"${grand_customs:,.2f}",
      "Sum of قيمة الاستحصالات": f"${grand_collections:,.2f}",
      "Sum of متبقي حقيقي": f"${grand_remaining:,.0f}",
  })

pivot_display_df = pd.DataFrame(tree_rows)

if not pivot_display_df.empty:

  def highlight_totals(row):
    label = str(row["Row Labels"])
    if label.startswith("➖") or label == "Grand Total":
      return [
          "background-color: #f1f5f9; font-weight: bold; font-size: 16px;"
          " color: #000000;"
      ] * len(row)
    return ["font-size: 16px; font-weight: bold; color: #1f2937;"] * len(row)

  styled_pivot = pivot_display_df.style.apply(highlight_totals, axis=1)
  st.dataframe(styled_pivot, use_container_width=True, height=750)
else:
  st.warning("لا توجد نتائج مطابقة لكود الزبون المدخل.")

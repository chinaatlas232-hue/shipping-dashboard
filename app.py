import io
import os
import pandas as pd
import streamlit as st

# 1. إعداد الصفحة وتنسيقات CSS
st.set_page_config(
    page_title="Logistics Admin Dashboard", page_icon="📦", layout="wide"
)

st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem; max-width: 99% !important; }
    
    .metric-card {
        padding: 16px; border-radius: 12px; color: white;
        text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .metric-title { font-size: 15px; margin-bottom: 6px; opacity: 0.95; font-weight: 600; }
    .metric-value { font-size: 22px; font-weight: bold; }

    /* تكبير خط الجدول إلى 16 وجعله بولد */
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

# 2. شريط البحث الذكي (يبحث في الكود، الكفيل، ورقم الحاوية)
search_query = st.text_input(
    "🔍 بحث ذكي (ابحث برقم الكود، اسم الكفيل، أو رقم الحاوية):", ""
).strip()

filtered_df = df.copy()

if search_query:
  search_cols = [
      c
      for c in ["code", "الكفيل", "رقم الحاوية", "رقم الحاويات"]
      if c in filtered_df.columns
  ]
  if search_cols:
    mask = filtered_df[search_cols].apply(
        lambda col: col.astype(str).str.contains(
            search_query, case=False, na=False
        )
    )
    filtered_df = filtered_df[mask.any(axis=1)]

# 3. حساب قيم المربعات التوضيحية
total_customs = (
    filtered_df["مبلغ الجمرك"].sum() if not filtered_df.empty else 0.0
)

osama_customs = 0.0
if "الكفيل" in filtered_df.columns and not filtered_df.empty:
  osama_customs = filtered_df[
      filtered_df["الكفيل"].astype(str).str.contains("اسامة|أسامة", na=False)
  ]["مبلغ الجمرك"].sum()

not_arrived_customs = 0.0
if "الكفيل" in filtered_df.columns and not filtered_df.empty:
  not_arrived_customs = filtered_df[
      filtered_df["الكفيل"].astype(str).str.contains("لم تصل بعد", na=False)
  ]["مبلغ الجمرك"].sum()

m1, m2, m3 = st.columns(3)

with m1:
  st.markdown(
      f'<div class="metric-card" style="background-color: #1e3a8a;"><div'
      ' class="metric-title">أجور الجمرك الكلي</div><div'
      f' class="metric-value">${total_customs:,.2f}</div></div>',
      unsafe_allow_html=True,
  )

with m2:
  st.markdown(
      f'<div class="metric-card" style="background-color: #0f766e;"><div'
      ' class="metric-title">أسامة</div><div'
      f' class="metric-value">${osama_customs:,.2f}</div></div>',
      unsafe_allow_html=True,
  )

with m3:
  st.markdown(
      f'<div class="metric-card" style="background-color: #dc2626;"><div'
      ' class="metric-title">لم تصل بعد</div><div'
      f' class="metric-value">${not_arrived_customs:,.2f}</div></div>',
      unsafe_allow_html=True,
  )

st.markdown("---")

# 4. بناء الجدول الشجري مع تحديد علامة "لم تصل بعد"
tree_rows = []

if not filtered_df.empty:
  grand_customs = filtered_df["مبلغ الجمرك"].sum()
  grand_collections = filtered_df["قيمة الاستحصالات"].sum()
  grand_remaining = filtered_df["متبقي حقيقي"].sum()

  container_col = next(
      (c for c in ["رقم الحاوية", "رقم الحاويات"] if c in filtered_df.columns),
      None,
  )
  sponsor_col = "الكفيل" if "الكفيل" in filtered_df.columns else None

  group_cols = []
  if sponsor_col:
    group_cols.append(sponsor_col)
  if "code" in filtered_df.columns:
    group_cols.append("code")

  if group_cols:
    grouped_parents = filtered_df.groupby(group_cols, dropna=False)

    for group_keys, parent_group in grouped_parents:
      is_not_arrived = False
      if isinstance(group_keys, tuple):
        s_val, c_val = group_keys[0], group_keys[1]
        label_text = f"➖ {c_val} (الكفيل: {s_val})" if pd.notna(s_val) else f"➖ {c_val}"
        if pd.notna(s_val) and "لم تصل بعد" in str(s_val):
          is_not_arrived = True
      else:
        label_text = f"➖ {group_keys}"
        if "لم تصل بعد" in str(group_keys):
          is_not_arrived = True

      sum_customs = parent_group["مبلغ الجمرك"].sum()
      sum_collections = parent_group["قيمة الاستحصالات"].sum()
      sum_remaining = parent_group["متبقي حقيقي"].sum()

      tree_rows.append({
          "Row Labels": label_text,
          "Sum of مبلغ الجمرك": f"${sum_customs:,.2f}",
          "Sum of قيمة الاستحصالات": f"${sum_collections:,.2f}",
          "Sum of متبقي حقيقي": f"${sum_remaining:,.0f}",
          "is_not_arrived": is_not_arrived,
      })

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
              "is_not_arrived": is_not_arrived,
          })

  tree_rows.append({
      "Row Labels": "Grand Total",
      "Sum of مبلغ الجمرك": f"${grand_customs:,.2f}",
      "Sum of قيمة الاستحصالات": f"${grand_collections:,.2f}",
      "Sum of متبقي حقيقي": f"${grand_remaining:,.0f}",
      "is_not_arrived": False,
  })

pivot_display_df = pd.DataFrame(tree_rows)

if not pivot_display_df.empty:
  # استبعاد عمود التمييز من العرض النهائي
  is_not_arrived_series = pivot_display_df["is_not_arrived"]
  display_df = pivot_display_df.drop(columns=["is_not_arrived"])

  # 5. التنسيق الشرطي لإعطاء اللون الأحمر للشحنات التي لم تصل بعد
  def apply_row_styles(row):
    idx = row.name
    label = str(row["Row Labels"])
    is_not_arr = is_not_arrived_series.loc[idx]

    if is_not_arr:
      if label.startswith("➖"):
        return [
            "background-color: #fee2e2; color: #991b1b; font-weight: bold;"
            " font-size: 16px;"
        ] * len(row)
      return [
          "background-color: #fff1f2; color: #b91c1c; font-size: 16px;"
          " font-weight: bold;"
      ] * len(row)

    if label.startswith("➖") or label == "Grand Total":
      return [
          "background-color: #f1f5f9; font-weight: bold; font-size: 16px;"
          " color: #000000;"
      ] * len(row)

    return ["font-size: 16px; font-weight: bold; color: #1f2937;"] * len(row)

  styled_pivot = display_df.style.apply(apply_row_styles, axis=1)
  st.dataframe(styled_pivot, use_container_width=True, height=750)
else:
  st.warning("لا توجد نتائج مطابقة لمفهوم البحث المدخل.")

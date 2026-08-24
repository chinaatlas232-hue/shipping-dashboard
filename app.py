import io
import os
import pandas as pd
import streamlit as st

# 1. إعداد الصفحة وتكبير الخط وتنسيقات CSS
st.set_page_config(
    page_title="Logistics Admin Dashboard", page_icon="📦", layout="wide"
)

st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem; max-width: 99% !important; }
    
    /* تكبير خط الجدول إلى 16 وجعله بولد (Bold) */
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


# 2. تحميل البيانات
def load_data():
  if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
  else:
    # بيانات افتراضية تجريبية تحوي الكفيل
    df = pd.DataFrame({
        "code": ["B4344", "B4344", "B4344"],
        "الكفيل": ["أبو فهد", "أبو فهد", "أبو فهد"],
        "رقم الحاوية": ["RQ6027", "RQ6028", "RQ6030"],
        "مبلغ الجمرك": [60.90, 163.50, 1481.40],
        "قيمة الاستحصالات": [61.00, 163.50, 1480.90],
    })

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

# 3. صندوق بحث للرمز/كود الزبون حصراً
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

# 4. بناء الجدول الشجري المحدث بإضافة الكفيل
tree_rows = []

if not filtered_df.empty and "code" in filtered_df.columns:
  grand_customs = filtered_df["مبلغ الجمرك"].sum()
  grand_collections = filtered_df["قيمة الاستحصالات"].sum()
  grand_remaining = filtered_df["متبقي حقيقي"].sum()

  # التجميع حسب الكود
  for code, code_group in filtered_df.groupby("code"):
    # استخراج اسم الكفيل إذا كان موجوداً
    sponsor_name = ""
    if "الكفيل" in code_group.columns and not code_group["الكفيل"].dropna().empty:
      sponsor_name = f" (الكفيل: {code_group['الكفيل'].iloc[0]})"

    sum_customs = code_group["مبلغ الجمرك"].sum()
    sum_collections = code_group["قيمة الاستحصالات"].sum()
    sum_remaining = code_group["متبقي حقيقي"].sum()

    # صف الزبون الرئيسي مع إظهار الكفيل
    tree_rows.append({
        "Row Labels": f"➖ {code}{sponsor_name}",
        "Sum of مبلغ الجمرك": f"${sum_customs:,.2f}",
        "Sum of قيمة الاستحصالات": f"${sum_collections:,.2f}",
        "Sum of متبقي حقيقي": f"${sum_remaining:,.0f}",
    })

    # صفوف الحاويات التفصيلية
    container_col = (
        "رقم الحاوية"
        if "رقم الحاوية" in code_group.columns
        else (
            "رقم الحاويات" if "رقم الحاويات" in code_group.columns else None
        )
    )
    if container_col:
      for container, container_group in code_group.groupby(container_col):
        c_customs = container_group["مبلغ الجمرك"].sum()
        c_collections = container_group["قيمة الاستحصالات"].sum()
        c_remaining = container_group["متبقي حقيقي"].sum()

        tree_rows.append({
            "Row Labels": f"    ↳ {container}",
            "Sum of مبلغ الجمرك": f"${c_customs:,.2f}",
            "Sum of قيمة الاستحصالات": f"${c_collections:,.2f}",
            "Sum of متبقي حقيقي": f"${c_remaining:,.0f}",
        })

  # الإجمالي العام
  tree_rows.append({
      "Row Labels": "Grand Total",
      "Sum of مبلغ الجمرك": f"${grand_customs:,.2f}",
      "Sum of قيمة الاستحصالات": f"${grand_collections:,.2f}",
      "Sum of متبقي حقيقي": f"${grand_remaining:,.0f}",
  })

# 5. عرض الجدول بالتنسيق الجديد
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

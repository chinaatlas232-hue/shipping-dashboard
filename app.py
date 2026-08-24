import io
import os
import pandas as pd
import streamlit as st

# 1. إعداد الصفحة
st.set_page_config(
    page_title="Logistics Admin Dashboard", page_icon="📦", layout="wide"
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


# 2. تحميل البيانات وتجهيز الأعمدة
def load_data():
  if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
  else:
    # بيانات افتراضية للتجربة
    df = pd.DataFrame({
        "code": [
            "أسامة",
            "أسامة",
            "أسامة",
            "أسامة",
            "لم تصل بعد",
            "لم تصل بعد",
        ],
        "رقم الحاوية": [
            "RQ6027",
            "RQ6028",
            "RQ6030",
            "RQ6036",
            "RQ6043",
            "RQ6044",
        ],
        "مبلغ الجمرك": [60.90, 163.50, 1481.40, 134.40, 3368.22, 3515.88],
        "قيمة الاستحصالات": [61.00, 163.50, 1480.90, 0.00, 0.00, 0.00],
    })

  df.columns = df.columns.astype(str).str.strip()

  # التأكد من وجود الأعمدة المطلوبة وتنظيف القيم الحسابية
  for col in ["مبلغ الجمرك", "قيمة الاستحصالات"]:
    if col in df.columns:
      df[col] = clean_numeric(df[col])
    else:
      df[col] = 0.0

  # حساب المتبقي الحقيقي لكل صف (مبلغ الجمرك - قيمة الاستحصالات)
  df["متبقي حقيقي"] = df["مبلغ الجمرك"] - df["قيمة الاستحصالات"]
  return df


df = load_data()

st.title("💰 كشف الحساب التجميعي (Pivot Report)")
st.markdown("---")

# 3. شريط بحث حصري بالرمز/كود الزبون فقط
search_code = st.text_input(
    "🔍 ابحث عن كود الزبون (Code) حصراً لتصفية الجدول:", ""
)

filtered_df = df.copy()

# تصفية البيانات بحسب الكود المدخل في صندوق البحث
if search_query := search_code.strip():
  if "code" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["code"]
        .astype(str)
        .str.contains(search_query, case=False, na=False)
    ]

# 4. بناء الجدول الشجري المتطابق مع صورة Pivot Table
tree_rows = []

if not filtered_df.empty and "code" in filtered_df.columns:
  # التجميع حسب الكود ورقم الحاوية
  grouped = filtered_df.groupby(
      ["code", "رقم الحاوية"], dropna=False
  ).sum(numeric_only=True)

  # حساب إجمالي الديون المتبقية
  grand_customs = filtered_df["مبلغ الجمرك"].sum()
  grand_collections = filtered_df["قيمة الاستحصالات"].sum()
  grand_remaining = filtered_df["متبقي حقيقي"].sum()

  # التكرار لبناء صفوف الجدول (اسم الزبون أولاً ثم الحاويات التابعة له)
  for code, code_group in filtered_df.groupby("code"):
    # صف الإجمالي الخاص بالزبون (Main Row)
    sum_customs = code_group["مبلغ الجمرك"].sum()
    sum_collections = code_group["قيمة الاستحصالات"].sum()
    sum_remaining = code_group["متبقي حقيقي"].sum()

    tree_rows.append({
        "Row Labels": f"➖ {code}",
        "Sum of مبلغ الجمرك": f"${sum_customs:,.2f}",
        "Sum of قيمة الاستحصالات": f"${sum_collections:,.2f}",
        "Sum of متبقي حقيقي": f"${sum_remaining:,.0f}",
    })

    # صفوف الحاويات التفصيلية (Sub Rows)
    for container, container_group in code_group.groupby("رقم الحاوية"):
      c_customs = container_group["مبلغ الجمرك"].sum()
      c_collections = container_group["قيمة الاستحصالات"].sum()
      c_remaining = container_group["متبقي حقيقي"].sum()

      tree_rows.append({
          "Row Labels": f"    ↳ {container}",
          "Sum of مبلغ الجمرك": f"${c_customs:,.2f}",
          "Sum of قيمة الاستحصالات": f"${c_collections:,.2f}",
          "Sum of متبقي حقيقي": f"${c_remaining:,.0f}",
      })

  # صف الإجمالي العام (Grand Total)
  tree_rows.append({
      "Row Labels": "Grand Total",
      "Sum of مبلغ الجمرك": f"${grand_customs:,.2f}",
      "Sum of قيمة الاستحصالات": f"${grand_collections:,.2f}",
      "Sum of متبقي حقيقي": f"${grand_remaining:,.0f}",
  })

# 5. عرض الجدول بتنسيق مشابه للصورة
pivot_display_df = pd.DataFrame(tree_rows)

if not pivot_display_df.empty:
  # تنسيق الخلايا العريضة والخطوط البارزة للصفوف الرئيسية
  def highlight_totals(row):
    label = str(row["Row Labels"])
    if label.startswith("➖") or label == "Grand Total":
      return [
          "background-color: #f1f5f9; font-weight: bold; color: #000000;"
      ] * len(row)
    return ["color: #1f2937;"] * len(row)

  styled_pivot = pivot_display_df.style.apply(highlight_totals, axis=1)

  st.dataframe(styled_pivot, use_container_width=True, height=750)
else:
  st.warning("لا توجد نتائج مطابقة لكود الزبون المدخل.")

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Logistics Dashboard — B12", page_icon="🚢", layout="wide")

DATA_FILE = "data.xlsx"
PLOTLY_TEMPLATE = "plotly_dark"

# ---------------------------------------------------------------- load data
@st.cache_data
def load_data(path: str) -> tuple[pd.DataFrame, dict]:
    raw = pd.read_excel(path, header=None)

    # --- header KPIs (row 1): code / orders / containers / client paid / office paid
    hdr = {
        "code": str(raw.iloc[1, 1]),
        "orders_reported": pd.to_numeric(raw.iloc[1, 3], errors="coerce"),
        "containers_reported": pd.to_numeric(raw.iloc[1, 5], errors="coerce"),
        "client_paid_reported": pd.to_numeric(raw.iloc[1, 7], errors="coerce"),
        "office_paid_reported": pd.to_numeric(raw.iloc[2, 7], errors="coerce"),
    }

    # --- table starts at row 4, ends before "Grand Total"
    tbl = raw.iloc[4:].copy()
    tbl.columns = [
        "container", "shipping_mark", "amount", "client_paid",
        "office_paid", "ctns", "cbm", "shipping_fees",
    ]
    tbl = tbl[tbl["shipping_mark"].notna()].copy()
    tbl = tbl[tbl["container"].astype(str).str.strip().str.lower() != "grand total"]
    tbl["container"] = tbl["container"].ffill().astype(str).str.strip()

    for c in ["amount", "client_paid", "office_paid", "ctns", "cbm", "shipping_fees"]:
        tbl[c] = pd.to_numeric(tbl[c], errors="coerce")

    tbl["balance"] = tbl["amount"] - tbl["client_paid"] - tbl["office_paid"]
    tbl["shipping_mark"] = tbl["shipping_mark"].astype(str).str.strip()
    return tbl.reset_index(drop=True), hdr


df_all, hdr = load_data(DATA_FILE)

# ---------------------------------------------------------------- sidebar filters
with st.sidebar:
    st.title("🚢 Logistics Dashboard")
    st.caption(f"Client code **{hdr['code']}** · source: ذكاء 2.xlsx")

    st.subheader("Filters / الفلاتر")

    containers = sorted(df_all["container"].unique())
    sel_containers = st.multiselect(
        "Container No. (الحاوية)", containers, default=containers
    )

    marks = sorted(df_all["shipping_mark"].unique())
    sel_marks = st.multiselect("Shipping Mark (العلامة)", marks, default=marks)

    amt_min, amt_max = int(df_all["amount"].min()), int(df_all["amount"].max())
    amt_range = st.slider(
        "Amount range (نطاق المبلغ)", amt_min, amt_max, (amt_min, amt_max),
        step=max(1, (amt_max - amt_min) // 100),
    )

    st.divider()
    st.subheader("Reported totals (from file)")
    st.metric("عدد الطلبات (Orders)", f"{int(hdr['orders_reported']):,}")
    st.metric("عدد الحاويات (Containers)", f"{int(hdr['containers_reported']):,}")

# ---------------------------------------------------------------- apply filters
df = df_all[
    df_all["container"].isin(sel_containers)
    & df_all["shipping_mark"].isin(sel_marks)
    & df_all["amount"].between(amt_range[0], amt_range[1])
].copy()

if df.empty:
    st.error("No rows match the current filters. Please widen your selection.")
    st.stop()

# ---------------------------------------------------------------- KPI cards
total_amount = df["amount"].sum()
total_client = df["client_paid"].sum()
total_office = df["office_paid"].sum()
total_ctns = int(df["ctns"].sum())
total_cbm = df["cbm"].sum()
total_fees = df["shipping_fees"].sum()

st.title("🚢 Logistics Dashboard — B12")
st.caption("Interactive view of shipments by container, shipping mark, payments and freight")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Orders (الطلبات)", f"{len(df):,}")
k2.metric("Containers (الحاويات)", df["container"].nunique())
k3.metric("Total Amount", f"{total_amount:,.0f}")
k4.metric("Client Paid", f"{total_client:,.0f}")
k5.metric("Office Paid", f"{total_office:,.0f}")

k6, k7, k8, k9, k10 = st.columns(5)
k6.metric("Cartons (Ctns)", f"{total_ctns:,}")
k7.metric("Volume (CBM)", f"{total_cbm:,.2f}")
k8.metric("Shipping Fees (أجور الشحن)", f"{total_fees:,.1f}")
k9.metric("Client Share", f"{total_client / total_amount * 100:.1f}%")
k10.metric("Office Share", f"{total_office / total_amount * 100:.1f}%")

st.divider()

# ---------------------------------------------------------------- chart 1: payments by container
by_container = (
    df.groupby("container", as_index=False)
    .agg(amount=("amount", "sum"), client_paid=("client_paid", "sum"),
         office_paid=("office_paid", "sum"), orders=("shipping_mark", "count"),
         ctns=("ctns", "sum"), cbm=("cbm", "sum"))
    .sort_values("amount", ascending=False)
)

fig1 = go.Figure()
fig1.add_bar(
    x=by_container["container"], y=by_container["client_paid"],
    name="Client Paid", marker_color="#4FC3F7",
)
fig1.add_bar(
    x=by_container["container"], y=by_container["office_paid"],
    name="Office Paid", marker_color="#FFB74D",
)
fig1.add_scatter(
    x=by_container["container"], y=by_container["amount"],
    name="Total Amount", mode="lines+markers",
    line=dict(color="#E8EAED", width=2, dash="dot"), marker=dict(size=7),
)
fig1.update_layout(
    barmode="stack", template=PLOTLY_TEMPLATE,
    title="Payments & Amount by Container",
    xaxis_title="Container", yaxis_title="Value",
    height=420, legend=dict(orientation="h", y=1.12),
    margin=dict(l=10, r=10, t=60, b=10),
)

c_left, c_right = st.columns([3, 2])
with c_left:
    st.plotly_chart(fig1, use_container_width=True)

    # ---------------------------------------------------------------- chart 2: top shipping marks
    top_marks = df.nlargest(15, "amount").sort_values("amount")
    fig2 = px.bar(
        top_marks, x="amount", y="shipping_mark", color="container",
        orientation="h", template=PLOTLY_TEMPLATE,
        title="Top 15 Shipping Marks by Amount",
        labels={"amount": "Amount", "shipping_mark": "Shipping Mark"},
        color_discrete_sequence=px.colors.qualitative.Dark24,
    )
    fig2.update_layout(height=480, margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig2, use_container_width=True)

with c_right:
    # ---------------------------------------------------------------- chart 3: payment split donut
    split = pd.DataFrame(
        {"party": ["Client Paid", "Office Paid"],
         "value": [total_client, total_office]}
    )
    fig3 = px.pie(
        split, names="party", values="value", hole=0.55,
        template=PLOTLY_TEMPLATE, title="Payment Split",
        color_discrete_sequence=["#4FC3F7", "#FFB74D"],
    )
    fig3.update_traces(textinfo="percent+label", textfont_size=13)
    fig3.update_layout(height=300, margin=dict(l=10, r=10, t=60, b=10),
                       showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    # ---------------------------------------------------------------- chart 4: ctns vs cbm
    fig4 = px.scatter(
        df, x="ctns", y="cbm", size="amount", color="container",
        hover_name="shipping_mark", template=PLOTLY_TEMPLATE,
        title="Cartons vs Volume (CBM) — bubble = Amount",
        labels={"ctns": "Sum of Ctns", "cbm": "Sum of Cbm"},
        color_discrete_sequence=px.colors.qualitative.Dark24,
    )
    fig4.update_layout(height=480, margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig4, use_container_width=True)

# ---------------------------------------------------------------- chart 5: orders per container
fig5 = px.bar(
    by_container, x="container", y="orders", color="ctns",
    template=PLOTLY_TEMPLATE, title="Orders & Cartons per Container",
    labels={"orders": "Number of Orders", "ctns": "Cartons"},
    color_continuous_scale="Teal",
)
fig5.update_layout(height=360, margin=dict(l=10, r=10, t=60, b=10))
st.plotly_chart(fig5, use_container_width=True)

# ---------------------------------------------------------------- data table
st.divider()
st.subheader("📋 Detailed Data (البيانات التفصيلية)")
show_df = df[
    ["container", "shipping_mark", "amount", "client_paid", "office_paid",
     "balance", "ctns", "cbm", "shipping_fees"]
].sort_values(["container", "amount"], ascending=[True, False])

csv = show_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "⬇️ Download filtered data (CSV)", csv,
    file_name="logistics_filtered.csv", mime="text/csv",
)

st.dataframe(show_df, use_container_width=True, height=420, hide_index=True)

st.caption(
    f"Showing {len(df)} of {len(df_all)} orders · "
    f"Totals — Amount: {total_amount:,.0f} · Cartons: {total_ctns:,} · "
    f"CBM: {total_cbm:,.2f} · Fees: {total_fees:,.1f}"
)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="Kopiseru – Area Manager Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

DAY_NAMES = {0: "Sen", 1: "Sel", 2: "Rab", 3: "Kam", 4: "Jum", 5: "Sab", 6: "Min"}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

.stApp { background: #F2F4F7; }
section[data-testid="stSidebar"] > div { background: #FFFFFF !important; }
.stSidebar { background: #FFFFFF !important; border-right: 1px solid #EAECF0; }

.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.05rem !important;
    padding-left: 1.1rem !important;
    padding-right: 1.1rem !important;
    max-width: 100% !important;
}
[data-testid="stHorizontalBlock"] { gap: 0.55rem !important; }

/* Header */
.dash-hdr { display:flex; align-items:baseline; gap:0.7rem; margin-bottom:0.45rem; }
.dash-title { font-size:1.05rem; font-weight:700; color:#101828; letter-spacing:-.01em; }
.dash-sub { font-size:0.63rem; color:#98A2B3; }

/* KPI Strip */
.kpi-strip {
    display:flex; align-items:stretch;
    background:#FFFFFF; border:1px solid #EAECF0;
    border-radius:10px; padding:0.42rem 0;
    margin-bottom:0.52rem;
    box-shadow:0 1px 4px rgba(16,24,40,0.05);
}
.kpi-item { flex:1; text-align:center; padding:0 0.5rem; border-right:1px solid #F2F4F7; }
.kpi-item:last-child { border-right:none; }
.kpi-l { font-size:0.57rem; color:#98A2B3; text-transform:uppercase; letter-spacing:.08em; font-weight:600; }
.kpi-v { font-size:0.98rem; font-weight:700; color:#101828; line-height:1.2; }
.kpi-d { font-size:0.57rem; font-weight:600; }
.kpi-d.pos { color:#12B76A; } .kpi-d.neg { color:#F04438; } .kpi-d.neu { color:#98A2B3; }

/* Chart box */
.cbox {
    background:#FFFFFF; border:1px solid #EAECF0;
    border-radius:12px; padding:0.5rem 0.8rem 0.2rem;
    box-shadow:0 1px 4px rgba(16,24,40,0.05);
    margin-bottom:0.4rem;
}
.ct  { font-size:0.71rem; font-weight:700; color:#344054; margin:0; }
.cs  { font-size:0.57rem; color:#98A2B3; margin:0; }

/* Sidebar */
.stSelectbox label, .stDateInput label, .stMultiSelect label {
    color:#667085 !important; font-size:0.66rem !important;
    font-weight:600 !important; text-transform:uppercase; letter-spacing:.07em;
}
.brand { font-size:1.05rem; font-weight:700; color:#101828; }
.brand-sub { font-size:0.61rem; color:#98A2B3; margin-top:1px; }

/* Image placeholder */
.img-box {
    width:100%; aspect-ratio:16/6;
    background:#F9FAFB; border:1.5px dashed #D0D5DD;
    border-radius:10px; display:flex; flex-direction:column;
    align-items:center; justify-content:center; gap:0.2rem;
    margin-bottom:0.85rem;
}
.img-box-icon { font-size:1.4rem; opacity:0.3; }
.img-box-text { font-size:0.6rem; color:#98A2B3; font-weight:500; }

[data-baseweb="tag"] { background-color:#F2F4F7 !important; color:#344054 !important; border:none !important; }
.stPlotlyChart { margin-top:-0.25rem !important; }
hr { border-color:#F2F4F7 !important; margin:0.25rem 0 !important; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:#F2F4F7; }
::-webkit-scrollbar-thumb { background:#D0D5DD; border-radius:4px; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv("kopiseru.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["day_name"] = df["day_of_week"].map(DAY_NAMES)
    return df

df = load_data()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("<div class='brand'>☕ Kopiseru</div>"
                "<div class='brand-sub'>Area Manager Dashboard</div>",
                unsafe_allow_html=True)
    st.divider()

    provinces = sorted(df["branch_province"].unique())
    selected_province = st.selectbox(
        "Provinsi", options=provinces,
        index=provinces.index("dki jakarta") if "dki jakarta" in provinces else 0,
        format_func=lambda x: x.title(),
    )
    min_date, max_date = df["date"].min(), df["date"].max()
    date_range = st.date_input("Rentang Tanggal", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)
    start_date, end_date = (date_range if len(date_range) == 2 else (min_date, max_date))

    branch_types = sorted(df["branch_type"].unique())
    selected_types = st.multiselect(
        "Tipe Cabang", options=branch_types, default=branch_types,
        format_func=lambda x: x.title(),
    )
    st.divider()
    st.caption("Data: 2021 – 2023  ·  40 cabang  ·  8 provinsi")


# ============================================================
# FILTER
# ============================================================
mask = (
    (df["branch_province"] == selected_province)
    & (df["date"] >= pd.Timestamp(start_date))
    & (df["date"] <= pd.Timestamp(end_date))
    & (df["branch_type"].isin(selected_types))
)
fdf = df[mask]
ndf = df[
    (df["date"] >= pd.Timestamp(start_date))
    & (df["date"] <= pd.Timestamp(end_date))
    & (df["branch_type"].isin(selected_types))
]
n_cabang = fdf["branch_name"].nunique()

st.markdown(
    f"<div class='dash-hdr'>"
    f"<span class='dash-title'>☕ {selected_province.title()} — {n_cabang} Cabang</span>"
    f"<span class='dash-sub'>{start_date.strftime('%d %b %Y')} – {end_date.strftime('%d %b %Y')}</span>"
    f"</div>",
    unsafe_allow_html=True,
)

if fdf.empty:
    st.warning("Tidak ada data. Ubah filter di sidebar.")
    st.stop()


# ============================================================
# KPI STRIP
# ============================================================
total_rev  = fdf["total_revenue"].sum()
total_prof = fdf["profit"].sum()
total_cost = fdf["operating_cost"].sum()
total_txn  = fdf["total_transactions"].sum()
avg_margin = fdf["profit_margin"].mean()
nat_margin = ndf["profit_margin"].mean()
avg_ticket = fdf["avg_ticket_size"].mean()
nat_ticket = ndf["avg_ticket_size"].mean()
d_mg = avg_margin - nat_margin
d_tk = avg_ticket - nat_ticket

def badge(val, fmt):
    s = "▲" if val >= 0 else "▼"
    c = "pos" if val >= 0 else "neg"
    return f'<span class="kpi-d {c}">{s} {fmt(abs(val))}</span>'

days = max((end_date - start_date).days, 1)

st.markdown(f"""
<div class="kpi-strip">
  <div class="kpi-item">
    <div class="kpi-l">Total Revenue</div>
    <div class="kpi-v">Rp {total_rev/1e6:,.1f} Jt</div>
    <span class="kpi-d neu">{n_cabang} cabang aktif</span>
  </div>
  <div class="kpi-item">
    <div class="kpi-l">Total Profit</div>
    <div class="kpi-v">Rp {total_prof/1e6:,.1f} Jt</div>
    <span class="kpi-d neu">{total_prof/total_rev*100:.1f}% dr revenue</span>
  </div>
  <div class="kpi-item">
    <div class="kpi-l">Biaya Operasional</div>
    <div class="kpi-v">Rp {total_cost/1e6:,.1f} Jt</div>
    <span class="kpi-d neu">{total_cost/total_rev*100:.1f}% dr revenue</span>
  </div>
  <div class="kpi-item">
    <div class="kpi-l">Avg Margin</div>
    <div class="kpi-v">{avg_margin*100:.1f}%</div>
    {badge(d_mg, lambda v: f"{v*100:.1f}pp")} <span class="kpi-d neu">vs nasional</span>
  </div>
  <div class="kpi-item">
    <div class="kpi-l">Avg Ticket Size</div>
    <div class="kpi-v">Rp {avg_ticket:,.0f}</div>
    {badge(d_tk, lambda v: f"Rp {v:,.0f}")} <span class="kpi-d neu">vs nasional</span>
  </div>
  <div class="kpi-item">
    <div class="kpi-l">Total Transaksi</div>
    <div class="kpi-v">{total_txn:,.0f}</div>
    <span class="kpi-d neu">avg {total_txn/n_cabang/days*30:.0f}/cab/bln</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# SHARED HELPERS
# ============================================================
BG   = "rgba(0,0,0,0)"
TPL  = "plotly_white"
CFG  = {"displayModeBar": False}
GRID = "#F2F4F7"
LINE = "#EAECF0"
TXT  = "#667085"
TXT2 = "#98A2B3"

# Soft color palette
SA = "#7EB8D4"   # sky blue
SB = "#85C99E"   # sage green
SC = "#F4A26E"   # peach
SD = "#B39DDB"   # lavender
SE = "#F7C672"   # amber
SF = "#E8909A"   # rose
SG = "#80C4BB"   # teal

def base(fig, h, lm=4, rm=8, is_cat_y=False):
    fig.update_layout(
        height=h, paper_bgcolor=BG, plot_bgcolor=BG,
        template=TPL, margin=dict(l=lm, r=rm, t=8, b=4),
        font=dict(family="Plus Jakarta Sans", size=10, color=TXT),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=LINE,
                        font=dict(family="Plus Jakarta Sans", size=11, color="#101828")),
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=LINE, zeroline=False, tickfont_size=9)
    if is_cat_y:
        fig.update_yaxes(gridcolor=GRID, linecolor=LINE, zeroline=False, tickfont_size=8,
                         type="category", dtick=1, automargin=True)
    else:
        fig.update_yaxes(gridcolor=GRID, linecolor=LINE, zeroline=False, tickfont_size=9)
    return fig

def box(title, sub=""):
    s = f'<div class="cs">{sub}</div>' if sub else ""
    st.markdown(f'<div class="cbox"><div class="ct">{title}</div>{s}', unsafe_allow_html=True)

def box_end():
    st.markdown("</div>", unsafe_allow_html=True)

def short(series):
    return series.str.title().str.replace("Kopiseru ", "", regex=False)


# ============================================================
# ROW 1 — FULL WIDTH: Tren (compact)
# ============================================================
box("📈 Tren Revenue, Biaya & Profit",
    "Gambaran besar wilayah — kondisi keuangan dari waktu ke waktu")
tr = (
    fdf.set_index("date").resample("ME")
    .agg(rev=("total_revenue","sum"), cost=("operating_cost","sum"), prof=("profit","sum"))
    .reset_index()
)
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=tr["date"], y=tr["rev"], name="Revenue",
    mode="lines", line=dict(color=SA, width=2),
    fill="tozeroy", fillcolor="rgba(126,184,212,0.10)",
    hovertemplate="<b>%{x|%b %Y}</b><br>Revenue: Rp %{y:,.0f}<extra></extra>",
))
fig1.add_trace(go.Scatter(
    x=tr["date"], y=tr["cost"], name="Biaya",
    mode="lines", line=dict(color=SC, width=1.8, dash="dot"),
    fill="tozeroy", fillcolor="rgba(244,162,110,0.08)",
    hovertemplate="<b>%{x|%b %Y}</b><br>Biaya: Rp %{y:,.0f}<extra></extra>",
))
fig1.add_trace(go.Scatter(
    x=tr["date"], y=tr["prof"], name="Profit",
    mode="lines", line=dict(color=SB, width=2),
    hovertemplate="<b>%{x|%b %Y}</b><br>Profit: Rp %{y:,.0f}<extra></extra>",
))
fig1.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font_size=9),
    yaxis=dict(tickformat=",.0s"),
)
base(fig1, h=95)
st.plotly_chart(fig1, width="stretch", config=CFG, key="trend")
box_end()

# ============================================================
# ROW 2 — Pendapatan & Biaya (horizontal) [3] | Profit Margin [2]
# ============================================================
r2a, r2b = st.columns([3, 2])

# helper: dynamic height based on branch count
def dh(n, per=14, base_h=95):   # per px per branch
    return max(base_h, n * per + 24)

n = fdf["branch_name"].nunique()

with r2a:
    box("💰 Pendapatan & Biaya per Cabang",
        "Revenue vs biaya — cabang mana yang paling boros?")
    cb = (
        fdf.groupby("branch_name")
        .agg(rev=("total_revenue","sum"), cost=("operating_cost","sum"))
        .reset_index().sort_values("rev", ascending=True)
    )
    cb["lbl"]   = short(cb["branch_name"])
    cb["ratio"] = (cb["cost"] / cb["rev"] * 100).round(1)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        name="Revenue", y=cb["lbl"], x=cb["rev"],
        orientation="h", marker_color=SA, marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Revenue: Rp %{x:,.0f}<extra></extra>",
    ))
    fig2.add_trace(go.Bar(
        name="Biaya", y=cb["lbl"], x=cb["cost"],
        orientation="h", marker_color=SC, marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Biaya: Rp %{x:,.0f}<br>(%{customdata:.1f}% dr rev)<extra></extra>",
        customdata=cb["ratio"],
    ))
    fig2.update_layout(
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font_size=9),
        xaxis=dict(tickformat=",.0s"),
    )
    base(fig2, h=dh(n), is_cat_y=True)
    st.plotly_chart(fig2, width="stretch", config=CFG, key="cost_branch")
    box_end()

with r2b:
    box("📊 Profit Margin per Cabang",
        "Hijau = di atas nasional · merah = di bawah")
    mg = (
        fdf.groupby("branch_name")["profit_margin"]
        .mean().reset_index()
        .sort_values("profit_margin", ascending=True)
    )
    mg["lbl"] = short(mg["branch_name"])
    nat_mg    = ndf["profit_margin"].mean()
    mcol      = [SB if v >= nat_mg else SF for v in mg["profit_margin"]]
    fig3 = go.Figure(go.Bar(
        x=mg["profit_margin"], y=mg["lbl"], orientation="h",
        marker_color=mcol, marker_line_width=0,
        text=[f"{v*100:.1f}%" for v in mg["profit_margin"]],
        textposition="outside", textfont=dict(size=8, color=TXT),
        hovertemplate="<b>%{y}</b><br>Margin: %{x:.1%}<extra></extra>",
    ))
    fig3.add_vline(
        x=nat_mg, line_dash="dash", line_color=SD,
        annotation_text=f"Nas. {nat_mg*100:.1f}%",
        annotation_position="top right",
        annotation_font=dict(color=SD, size=8),
    )
    fig3.update_layout(xaxis=dict(tickformat=".0%"))
    base(fig3, h=dh(n), rm=48, is_cat_y=True)
    st.plotly_chart(fig3, width="stretch", config=CFG, key="margin")
    box_end()


# ============================================================
# ROW 3 — Ticket | Efisiensi Staff | Komposisi | Weekend vs Weekday
# ============================================================
r3a, r3b, r3c, r3d = st.columns(4)

H3 = dh(n, per=13, base_h=95)

# ── Avg Ticket Size ──────────────────────────────────────────
with r3a:
    box("🎫 Avg Ticket Size", "Ticket kecil = potensi upsell")
    tk = (
        fdf.groupby("branch_name")["avg_ticket_size"]
        .mean().reset_index()
        .sort_values("avg_ticket_size", ascending=True)
    )
    tk["lbl"] = short(tk["branch_name"])
    nat_tk    = ndf["avg_ticket_size"].mean()
    tkcol     = [SB if v >= nat_tk else SD for v in tk["avg_ticket_size"]]
    fig4 = go.Figure(go.Bar(
        x=tk["avg_ticket_size"], y=tk["lbl"], orientation="h",
        marker_color=tkcol, marker_line_width=0,
        text=[f"Rp{v/1e3:.0f}k" for v in tk["avg_ticket_size"]],
        textposition="outside", textfont=dict(size=7.5, color=TXT),
        hovertemplate="<b>%{y}</b><br>Avg Ticket: Rp %{x:,.0f}<extra></extra>",
    ))
    fig4.add_vline(
        x=nat_tk, line_dash="dash", line_color=SC,
        annotation_text="Nas.",
        annotation_position="top right",
        annotation_font=dict(color=SC, size=8),
    )
    fig4.update_layout(xaxis=dict(tickformat=",.0f"))
    base(fig4, h=H3, rm=38, is_cat_y=True)
    st.plotly_chart(fig4, width="stretch", config=CFG, key="ticket")
    box_end()

# ── Efisiensi Staff — semua cabang ───────────────────────────
with r3b:
    box("👥 Efisiensi Staff", "Txn/karyawan vs benchmark nasional")
    eff = (
        fdf.groupby("branch_name")["transactions_per_employee"]
        .mean().reset_index()
        .sort_values("transactions_per_employee", ascending=True)
    )
    eff["lbl"] = short(eff["branch_name"])
    nat_eff    = ndf["transactions_per_employee"].mean()
    ecol       = [SB if v >= nat_eff else SE for v in eff["transactions_per_employee"]]
    fig5 = go.Figure(go.Bar(
        x=eff["transactions_per_employee"], y=eff["lbl"], orientation="h",
        marker_color=ecol, marker_line_width=0,
        text=[f"{v:.1f}" for v in eff["transactions_per_employee"]],
        textposition="outside", textfont=dict(size=7.5, color=TXT),
        hovertemplate="<b>%{y}</b><br>%{x:.1f} txn/karyawan<extra></extra>",
    ))
    fig5.add_vline(
        x=nat_eff, line_dash="dash", line_color=SC,
        annotation_text=f"Nas. {nat_eff:.1f}",
        annotation_position="top right",
        annotation_font=dict(color=SC, size=8),
    )
    base(fig5, h=H3, rm=38, is_cat_y=True)
    st.plotly_chart(fig5, width="stretch", config=CFG, key="staff_eff")
    box_end()

# ── Komposisi Channel per Cabang (stacked horizontal) ────────
with r3c:
    box("🛍️ Komposisi Layanan", "Proporsi dine-in · delivery · takeaway")
    ch = (
        fdf.groupby("branch_name")[["dine_in_percent","delivery_percent","takeaway_percent"]]
        .mean().reset_index()
        .sort_values("dine_in_percent", ascending=True)
    )
    ch["lbl"] = short(ch["branch_name"])
    fig6 = go.Figure()
    fig6.add_trace(go.Bar(
        name="Dine-in", y=ch["lbl"], x=ch["dine_in_percent"],
        orientation="h", marker_color=SA, marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Dine-in: %{x:.1f}%<extra></extra>",
    ))
    fig6.add_trace(go.Bar(
        name="Delivery", y=ch["lbl"], x=ch["delivery_percent"],
        orientation="h", marker_color=SC, marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Delivery: %{x:.1f}%<extra></extra>",
    ))
    fig6.add_trace(go.Bar(
        name="Takeaway", y=ch["lbl"], x=ch["takeaway_percent"],
        orientation="h", marker_color=SB, marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Takeaway: %{x:.1f}%<extra></extra>",
    ))
    fig6.update_layout(
        barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font_size=8),
        xaxis=dict(ticksuffix="%"),
    )
    base(fig6, h=H3, is_cat_y=True)
    st.plotly_chart(fig6, width="stretch", config=CFG, key="channel_comp")
    box_end()

# ── Weekend vs Weekday per Cabang (horizontal grouped) ───────
with r3d:
    box("📅 Weekend vs Weekday", "Diurutkan selisih terbesar — dasar jadwal shift")
    wd = (
        fdf.groupby(["branch_name","is_weekend"])["total_transactions"]
        .mean().reset_index()
    )
    wd_pivot = (
        wd.pivot(index="branch_name", columns="is_weekend",
                 values="total_transactions")
    )
    if True not in wd_pivot.columns:
        wd_pivot[True] = 0.0
    if False not in wd_pivot.columns:
        wd_pivot[False] = 0.0
    wd_pivot = wd_pivot.fillna(0.0).reset_index()
    wd_pivot = wd_pivot.rename(columns={False: "Weekday", True: "Weekend"})
    wd_pivot["lbl"]  = short(wd_pivot["branch_name"])
    wd_pivot["diff"] = wd_pivot["Weekend"] - wd_pivot["Weekday"]
    wd_pivot = wd_pivot.sort_values("diff", ascending=True)  # ascending for horizontal
    fig7 = go.Figure()
    fig7.add_trace(go.Bar(
        name="Weekday", y=wd_pivot["lbl"], x=wd_pivot["Weekday"],
        orientation="h", marker_color=SA, marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Weekday: %{x:.0f} txn<extra></extra>",
    ))
    fig7.add_trace(go.Bar(
        name="Weekend", y=wd_pivot["lbl"], x=wd_pivot["Weekend"],
        orientation="h", marker_color=SG, marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Weekend: %{x:.0f} txn<extra></extra>",
    ))
    fig7.update_layout(
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font_size=8),
        xaxis=dict(title="Avg Txn/Hari"),
    )
    base(fig7, h=H3, is_cat_y=True)
    st.plotly_chart(fig7, width="stretch", config=CFG, key="weekend")
    box_end()

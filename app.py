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

# ============================================================
# DATA (Mocked for testing)
# ============================================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("kopiseru.csv")
    except:
        dates = pd.date_range(start="2023-01-01", end="2023-01-31")
        branches = ["Kopiseru Sudirman", "Kopiseru Kemang", "Kopiseru Menteng"]
        data = []
        import random
        for d in dates:
            for b in branches:
                rev = random.randint(5000000, 15000000)
                cost = rev * random.uniform(0.5, 0.8)
                data.append({
                    "date": d, "branch_name": b, "branch_province": "dki jakarta", "branch_type": "Kiosk",
                    "day_of_week": d.weekday(), "total_revenue": rev, "operating_cost": cost, 
                    "profit": rev - cost, "profit_margin": (rev-cost)/rev, "total_transactions": random.randint(100, 300),
                    "avg_ticket_size": random.randint(30000, 60000), "transactions_per_employee": random.uniform(10, 30),
                    "dine_in_percent": random.uniform(20, 50), "delivery_percent": random.uniform(20, 50),
                    "takeaway_percent": random.uniform(10, 30), "is_weekend": d.weekday() >= 5
                })
        df = pd.DataFrame(data)
        
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
        "📍 PROVINSI", options=provinces,
        index=provinces.index("dki jakarta") if "dki jakarta" in provinces else 0,
        format_func=lambda x: x.title(),
    )
    
    min_date, max_date = df["date"].min(), df["date"].max()
    date_range = st.date_input("📅 RENTANG TANGGAL", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)
    start_date, end_date = (date_range if len(date_range) == 2 else (min_date, max_date))

    branch_types = sorted(df["branch_type"].unique())
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #334155; margin-top: 1rem; margin-bottom:0.5rem;'>🏪 TIPE CABANG</div>", unsafe_allow_html=True)
    
    selected_types = []
    for bt in branch_types:
        if st.checkbox(bt.title(), value=True, key=f"chk_{bt}"):
            selected_types.append(bt)
            
    if not selected_types:
        selected_types = branch_types
        
    st.divider()
    theme_mode = st.radio("🎨 TEMA", ["Light Mode", "Dark Mode"], index=0, horizontal=False)
    is_dark = (theme_mode == "Dark Mode")
    
    st.divider()
    st.caption("Data: 2021 – 2023  ·  40 cabang")

# ============================================================
# DESIGN SYSTEM (THEMING VARIABLES)
# ============================================================
if is_dark:
    BG_COLOR = "#0F172A"       # slate-900
    SIDEBAR_BG = "#2C241E"     # dark espresso/mocha for dark mode sidebar
    CARD_BG = "#1E293B"        # slate-800
    BORDER_COLOR = "#334155"   # slate-700
    TEXT_MAIN = "#F8FAFC"      # slate-50
    TEXT_MUTED = "#94A3B8"     # slate-400
    GRID_COLOR = "#334155"     # slate-700
    PLOT_TEXT = "#F8FAFC"      # Strong white for graph text in dark mode
    TPL = "plotly_dark"
    # Inputs
    SIDEBAR_INPUT_BG = "#3E3025"
    SIDEBAR_INPUT_TEXT = "#F2E6D8"
    SIDEBAR_INPUT_BORDER = "#554437"
    # Palette
    PRIMARY = "#8B5A2B"  # Cokelat tua untuk dark mode
    SA = "#38BDF8"   # sky
    SB = "#34D399"   # emerald
    SC = "#FB923C"   # orange
    SD = "#818CF8"   # indigo
    SE = "#FBBF24"   # amber
    SF = "#F87171"   # red
    SG = "#2DD4BF"   # teal
else:
    BG_COLOR = "#F8FAFC"       # slate-50
    SIDEBAR_BG = "#FAF4EC"     # light warm cream / cokelat muda
    CARD_BG = "#FFFFFF"
    BORDER_COLOR = "#E2E8F0"   # slate-200
    TEXT_MAIN = "#0F172A"      # slate-900
    TEXT_MUTED = "#64748B"     # slate-500
    GRID_COLOR = "#F1F5F9"     # slate-100
    PLOT_TEXT = "#0F172A"      # Strong dark for graph text in light mode
    TPL = "plotly_white"
    # Inputs
    SIDEBAR_INPUT_BG = "#F4EAE0"  # Cokelat muda
    SIDEBAR_INPUT_TEXT = "#2C241E"
    SIDEBAR_INPUT_BORDER = "#E5D7C9"
    # Palette
    PRIMARY = "#5C4033"  # Cokelat tua untuk light mode
    SA = "#1E293B"   # dark slate
    SB = "#059669"   # emerald
    SC = "#D97706"   # amber
    SD = "#6366F1"   # indigo
    SE = "#EAB308"   # yellow
    SF = "#DC2626"   # red
    SG = "#0EA5E9"   # light blue

# ============================================================
# CUSTOM STYLES INJECTION
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; }}

/* Background & Sidebar */
.stApp {{ background: {BG_COLOR} !important; }}
section[data-testid="stSidebar"] > div {{ 
    background: {SIDEBAR_BG} !important; 
    padding-top: 0rem !important;
}}
[data-testid="stSidebarUserContent"] {{ 
    padding-top: 0rem !important; 
}}
.stSidebar {{ background: {SIDEBAR_BG} !important; border-right: 1px solid {BORDER_COLOR}; }}

/* TIGHTEN MAIN CONTAINER */
.block-container {{
    padding-top: 0.5rem !important;
    padding-bottom: 0.1rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
}}
[data-testid="stHorizontalBlock"] {{ gap: 0.8rem !important; }}
header[data-testid="stHeader"] {{ display: none; }}

/* KPI Strip Enhancements */
.kpi-strip {{
    display:flex; align-items:stretch; gap: 0.8rem;
    margin-bottom: 0.5rem;
}}
.kpi-item {{ 
    flex:1; text-align:left; 
    padding: 0.6rem 1rem;
    background: {CARD_BG}; 
    border:1px solid {BORDER_COLOR}; 
    border-radius:8px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}}
.kpi-title-box {{
    display: flex; flex-direction: column; justify-content: center;
}}
.kpi-l {{ font-size:0.7rem; color: {TEXT_MUTED}; text-transform:uppercase; letter-spacing:.05em; font-weight:700; margin-bottom: 0.1rem;}}
.kpi-v {{ font-size:1.3rem; font-weight:800; color: {TEXT_MAIN}; line-height:1.2;}}

/* Header / Title injected in Card */
.dash-title {{ font-size:1rem; font-weight:800; color: {TEXT_MAIN}; letter-spacing:-.02em; margin-bottom:0.1rem;}}
.dash-sub {{ font-size:0.7rem; color: {TEXT_MUTED}; font-weight: 500; }}

/* Chart box */
.cbox {{
    background: {CARD_BG}; border:1px solid {BORDER_COLOR};
    border-radius:8px; padding:0.6rem 0.8rem 0.1rem;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    margin-bottom: 0.5rem;
    height: 100%;
}}
.ct  {{ font-size:0.85rem; font-weight:700; color: {TEXT_MAIN}; margin:0 0 0.1rem 0; letter-spacing:-.01em;}}
.cs  {{ font-size:0.65rem; color: {TEXT_MUTED}; margin:0 0 0.2rem 0; font-weight:400;}}

/* Sidebar brand styling */
.brand {{ font-size:2rem; font-weight:800; color: {TEXT_MAIN}; letter-spacing:-.02em; line-height:1.2; margin-top:-2rem; }}
.brand-sub {{ font-size:0.9rem; color: {TEXT_MUTED}; font-weight: 500; margin-top:-2px; margin-bottom: 0.8rem; }}

section[data-testid="stSidebar"] .stSelectbox label, 
section[data-testid="stSidebar"] .stDateInput label,
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {{
    font-size: 0.75rem !important; font-weight: 600 !important; color: {TEXT_MUTED} !important;
}}

/* Custom styling for inputs to be light brown instead of default streamit colors */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-baseweb="base-input"] > input,
section[data-testid="stSidebar"] div[data-baseweb="base-input"] {{
    background-color: {SIDEBAR_INPUT_BG} !important;
    color: {SIDEBAR_INPUT_TEXT} !important;
    border-color: {SIDEBAR_INPUT_BORDER} !important;
}}
section[data-testid="stSidebar"] div[data-baseweb="select"] span {{
    color: {SIDEBAR_INPUT_TEXT} !important;
}}

/* Streamlit widgets texts inside sidebar */
div[data-testid="stSidebar"] .stCheckbox label,
div[data-testid="stSidebar"] .stRadio label {{
    color: {TEXT_MAIN} !important;
}}

/* ==============================================================
   CHECKBOX - TIPE CABANG
============================================================== */
/* 1. Target the visual box */
div[data-testid="stCheckbox"] label > *:not(:has(div[data-testid="stMarkdownContainer"])):not(input) {{
    border-radius: 50% !important;
    background-color: {SIDEBAR_INPUT_BG} !important;
    border: 2px solid {SIDEBAR_INPUT_BORDER} !important;
    width: 1.25rem !important;
    height: 1.25rem !important;
    margin-right: 0.5rem !important; /* Jarak antara bulatan dan teks */
    display: inline-block !important;
}}

/* 2. Checked state */
div[data-testid="stCheckbox"] label:has(input:checked) > *:not(:has(div[data-testid="stMarkdownContainer"])):not(input) {{
    background-color: {PRIMARY} !important;
    border-color: {PRIMARY} !important;
}}

/* 3. Hide ALL inner elements */
div[data-testid="stCheckbox"] label > *:not(:has(div[data-testid="stMarkdownContainer"])):not(input) > * {{
    display: none !important;
}}

/* ==============================================================
   RADIO BUTTON - TEMA
============================================================== */
/* Target the actual radio circle, avoiding the 'TEMA' label and the text */
div[data-testid="stRadio"] div[role="radiogroup"] label > *:not(:has(div[data-testid="stMarkdownContainer"])):not(input) {{
    background-color: {SIDEBAR_INPUT_BG} !important;
    border: 2px solid {SIDEBAR_INPUT_BORDER} !important;
    width: 1.25rem !important;
    height: 1.25rem !important;
    margin-right: 0.5rem !important; /* Jarak antara bulatan dan teks */
    border-radius: 50% !important; /* Pastikan selalu bulat */
}}

div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) > *:not(:has(div[data-testid="stMarkdownContainer"])):not(input) {{
    background-color: {PRIMARY} !important;
    border-color: {PRIMARY} !important;
}}

/* Hide inner native dot inside the radio circle */
div[data-testid="stRadio"] div[role="radiogroup"] label > *:not(:has(div[data-testid="stMarkdownContainer"])):not(input) > * {{
    display: none !important;
}}

/* Force vertical spacing between Light Mode and Dark Mode options */
div[data-testid="stRadio"] div[role="radiogroup"] label {{
    margin-bottom: 0.75rem !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] label:last-child {{
    margin-bottom: 0 !important;
}}

/* Tighten gaps for checkboxes */
div[data-testid="stSidebar"] div[data-testid="stCheckbox"] {{
    margin-bottom: -0.4rem !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width:4px; height: 4px;}}
::-webkit-scrollbar-track {{ background: {BG_COLOR}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER_COLOR}; border-radius:4px; }}
::-webkit-scrollbar-thumb:hover {{ background: {TEXT_MUTED}; }}
</style>
""", unsafe_allow_html=True)


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

if fdf.empty:
    st.warning("Tidak ada data. Silakan ubah filter di sidebar.")
    st.stop()


# ============================================================
# KPI STRIP
# ============================================================
total_rev  = fdf["total_revenue"].sum()
total_prof = fdf["profit"].sum()
avg_margin = fdf["profit_margin"].mean()

st.markdown(f"""
<div class="kpi-strip">
  <div class="kpi-item kpi-title-box">
    <div class="dash-title">{selected_province.title()} — {n_cabang} Cabang</div>
    <div class="dash-sub">{start_date.strftime('%d %b %y')} – {end_date.strftime('%d %b %y')}</div>
  </div>
  <div class="kpi-item">
    <div class="kpi-l">Total Revenue</div>
    <div class="kpi-v">Rp {total_rev/1e6:,.1f}M</div>
  </div>
  <div class="kpi-item">
    <div class="kpi-l">Total Profit</div>
    <div class="kpi-v">Rp {total_prof/1e6:,.1f}M</div>
  </div>
  <div class="kpi-item">
    <div class="kpi-l">Avg Profit Margin</div>
    <div class="kpi-v">{avg_margin*100:.1f}%</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# SHARED HELPERS & COLOR PALETTE
# ============================================================
BG   = "rgba(0,0,0,0)"
CFG  = {"displayModeBar": False}

# 📉 TINGGI GRAFIK DIPERKECIL (dari 240 ke 210) agar pas 1 layar
H_CHART = 210 

def base(fig, h, lm=0, rm=0, is_cat_y=False):
    fig.update_layout(
        height=h, paper_bgcolor=BG, plot_bgcolor=BG,
        template=TPL, margin=dict(l=lm, r=rm, t=5, b=0),
        font=dict(family="Plus Jakarta Sans", size=10, color=PLOT_TEXT),
        hoverlabel=dict(bgcolor=CARD_BG, bordercolor=BORDER_COLOR, font=dict(family="Plus Jakarta Sans", size=11, color=TEXT_MAIN)),
    )
    fig.update_xaxes(
        gridcolor=GRID_COLOR, linecolor=BORDER_COLOR, zeroline=False, 
        tickfont=dict(color=PLOT_TEXT, size=10)
    )
    if is_cat_y:
        fig.update_yaxes(
            gridcolor=GRID_COLOR, linecolor=BORDER_COLOR, zeroline=False, 
            type="category", dtick=1, automargin=True, 
            tickfont=dict(color=PLOT_TEXT, size=10)
        )
    else:
        fig.update_yaxes(
            gridcolor=GRID_COLOR, linecolor=BORDER_COLOR, zeroline=False, 
            tickfont=dict(color=PLOT_TEXT, size=10)
        )
    return fig

def box(title, sub=""):
    s = f'<div class="cs">{sub}</div>' if sub else ""
    st.markdown(f'<div class="cbox"><div class="ct">{title}</div>{s}', unsafe_allow_html=True)

def box_end():
    st.markdown("</div>", unsafe_allow_html=True)

def short(series):
    return series.str.title().str.replace("Kopiseru ", "", regex=False)


# ============================================================
# ROW 1: 3 Column Grid
# ============================================================
r1_col1, r1_col2, r1_col3 = st.columns(3)

with r1_col1:
    box("📈 Tren Keuangan Wilayah", "Pergerakan Rev, Biaya & Profit")
    tr = (fdf.set_index("date").resample("ME")
          .agg(rev=("total_revenue","sum"), cost=("operating_cost","sum"), prof=("profit","sum"))
          .reset_index())
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=tr["date"], y=tr["rev"], name="Rev", mode="lines", line=dict(color=SA, width=2)))
    fig1.add_trace(go.Scatter(x=tr["date"], y=tr["cost"], name="Biaya", mode="lines", line=dict(color=SC, width=2, dash="dot")))
    fig1.add_trace(go.Scatter(x=tr["date"], y=tr["prof"], name="Profit", mode="lines", line=dict(color=SB, width=2)))
    fig1.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=PLOT_TEXT)), 
        yaxis=dict(tickformat=",.0s")
    )
    base(fig1, h=H_CHART)
    st.plotly_chart(fig1, use_container_width=True, config=CFG)
    box_end()

with r1_col2:
    box("💰 Revenue vs Biaya", "Performa per cabang")
    cb = fdf.groupby("branch_name").agg(rev=("total_revenue","sum"), cost=("operating_cost","sum")).reset_index().sort_values("rev", ascending=True)
    cb["lbl"] = short(cb["branch_name"])
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Rev", y=cb["lbl"], x=cb["rev"], orientation="h", marker_color=SA))
    fig2.add_trace(go.Bar(name="Biaya", y=cb["lbl"], x=cb["cost"], orientation="h", marker_color=SC))
    fig2.update_layout(
        barmode="group", showlegend=False, xaxis=dict(tickformat=",.0s"),
        font=dict(color=PLOT_TEXT)
    )
    base(fig2, h=H_CHART, is_cat_y=True)
    st.plotly_chart(fig2, use_container_width=True, config=CFG)
    box_end()

with r1_col3:
    box("📊 Profit Margin per Cabang", "Vs rata-rata nasional")
    nat_margin = ndf["profit_margin"].mean()
    mg = fdf.groupby("branch_name")["profit_margin"].mean().reset_index().sort_values("profit_margin", ascending=True)
    mg["lbl"] = short(mg["branch_name"])
    mcol = [SB if v >= nat_margin else SF for v in mg["profit_margin"]]
    fig3 = go.Figure(go.Bar(
        x=mg["profit_margin"], y=mg["lbl"], orientation="h", marker_color=mcol,
        text=[f"{v*100:.1f}%" for v in mg["profit_margin"]],
        textposition="outside", textfont=dict(size=10, color=PLOT_TEXT)
    ))
    fig3.add_vline(x=nat_margin, line_dash="dash", line_color=SD)
    fig3.update_layout(xaxis=dict(tickformat=".0%"), font=dict(color=PLOT_TEXT))
    base(fig3, h=H_CHART, is_cat_y=True)
    st.plotly_chart(fig3, use_container_width=True, config=CFG)
    box_end()

# ============================================================
# ROW 2: 3 Column Grid
# ============================================================
r2_col1, r2_col2, r2_col3 = st.columns(3)

with r2_col1:
    box("🎫 Avg Ticket Size", "Pembelanjaan per transaksi")
    nat_ticket = ndf["avg_ticket_size"].mean()
    tk = fdf.groupby("branch_name")["avg_ticket_size"].mean().reset_index().sort_values("avg_ticket_size", ascending=True)
    tk["lbl"] = short(tk["branch_name"])
    tkcol = [SA if v >= nat_ticket else SE for v in tk["avg_ticket_size"]]
    fig4 = go.Figure(go.Bar(
        x=tk["avg_ticket_size"], y=tk["lbl"], orientation="h", marker_color=tkcol,
        text=[f"Rp{v/1e3:.0f}k" for v in tk["avg_ticket_size"]],
        textposition="outside", textfont=dict(size=10, color=PLOT_TEXT)
    ))
    fig4.add_vline(x=nat_ticket, line_dash="dash", line_color=SD)
    fig4.update_layout(font=dict(color=PLOT_TEXT))
    base(fig4, h=H_CHART, is_cat_y=True)
    st.plotly_chart(fig4, use_container_width=True, config=CFG)
    box_end()

with r2_col2:
    box("🛍️ Komposisi Layanan", "Dine-in, Delivery, Takeaway")
    ch = fdf.groupby("branch_name")[["dine_in_percent","delivery_percent","takeaway_percent"]].mean().reset_index().sort_values("dine_in_percent", ascending=True)
    ch["lbl"] = short(ch["branch_name"])
    fig6 = go.Figure()
    fig6.add_trace(go.Bar(name="Dine-in", y=ch["lbl"], x=ch["dine_in_percent"], orientation="h", marker_color=SA))
    fig6.add_trace(go.Bar(name="Delivery", y=ch["lbl"], x=ch["delivery_percent"], orientation="h", marker_color=SC))
    fig6.add_trace(go.Bar(name="Takeaway", y=ch["lbl"], x=ch["takeaway_percent"], orientation="h", marker_color=SB))
    fig6.update_layout(barmode="stack", showlegend=False, xaxis=dict(ticksuffix="%"), font=dict(color=PLOT_TEXT))
    base(fig6, h=H_CHART, is_cat_y=True)
    st.plotly_chart(fig6, use_container_width=True, config=CFG)
    box_end()

with r2_col3:
    box("📅 Transaksi: Weekend vs Weekday", "Dasar penjadwalan")
    wd = fdf.groupby(["branch_name","is_weekend"])["total_transactions"].mean().reset_index()
    wd_pivot = wd.pivot(index="branch_name", columns="is_weekend", values="total_transactions")
    if True not in wd_pivot.columns: wd_pivot[True] = 0.0
    if False not in wd_pivot.columns: wd_pivot[False] = 0.0
    wd_pivot = wd_pivot.fillna(0.0).reset_index().rename(columns={False: "Weekday", True: "Weekend"})
    wd_pivot["lbl"]  = short(wd_pivot["branch_name"])
    wd_pivot["diff"] = wd_pivot["Weekend"] - wd_pivot["Weekday"]
    wd_pivot = wd_pivot.sort_values("diff", ascending=True) 
    
    fig7 = go.Figure()
    fig7.add_trace(go.Bar(name="Wkday", y=wd_pivot["lbl"], x=wd_pivot["Weekday"], orientation="h", marker_color=SA))
    fig7.add_trace(go.Bar(name="Wkend", y=wd_pivot["lbl"], x=wd_pivot["Weekend"], orientation="h", marker_color=SG))
    fig7.update_layout(barmode="group", showlegend=False, font=dict(color=PLOT_TEXT))
    base(fig7, h=H_CHART, is_cat_y=True)
    st.plotly_chart(fig7, use_container_width=True, config=CFG)
    box_end()
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random

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
        branches = ["Kopiseru Sudirman", "Kopiseru Kemang", "Kopiseru Menteng", "Kopiseru Senayan"]
        data = []
        for d in dates:
            for b in branches:
                rev = random.randint(5000000, 15000000)
                cost = rev * random.uniform(0.5, 0.8)
                
                # Menyesuaikan variasi tipe cabang sesuai referensi
                if "Sudirman" in b: b_type = "Office Area"
                elif "Senayan" in b: b_type = "Mall"
                elif "Kemang" in b: b_type = "Standalone"
                else: b_type = "University"
                
                data.append({
                    "date": d, "branch_name": b, "branch_province": "dki jakarta", "branch_type": b_type,
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

# ── Helper: Format Rupiah Indonesia ─────────────────────────
def fmt_idr(val):
    """Format nilai Rupiah ke Rb/Jt/M/T secara otomatis."""
    abs_val = abs(val)
    if abs_val >= 1e12: return f"Rp {val/1e12:,.2f} T"
    elif abs_val >= 1e9: return f"Rp {val/1e9:,.1f} M"
    elif abs_val >= 1e6: return f"Rp {val/1e6:,.1f} Jt"
    elif abs_val >= 1e3: return f"Rp {val/1e3:,.1f} Rb"
    return f"Rp {val:,.0f}"

def idr_scale(series):
    """Skala terbaik (divisor, suffix IDR) untuk sumbu grafik."""
    mx = series.abs().max()
    if mx >= 1e12: return 1e12, " T"
    elif mx >= 1e9: return 1e9, " M"
    elif mx >= 1e6: return 1e6, " Jt"
    elif mx >= 1e3: return 1e3, " Rb"
    return 1, ""

# ============================================================
# TOP NAVBAR
# ============================================================
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([0.9, 0.8, 1.1, 1.0, 1.3])

with nav_col1:
    st.markdown("<div class='brand-container'>"
                "<div class='brand'>☕ Kopiseru</div>"
                "<div class='brand-sub'>Dashboard Analytics</div>"
                "</div>",
                unsafe_allow_html=True)

with nav_col2:
    provinces = sorted(df["branch_province"].unique())
    selected_province = st.selectbox(
        "📍 PROVINSI", options=provinces,
        index=provinces.index("dki jakarta") if "dki jakarta" in provinces else 0,
        format_func=lambda x: x.title(),
        label_visibility="collapsed"
    )

with nav_col3:
    min_date, max_date = df["date"].min(), df["date"].max()
    date_range = st.date_input("📅 RENTANG TANGGAL", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date, label_visibility="collapsed")
    start_date, end_date = (date_range if len(date_range) == 2 else (min_date, max_date))

with nav_col4:
    branch_types = sorted(df["branch_type"].unique())
    
    # MENGGUNAKAN POPOVER & CHECKBOX SEBAGAI GANTI MULTISELECT
    with st.popover("Tipe Cabang", use_container_width=True):
        selected_types = []
        for bt in branch_types:
            # Gunakan st.checkbox agar user memilih langsung dari list
            if st.checkbox(bt, value=True, key=f"filter_{bt}"):
                selected_types.append(bt)

with nav_col5:
    theme_mode = st.radio("🎨 TEMA", ["Light Mode", "Dark Mode"], index=0, horizontal=True, label_visibility="collapsed")
    is_dark = (theme_mode == "Dark Mode")
    

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
    # Inputs (Disamakan semua jadi warna kotak input)
    SIDEBAR_INPUT_BG = "#1E293B"       # match CARD_BG (slate-800)
    SIDEBAR_INPUT_TEXT = "#F8FAFC"     # TEXT_MAIN
    SIDEBAR_INPUT_BORDER = "#334155"   # BORDER_COLOR (slate-700)
    # Palette
    PRIMARY = "#8B5A2B"  
    SA = "#38BDF8"   
    SB = "#34D399"   
    SC = "#FB923C"   
    SD = "#818CF8"   
    SE = "#FBBF24"   
    SF = "#F87171"   
    SG = "#2DD4BF"   
else:
    BG_COLOR = "#FFFAF4"       # warm cream / off-white untuk main layout
    SIDEBAR_BG = "#FAF4EC"     # light warm cream / cokelat muda
    CARD_BG = "#FFFFFF"        # Kotak putih untuk grafik
    BORDER_COLOR = "#E2E8F0"   # slate-200
    TEXT_MAIN = "#0F172A"      # slate-900
    TEXT_MUTED = "#64748B"     # slate-500
    GRID_COLOR = "#F1F5F9"     # slate-100
    PLOT_TEXT = "#0F172A"      # Strong dark for graph text in light mode
    TPL = "plotly_white"
    # Inputs (Disamakan semua jadi warna kotak input)
    SIDEBAR_INPUT_BG = "#F4EAE0" 
    SIDEBAR_INPUT_TEXT = "#2C241E"
    SIDEBAR_INPUT_BORDER = "#E5D7C9"
    # Palette
    PRIMARY = "#5C4033"  
    SA = "#1E293B"   
    SB = "#059669"   
    SC = "#D97706"   
    SD = "#6366F1"   
    SE = "#EAB308"   
    SF = "#DC2626"   
    SG = "#0EA5E9"   

# ============================================================
# CUSTOM STYLES INJECTION
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; }}

/* Background & Sidebar */
.stApp {{ background: {BG_COLOR} !important; }}

/* TIGHTEN MAIN CONTAINER */
.block-container {{
    padding-top: 0.5rem !important;
    padding-bottom: 0.1rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
}}
[data-testid="stHorizontalBlock"] {{ gap: 0.8rem !important; }}
header[data-testid="stHeader"] {{ background: transparent !important; }}

/* Dashboard Cards */
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stVerticalBlockBorderWrapper"] > div,
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {{
    background-color: {CARD_BG} !important;
}}
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border: 1px solid {BORDER_COLOR} !important;
    border-radius: 8px !important;
    padding: 0.8rem !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
}}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{
    gap: 0.2rem !important;
}}

/* KPI Strip — Card Box Style */
.kpi-strip {{
    display: flex;
    align-items: stretch;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
}}
.kpi-title-box {{
    flex: 1.2;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 0.6rem 0.8rem;
}}
.kpi-card {{
    flex: 1;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: {CARD_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
    padding: 0.6rem 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}}
.kpi-card:hover {{
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border-color: {PRIMARY};
}}
.kpi-icon {{
    font-size: 1.5rem;
    line-height: 1;
    flex-shrink: 0;
}}
.kpi-body {{ display: flex; flex-direction: column; gap: 0.1rem; }}
.kpi-l {{ font-size:0.7rem; color: {TEXT_MUTED}; text-transform:uppercase; letter-spacing:.06em; font-weight:700; margin:0; }}
.kpi-v {{ font-size:1.25rem; font-weight:800; color: {TEXT_MAIN}; line-height:1.2; margin:0; }}

/* Header / Title injected in Card */
.dash-title {{ font-size:1rem; font-weight:800; color: {TEXT_MAIN}; letter-spacing:-.02em; margin-bottom:0.1rem;}}
.dash-sub {{ font-size:0.8rem; color: {TEXT_MUTED}; font-weight: 500; }}

/* Chart box wrapper */
.cbox {{
    background: transparent !important; 
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin-bottom: 0.2rem;
}}
.ct  {{ font-size:0.75rem; font-weight:700; color: {TEXT_MAIN}; margin:0 0 0.1rem 0; letter-spacing:-.01em;}}

/* Navbar brand styling (Flexbox Alignment) */
.brand {{ font-size:1.4rem; font-weight:800; color: {TEXT_MAIN}; letter-spacing:-.02em; line-height:1.1; margin:0; padding:0; }}
.brand-sub {{ font-size:0.75rem; color: {TEXT_MUTED}; font-weight: 600; line-height:1.1; margin:0; padding:0; }}
.brand-container {{ display: flex; flex-direction: column; justify-content: center; height: 40px; padding-left: 0.2rem; }}

/* ==============================================================
   INPUT UNIFICATION (Select, Date, Popover)
============================================================== */

/* ── 1. Wrapper Luar: Selectbox & Date Input ── */
div[data-baseweb="select"] > div {{
    background-color: {SIDEBAR_INPUT_BG} !important;
    border: 1px solid {SIDEBAR_INPUT_BORDER} !important;
    border-radius: 8px !important;
    min-height: 40px !important;
    height: 40px !important;
    box-shadow: none !important;
    transition: border-color 0.2s ease !important;
}}
div[data-baseweb="select"] > div:hover {{
    border-color: {PRIMARY} !important;
}}

/* ── 2. Date Input: wrapper LUAR yang bisa terlihat ── */
div[data-baseweb="input"] {{
    background-color: {SIDEBAR_INPUT_BG} !important;
    border: 1px solid {SIDEBAR_INPUT_BORDER} !important;
    border-radius: 8px !important;
    min-height: 40px !important;
    height: 40px !important;
    box-shadow: none !important;
    transition: border-color 0.2s ease !important;
}}
div[data-baseweb="input"]:hover {{
    border-color: {PRIMARY} !important;
}}

/* ── 3. Inner input (hapus background & border ganda) ── */
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input {{
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: {SIDEBAR_INPUT_TEXT} !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 0 10px !important;
}}

/* ── 4. Hapus wrapper base-input agar tidak double-box ── */
div[data-baseweb="base-input"] {{
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    min-height: unset !important;
    height: unset !important;
}}

/* ── 5. Warna Teks Selectbox ── */
div[data-baseweb="select"] div,
div[data-baseweb="select"] span {{
    color: {SIDEBAR_INPUT_TEXT} !important;
    font-weight: 500 !important;
}}

/* Penyesuaian Layout Internal Popover Button */
/* 1. Paksa tombol popover menjadi krem dengan selektor yang lebih spesifik */
div[data-testid="stPopover"] button {{
    background-color: {SIDEBAR_INPUT_BG} !important;
    color: {SIDEBAR_INPUT_TEXT} !important;
    border: 1px solid {SIDEBAR_INPUT_BORDER} !important;
    border-radius: 8px !important;
    padding: 0 12px !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    width: 100% !important;
    min-height: 40px !important;
}}

/* 2. Container teks direntangkan dan ditarik ke kiri */
div[data-testid="stPopover"] button > div:first-child {{
    flex-grow: 1 !important;
    display: flex !important;
    justify-content: flex-start !important;
    align-items: center !important;
}}

/* 3. Teks rata kiri */
div[data-testid="stPopover"] button p {{
    color: {SIDEBAR_INPUT_TEXT} !important;
    margin: 0 !important;
    text-align: left !important;
}}

/* Menghilangkan border bawaan saat aktif/focus */
div[data-testid="stPopover"] button:focus {{
    border-color: {PRIMARY} !important;
    box-shadow: none !important;
}}   

/* 2. Mengubah Background Body Popover (Ini yang sering terlewat) */
/* Kita targetkan elemen pembungkus di dalam popover */
[data-testid="stPopoverBody"] {{
    background-color: {SIDEBAR_INPUT_BG} !important; 
    border: 1px solid {SIDEBAR_INPUT_BORDER} !important;
    border-radius: 8px !important;
    padding: 10px !important;
}}

/* 3. Menghilangkan sisa warna putih pada container internal popover */
[data-testid="stPopoverBody"] > div {{
    background-color: transparent !important;
}}

/* Streamlit widgets texts inside navbar */
div[data-testid="stCheckbox"] label p,
div[data-testid="stRadio"] label p {{
    color: {TEXT_MAIN} !important;
}}

/* ==============================================================
   CHECKBOX KUSTOM
============================================================== */
div[data-testid="stCheckbox"] label > *:not(:has(div[data-testid="stMarkdownContainer"])):not(input) {{
    border-radius: 4px !important; 
    background-color: {SIDEBAR_INPUT_BG} !important;
    border: 2px solid {SIDEBAR_INPUT_BORDER} !important;
    width: 1.25rem !important;
    height: 1.25rem !important;
    margin-right: 0.5rem !important; 
    display: inline-block !important;
}}
div[data-testid="stCheckbox"] label:has(input:checked) > *:not(:has(div[data-testid="stMarkdownContainer"])):not(input) {{
    background-color: {PRIMARY} !important;
    border-color: {PRIMARY} !important;
}}
div[data-testid="stCheckbox"] label > *:not(:has(div[data-testid="stMarkdownContainer"])):not(input) > * {{
    display: none !important;
}}

/* ==============================================================
   RADIO BUTTON - TEMA (Sejajar Horizontal, Vertikal Center)
============================================================== */
div[data-testid="stRadio"] > div {{
    display: flex !important;
    align-items: center !important;
    height: 40px !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] {{
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 12px !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] label {{
    display: flex !important;
    align-items: center !important;
    margin: 0 !important;
    cursor: pointer;
    gap: 6px !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] label > *:not(:has(div[data-testid="stMarkdownContainer"])):not(input) {{
    background-color: {SIDEBAR_INPUT_BG} !important;
    border: 2px solid {SIDEBAR_INPUT_BORDER} !important;
    width: 1rem !important;
    height: 1rem !important;
    margin: 0 !important;
    border-radius: 50% !important;
    flex-shrink: 0 !important;
    transition: background-color 0.2s ease, border-color 0.2s ease !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) > *:not(:has(div[data-testid="stMarkdownContainer"])):not(input) {{
    background-color: {PRIMARY} !important;
    border-color: {PRIMARY} !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] label > *:not(:has(div[data-testid="stMarkdownContainer"])):not(input) > * {{
    display: none !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] label p {{
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: {TEXT_MAIN} !important;
    margin: 0 !important;
    line-height: 1 !important;
    white-space: nowrap !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width:4px; height: 4px;}}
::-webkit-scrollbar-track {{ background: {BG_COLOR}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER_COLOR}; border-radius:4px; }}
::-webkit-scrollbar-thumb:hover {{ background: {TEXT_MUTED}; }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# OPTIMASI 1: CUSTOM DIVIDER
# Mengganti st.divider() untuk mengontrol padding menjadi rapat
# ============================================================
st.markdown(f'<hr style="margin-top: -0.5rem; margin-bottom: 1rem; border: none; border-top: 1px solid {BORDER_COLOR};">', unsafe_allow_html=True)


# ============================================================
# FILTER
# ============================================================
start_ts = pd.Timestamp(start_date)
end_ts = pd.Timestamp(end_date)

ndf = df[
    (df["date"] >= start_ts)
    & (df["date"] <= end_ts)
    & (df["branch_type"].isin(selected_types))
]
fdf = ndf[ndf["branch_province"] == selected_province]
n_cabang = fdf["branch_name"].nunique()

if fdf.empty:
    st.warning("Tidak ada data. Silakan ubah filter di sidebar atau centang tipe cabang.")
    st.stop()


# ============================================================
# KPI STRIP
# ============================================================
total_rev  = fdf["total_revenue"].sum()
total_prof = fdf["profit"].sum()
avg_margin = fdf["profit_margin"].mean()

st.markdown(f"""
<div class="kpi-strip">
  <div class="kpi-title-box">
    <div class="dash-title">{selected_province.title()} — {n_cabang} Cabang</div>
    <div class="dash-sub">{start_date.strftime('%d %b %y')} – {end_date.strftime('%d %b %y')}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-body">
      <div class="kpi-l">Total Revenue</div>
      <div class="kpi-v">{fmt_idr(total_rev)}</div>
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-body">
      <div class="kpi-l">Total Profit</div>
      <div class="kpi-v">{fmt_idr(total_prof)}</div>
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-body">
      <div class="kpi-l">Avg Profit Margin</div>
      <div class="kpi-v">{avg_margin*100:.1f}%</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# SHARED HELPERS & COLOR PALETTE
# ============================================================
BG   = "rgba(0,0,0,0)"
CFG  = {"displayModeBar": False}

# 📉 TINGGI GRAFIK DIPERKECIL
H_CHART = 210 

def base(fig, h, lm=0, rm=0, bm=0, is_cat_y=False):
    fig.update_layout(
        height=h, paper_bgcolor=BG, plot_bgcolor=BG,
        template=TPL, margin=dict(l=lm, r=rm, t=5, b=bm),
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

def short(series):
    return series.str.title().str.replace("Kopiseru ", "", regex=False)


# ============================================================
# ROW 1: 3 Column Grid
# ============================================================
r1_col1, r1_col2, r1_col3 = st.columns(3)

with r1_col1:
    with st.container(border=True):
        st.markdown('<div class="ct">Tren Pendapatan, Biaya & Profit</div>', unsafe_allow_html=True)
        tr = (fdf.set_index("date").resample("ME")
              .agg(rev=("total_revenue","sum"), cost=("operating_cost","sum"), prof=("profit","sum"))
              .reset_index())
        sc1, sfx1 = idr_scale(tr[["rev","cost","prof"]].stack())
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=tr["date"], y=tr["rev"]/sc1, name="Pendapatan", mode="lines", line=dict(color=SA, width=2)))
        fig1.add_trace(go.Scatter(x=tr["date"], y=tr["cost"]/sc1, name="Biaya", mode="lines", line=dict(color=SC, width=2)))
        fig1.add_trace(go.Scatter(x=tr["date"], y=tr["prof"]/sc1, name="Profit", mode="lines", line=dict(color=SB, width=2)))
        fig1.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=PLOT_TEXT)),
            xaxis=dict(tickformat="%Y"),
            yaxis=dict(title=dict(text=f"Nilai Rupiah ({sfx1.strip()})", font=dict(size=10)), tickformat=",.1f"),
        )
        base(fig1, h=H_CHART, lm=55)
        st.plotly_chart(fig1, width="stretch", config=CFG)

with r1_col2:
    with st.container(border=True):
        st.markdown('<div class="ct">Pendapatan dan Biaya per Cabang</div>', unsafe_allow_html=True)
        cb = fdf.groupby("branch_name").agg(rev=("total_revenue","sum"), cost=("operating_cost","sum")).reset_index().sort_values("rev", ascending=True)
        cb["lbl"] = short(cb["branch_name"])
        sc2, sfx2 = idr_scale(cb[["rev","cost"]].stack())
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Biaya", y=cb["lbl"], x=cb["cost"]/sc2, orientation="h", marker_color=SC))
        fig2.add_trace(go.Bar(name="Pendapatan", y=cb["lbl"], x=cb["rev"]/sc2, orientation="h", marker_color=SA))
        fig2.update_layout(
            barmode="group", showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=PLOT_TEXT)),
            xaxis=dict(tickformat=",.1f", ticksuffix=sfx2),
            font=dict(color=PLOT_TEXT)
        )
        base(fig2, h=H_CHART, is_cat_y=True)
        st.plotly_chart(fig2, width="stretch", config=CFG)

with r1_col3:
    with st.container(border=True):
        st.markdown('<div class="ct">Profit Margin Cabang</div>', unsafe_allow_html=True)
        nat_margin = ndf["profit_margin"].mean()
        mg = fdf.groupby("branch_name")["profit_margin"].mean().reset_index().sort_values("profit_margin", ascending=True)
        mg["lbl"] = short(mg["branch_name"])
        mcol = [SB if v >= nat_margin else SF for v in mg["profit_margin"]]
        fig3 = go.Figure(go.Bar(
            x=mg["profit_margin"], y=mg["lbl"], orientation="h", marker_color=mcol,
            cliponaxis=False, showlegend=False
        ))
        fig3.add_vline(x=nat_margin, line_dash="dash", line_color=SD)
        fig3.add_annotation(
            x=nat_margin, y=-0.08, yref="paper",
            text=f"- - - Rata-rata Margin ({nat_margin*100:.1f}%)",
            showarrow=False,
            xanchor="left", yanchor="top",
            font=dict(size=8, color=SD),
            align="left",
        )
        x_min = mg["profit_margin"].min()
        fig3.update_layout(
            showlegend=False,
            xaxis=dict(
                showticklabels=False,
                showgrid=True,
                zeroline=True,
                automargin=True,
                range=[x_min * 1.35, mg["profit_margin"].max() * 1.45],
            ),
            font=dict(color=PLOT_TEXT)
        )
        base(fig3, h=H_CHART, is_cat_y=True, lm=80, rm=45)
        fig3.update_layout(margin=dict(b=30))
        st.plotly_chart(fig3, width="stretch", config=CFG)

# ============================================================
# ROW 2: 3 Column Grid
# ============================================================
r2_col1, r2_col2, r2_col3 = st.columns(3)

with r2_col1:
    with st.container(border=True):
        st.markdown('<div class="ct">Rata-rata Nilai Transaksi</div>', unsafe_allow_html=True)
        nat_ticket = ndf["avg_ticket_size"].mean()
        tk = fdf.groupby("branch_name")["avg_ticket_size"].mean().reset_index().sort_values("avg_ticket_size", ascending=True)
        tk["lbl"] = short(tk["branch_name"])
        tkcol = [SA if v >= nat_ticket else SE for v in tk["avg_ticket_size"]]
        sc4, sfx4 = idr_scale(tk["avg_ticket_size"])
        fig4 = go.Figure(go.Bar(
            x=tk["avg_ticket_size"]/sc4, y=tk["lbl"], orientation="h", marker_color=tkcol
        ))
        fig4.add_vline(x=nat_ticket/sc4, line_dash="dash", line_color=SD)
        fig4.update_layout(xaxis=dict(tickformat=",.1f", ticksuffix=sfx4), font=dict(color=PLOT_TEXT))
        base(fig4, h=H_CHART, is_cat_y=True)
        st.plotly_chart(fig4, width="stretch", config=CFG)

with r2_col2:
    with st.container(border=True):
        st.markdown('<div class="ct">Komposisi Channel Penjualan</div>', unsafe_allow_html=True)
        ch = fdf.groupby("branch_name")[["dine_in_percent","delivery_percent","takeaway_percent"]].mean().reset_index().sort_values("dine_in_percent", ascending=True)
        ch["lbl"] = short(ch["branch_name"])
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(name="Dine-in", y=ch["lbl"], x=ch["dine_in_percent"], orientation="h", marker_color=PRIMARY))
        fig6.add_trace(go.Bar(name="Delivery", y=ch["lbl"], x=ch["delivery_percent"], orientation="h", marker_color=SC))
        fig6.add_trace(go.Bar(name="Takeaway", y=ch["lbl"], x=ch["takeaway_percent"], orientation="h", marker_color=SE))
        fig6.update_layout(
            barmode="stack", showlegend=True, 
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=PLOT_TEXT), traceorder="normal"),
            xaxis=dict(ticksuffix="%"), font=dict(color=PLOT_TEXT)
        )
        base(fig6, h=H_CHART, is_cat_y=True)
        st.plotly_chart(fig6, width="stretch", config=CFG)

with r2_col3:
    with st.container(border=True):
        st.markdown('<div class="ct">Transaksi Weekend dan Weekday</div>', unsafe_allow_html=True)
        wd = fdf.groupby(["branch_name","is_weekend"])["total_transactions"].mean().reset_index()
        wd_pivot = wd.pivot(index="branch_name", columns="is_weekend", values="total_transactions")
        if True not in wd_pivot.columns: wd_pivot[True] = 0.0
        if False not in wd_pivot.columns: wd_pivot[False] = 0.0
        wd_pivot = wd_pivot.fillna(0.0).reset_index().rename(columns={False: "Weekday", True: "Weekend"})
        wd_pivot["lbl"]  = short(wd_pivot["branch_name"])
        wd_pivot["diff"] = wd_pivot["Weekend"] - wd_pivot["Weekday"]
        wd_pivot = wd_pivot.sort_values("diff", ascending=True) 
        
        fig7 = go.Figure()
        fig7.add_trace(go.Bar(name="Weekday", y=wd_pivot["lbl"], x=wd_pivot["Weekday"], orientation="h", marker_color=SA))
        fig7.add_trace(go.Bar(name="Weekend", y=wd_pivot["lbl"], x=wd_pivot["Weekend"], orientation="h", marker_color=TEXT_MUTED))
        fig7.update_layout(
            barmode="group", showlegend=True, 
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=PLOT_TEXT)),
            xaxis=dict(title=dict(text="Jumlah Transaksi", font=dict(size=10))),
            font=dict(color=PLOT_TEXT)
        )
        base(fig7, h=H_CHART, is_cat_y=True, bm=30)
        st.plotly_chart(fig7, width="stretch", config=CFG)
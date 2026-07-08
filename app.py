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

def short(series):
    return series.str.title().str.replace("Kopiseru ", "", regex=False)

def short_label(name: str) -> str:
    """Versi single-string dari `short()`, dipakai untuk label checkbox filter cabang."""
    return name.title().replace("Kopiseru ", "")

# ============================================================
# TOP NAVBAR
# ============================================================
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([0.9, 0.8, 1.1, 1.0, 1.3])

with nav_col1:
    st.markdown("<div class='brand-container'>"
                "<div class='brand'>☕ Kopiseru</div>"
                "<div class='brand-sub'>Area Manager Dashboard</div>"
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
    # key="navbar_tipe_cabang" dipakai sebagai hook CSS agar tampilannya
    # konsisten dengan input navbar lain (selectbox, date input), terpisah
    # dari gaya popover kecil "☰" yang dipakai di tiap grafik.
    with st.popover("Tipe Cabang", use_container_width=True, key="navbar_tipe_cabang"):
        selected_types = []
        for bt in branch_types:
            # Gunakan st.checkbox agar user memilih langsung dari list
            if st.checkbox(bt, value=True, key=f"filter_{bt}"):
                selected_types.append(bt)

with nav_col5:
    theme_mode = st.radio("🎨 TEMA", ["Light Mode", "Dark Mode"], index=0, horizontal=True, label_visibility="collapsed")
    is_dark = (theme_mode == "Dark Mode")


# ============================================================
# DESIGN SYSTEM (THEMING VARIABLES) — TEMA BIRU + GRADASI
# ============================================================
if is_dark:
    BG_COLOR = "#0B1220"       # navy hampir hitam
    SIDEBAR_BG = "#0F1B33"     # navy gelap
    CARD_BG = "#122038"        # biru gelap untuk kartu
    BORDER_COLOR = "#1E3A5F"   # biru kebiruan gelap
    TEXT_MAIN = "#EAF2FF"      # putih kebiruan
    TEXT_MUTED = "#8FB3E0"     # biru muda pudar
    GRID_COLOR = "#1B3350"     # biru grid gelap
    PLOT_TEXT = "#EAF2FF"
    TPL = "plotly_dark"
    # Inputs
    SIDEBAR_INPUT_BG = "#122038"
    SIDEBAR_INPUT_TEXT = "#EAF2FF"
    SIDEBAR_INPUT_BORDER = "#1E3A5F"
    # Palette — dasar biru, tapi tiap kategori punya warna sendiri biar tidak "biru semua"
    PRIMARY = "#3B82F6"
    SA = "#60A5FA"   # biru - Pendapatan
    SB = "#34D399"   # hijau - Profit / margin di atas rata-rata (dibiarkan hijau)
    SC = "#94A3B8"   # abu-abu - Biaya / Operasional
    SD = "#818CF8"   # indigo - garis rata-rata (aksen pembeda)
    SE = "#CBD5E1"   # abu-abu muda - kategori sekunder
    SF = "#F87171"   # merah - margin di bawah rata-rata (dibiarkan merah)
    SG = "#22D3EE"   # cyan - aksen
    # Gradasi
    GRADIENT_BG = "linear-gradient(180deg, #0B1220 0%, #0F1B33 55%, #0B1220 100%)"
    GRADIENT_KPI = "linear-gradient(135deg, #16294A 0%, #0F1B33 100%)"
    GRADIENT_BRAND = "linear-gradient(90deg, #60A5FA 0%, #22D3EE 100%)"
    GRADIENT_ACCENT = "linear-gradient(135deg, #3B82F6 0%, #22D3EE 100%)"
    GRADIENT_INPUT = "linear-gradient(135deg, #16294A 0%, #122038 100%)"
else:
    BG_COLOR = "#FFFFFF"       # putih bersih
    SIDEBAR_BG = "#F8FAFC"     # putih keabuan sangat tipis
    CARD_BG = "#FFFFFF"        # putih untuk kartu
    BORDER_COLOR = "#E2E8F0"   # abu-abu muda border
    TEXT_MAIN = "#0F1E3D"      # biru navy gelap
    TEXT_MUTED = "#64748B"     # abu-abu
    GRID_COLOR = "#F1F5F9"     # grid abu-abu sangat muda
    PLOT_TEXT = "#0F1E3D"
    TPL = "plotly_white"
    # Inputs
    SIDEBAR_INPUT_BG = "#F1F5F9"
    SIDEBAR_INPUT_TEXT = "#1E3A8A"
    SIDEBAR_INPUT_BORDER = "#E2E8F0"
    # Palette — dasar biru, tapi tiap kategori punya warna sendiri biar tidak "biru semua"
    PRIMARY = "#1D4ED8"
    SA = "#1E3A8A"   # biru tua - Pendapatan
    SB = "#059669"   # hijau - Profit / margin di atas rata-rata (dibiarkan hijau)
    SC = "#64748B"   # abu-abu - Biaya / Operasional
    SD = "#6366F1"   # indigo - garis rata-rata (aksen pembeda)
    SE = "#94A3B8"   # abu-abu muda - kategori sekunder
    SF = "#DC2626"   # merah - margin di bawah rata-rata (dibiarkan merah)
    SG = "#0EA5E9"   # cyan - aksen
    # Gradasi (background utama dibuat putih bersih, gradasi hanya di elemen aksen)
    GRADIENT_BG = "#FFFFFF"
    GRADIENT_KPI = "linear-gradient(135deg, #FFFFFF 0%, #F1F5F9 100%)"
    GRADIENT_BRAND = "linear-gradient(90deg, #1D4ED8 0%, #0EA5E9 100%)"
    GRADIENT_ACCENT = "linear-gradient(135deg, #1D4ED8 0%, #38BDF8 100%)"
    GRADIENT_INPUT = "linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%)"

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
    padding-top: 0.05rem !important;
    padding-bottom: 0.05rem !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
    max-width: 100% !important;
}}
[data-testid="stHorizontalBlock"] {{ gap: 0.5rem !important; }}
header[data-testid="stHeader"] {{ background: transparent !important; }}

/* Rapatkan jarak vertikal antar baris/blok elemen agar dashboard lebih ringkas */
[data-testid="element-container"], [data-testid="stElementContainer"] {{
    margin-bottom: 0.08rem !important;
}}

/* Dashboard Cards */
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stVerticalBlockBorderWrapper"] > div,
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {{
    background-color: {CARD_BG} !important;
}}
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border: 1px solid {BORDER_COLOR} !important;
    border-radius: 8px !important;
    padding: 0.3rem 0.35rem 0.2rem 0.35rem !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
}}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{
    gap: 0.03rem !important;
}}

/* KPI Strip — Card Box Style dengan gradasi biru */
.kpi-strip {{
    display: flex;
    align-items: stretch;
    gap: 0.5rem;
    margin-bottom: 0.2rem;
}}
.kpi-title-box {{
    flex: 1.2;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 0.25rem 0.7rem;
}}
.kpi-card {{
    flex: 1;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    background: {GRADIENT_KPI};
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
    min-height: 50px;
    padding: 0.3rem 1rem 0.3rem 0.8rem;
    box-shadow: 0 1px 4px rgba(29, 78, 216, 0.12);
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
    position: relative;
    overflow: hidden;
    width: 100%;
}}
.kpi-card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: {GRADIENT_ACCENT};
}}
.kpi-card:hover {{
    box-shadow: 0 4px 14px rgba(29, 78, 216, 0.2);
    border-color: {PRIMARY};
}}

.kpi-body {{ display: flex; flex-direction: column; gap: 0.1rem; }}
.kpi-l {{ font-size:0.65rem; color: {TEXT_MUTED}; text-transform:uppercase; letter-spacing:.06em; font-weight:700; margin:0; }}
.kpi-v {{
    font-size:0.85rem; font-weight:800; line-height:1.2; margin:0;
    background: {GRADIENT_BRAND};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.chart-title{{
    height:0px;
    display:flex;
    align-items:center;

    margin:0 !important;
    padding:0 !important;

    font-size:12px;
    font-weight:700;
    color: {TEXT_MAIN};
}}

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
.ct  {{
    display: block;
    font-size: 0.72rem;
    font-weight: 700;
    color: {TEXT_MAIN};
    letter-spacing: -.01em;
    background: {GRADIENT_KPI};
    border: 1px solid {BORDER_COLOR};
    border-left: 3px solid {PRIMARY};
    border-radius: 5px;
    padding: 2px 8px 2px 7px;
    margin: 0 0 0.15rem 0;
    line-height: 1.6;
}}

/* Navbar brand styling */
.brand {{ font-size:1.4rem; font-weight:800; color: {PRIMARY}; letter-spacing:-.02em; line-height:1.1; margin:0; padding:0; }}
.brand-sub {{ font-size:0.75rem; color: {TEXT_MUTED}; font-weight: 600; line-height:1.1; margin:0; padding:0; }}
.brand-container {{ display: flex; flex-direction: column; justify-content: center; height: 34px; padding-left: 0.2rem; }}

/* ==============================================================
   INPUT UNIFICATION (Select, Date, Popover)
============================================================== */
div[data-baseweb="select"] > div {{
    background-color: {SIDEBAR_INPUT_BG} !important;
    border: 1px solid {SIDEBAR_INPUT_BORDER} !important;
    border-radius: 8px !important;
    min-height: 34px !important;
    height: 34px !important;
    box-shadow: none !important;
    transition: border-color 0.2s ease !important;
}}
div[data-baseweb="select"] > div:hover {{
    border-color: {PRIMARY} !important;
}}

div[data-baseweb="input"] {{
    background-color: {SIDEBAR_INPUT_BG} !important;
    border: 1px solid {SIDEBAR_INPUT_BORDER} !important;
    border-radius: 8px !important;
    min-height: 34px !important;
    height: 34px !important;
    box-shadow: none !important;
    transition: border-color 0.2s ease !important;
}}
div[data-baseweb="input"]:hover {{
    border-color: {PRIMARY} !important;
}}

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

div[data-baseweb="base-input"] {{
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    min-height: unset !important;
    height: unset !important;
}}

div[data-baseweb="select"] div,
div[data-baseweb="select"] span {{
    color: {SIDEBAR_INPUT_TEXT} !important;
    font-weight: 500 !important;
}}

div[data-testid="stPopover"]{{
    display:flex;
    justify-content:flex-end;
    align-items:center;
    height:32px;
}}

div[data-testid="stPopover"] button {{
    background-color: {SIDEBAR_INPUT_BG} !important;
    color: {SIDEBAR_INPUT_TEXT} !important;
    border: 1px solid {SIDEBAR_INPUT_BORDER} !important;

    width: 38px !important;
    height: 26px !important;
    min-width: 38px !important;
    min-height: 26px !important;
    max-height: 26px !important;

    padding: 0 !important;

    line-height: 1 !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 2px !important;
    padding: 0 6px !important;
}}

div[data-testid="stPopover"] button > div:first-child {{
    flex-grow: 1 !important;
    display: flex !important;
    justify-content: flex-start !important;
    align-items: center !important;
}}

div[data-testid="stPopover"] button p {{
    color: {SIDEBAR_INPUT_TEXT} !important;
    margin: 0 !important;
    text-align: left !important;
}}

div[data-testid="stPopover"] button:focus {{
    border-color: {PRIMARY} !important;
    box-shadow: none !important;
}}

[data-testid="stPopoverBody"] {{
    background-color: {SIDEBAR_INPUT_BG} !important;
    border: 1px solid {SIDEBAR_INPUT_BORDER} !important;
    border-radius: 8px !important;
    padding: 10px !important;
}}

[data-testid="stPopoverBody"] > div {{
    background-color: transparent !important;
}}

/* ==============================================================
   NAVBAR "TIPE CABANG" & "CABANG" POPOVER — dibuat berbeda dari
   popover "☰" yang dulu dipakai di tiap grafik, disamakan dengan
   gaya input navbar lain (selectbox provinsi & date input). Filter
   cabang sekarang berlaku global untuk semua grafik.
============================================================== */
.st-key-navbar_tipe_cabang [data-testid="stPopover"] {{
    display: block !important;
    justify-content: unset !important;
    height: auto !important;
    width: 100% !important;
}}
.st-key-navbar_tipe_cabang [data-testid="stPopover"] button {{
    width: 100% !important;
    height: 34px !important;
    min-width: unset !important;
    min-height: 34px !important;
    max-height: 34px !important;
    background-color: {SIDEBAR_INPUT_BG} !important;
    color: {SIDEBAR_INPUT_TEXT} !important;
    border: 1px solid {SIDEBAR_INPUT_BORDER} !important;
    border-radius: 8px !important;
    padding: 0 12px !important;
    box-shadow: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 6px !important;
    transition: border-color 0.2s ease !important;
}}
.st-key-navbar_tipe_cabang [data-testid="stPopover"] button:hover {{
    border-color: {PRIMARY} !important;
}}
.st-key-navbar_tipe_cabang [data-testid="stPopover"] button:focus {{
    border-color: {PRIMARY} !important;
    box-shadow: none !important;
}}
.st-key-navbar_tipe_cabang [data-testid="stPopover"] button > div:first-child {{
    flex-grow: 1 !important;
    display: flex !important;
    justify-content: flex-start !important;
    align-items: center !important;
}}
.st-key-navbar_tipe_cabang [data-testid="stPopover"] button p {{
    font-size: 14px !important;
    font-weight: 500 !important;
    color: {SIDEBAR_INPUT_TEXT} !important;
    text-align: left !important;
    margin: 0 !important;
}}
.st-key-navbar_tipe_cabang [data-testid="stPopover"] button::after {{
    content: "▾";
    font-size: 11px;
    color: {TEXT_MUTED};
    flex-shrink: 0;
}}
.st-key-navbar_tipe_cabang [data-testid="stPopoverBody"] {{
    min-width: 220px !important;
    max-height: 320px !important;
    overflow-y: auto !important;
}}

/* ==============================================================
   TOMBOL FILTER CABANG DI SAMPING KPI STRIP — dibuat kecil (bukan
   full-width seperti input navbar) supaya tidak memakan tempat.
   Filter ini tetap berlaku global untuk semua grafik & KPI.
============================================================== */
.st-key-kpi_cabang_filter {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    height: 100% !important;
    margin-top: 10px !important;
}}
.st-key-kpi_cabang_filter [data-testid="stPopover"] {{
    display: block !important;
    height: auto !important;
    width: auto !important;
}}
.st-key-kpi_cabang_filter [data-testid="stPopover"] button {{
    height: 28px !important;
    min-height: 28px !important;
    max-height: 28px !important;
    width: auto !important;
    min-width: unset !important;
    background-color: {SIDEBAR_INPUT_BG} !important;
    color: {SIDEBAR_INPUT_TEXT} !important;
    border: 1px solid {SIDEBAR_INPUT_BORDER} !important;
    border-radius: 7px !important;
    padding: 0 10px !important;
    box-shadow: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 4px !important;
    transition: border-color 0.2s ease !important;
}}
.st-key-kpi_cabang_filter [data-testid="stPopover"] button:hover {{
    border-color: {PRIMARY} !important;
}}
.st-key-kpi_cabang_filter [data-testid="stPopover"] button:focus {{
    border-color: {PRIMARY} !important;
    box-shadow: none !important;
}}
.st-key-kpi_cabang_filter [data-testid="stPopover"] button p {{
    font-size: 12px !important;
    font-weight: 600 !important;
    color: {SIDEBAR_INPUT_TEXT} !important;
    margin: 0 !important;
    white-space: nowrap !important;
}}
.st-key-kpi_cabang_filter [data-testid="stPopover"] button::after {{
    content: "▾";
    font-size: 10px;
    color: {TEXT_MUTED};
    flex-shrink: 0;
}}
.st-key-kpi_cabang_filter [data-testid="stPopoverBody"] {{
    min-width: 200px !important;
    max-height: 300px !important;
    overflow-y: auto !important;
}}

div[data-testid="stCheckbox"] label p,
div[data-testid="stRadio"] label p {{
    color: {TEXT_MAIN} !important;
}}

/* CHECKBOX KUSTOM */
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

/* RADIO BUTTON */
div[data-testid="stRadio"] > div {{
    display: flex !important;
    align-items: center !important;
    height: 34px !important;
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
# CUSTOM DIVIDER
# ============================================================
st.markdown(f'<hr style="margin-top: -0.4rem; margin-bottom: 0.25rem; border: none; border-top: 1px solid {BORDER_COLOR};">', unsafe_allow_html=True)


# ============================================================
# BARIS KPI
# ============================================================

header_col, kpi_col_rev, kpi_col_prof, kpi_col_margin, kpi_col_best = st.columns(
    [3.0, 1.2, 1.2, 1.2, 1.3]
)

# ============================================================
# DATA FILTER CABANG
# ============================================================

branch_options = sorted(
    df[
        (df["branch_province"].str.lower() == selected_province.lower())
        & (df["branch_type"].isin(selected_types))
    ]["branch_name"].unique()
)

# simpan state filter
if "selected_branches" not in st.session_state:
    st.session_state.selected_branches = branch_options.copy()

# jika daftar cabang berubah karena filter provinsi / tipe
st.session_state.selected_branches = [
    b for b in st.session_state.selected_branches
    if b in branch_options
]

if not st.session_state.selected_branches:
    st.session_state.selected_branches = branch_options.copy()

# ============================================================
# HEADER
# ============================================================

with header_col:

    left_title, right_filter = st.columns([4.3, 1])

    with left_title:

        # sementara tampilkan jumlah semua cabang dulu
        n_cabang = len(st.session_state.selected_branches)

        st.markdown(
            f"""
            <div class="kpi-title-box">
                <div class="dash-title">
                    {selected_province.title()} — {n_cabang} Cabang
                </div>
                <div class="dash-sub">
                    {start_date.strftime('%d %b %y')} – {end_date.strftime('%d %b %y')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_filter:

        with st.popover("Cabang", key="kpi_cabang_filter"):

            temp = []

            for b in branch_options:

                checked = st.checkbox(
                    short_label(b),
                    value=b in st.session_state.selected_branches,
                    key=f"branch_filter_{b}"
                )

                if checked:
                    temp.append(b)

            if temp:
                st.session_state.selected_branches = temp

selected_branches = st.session_state.selected_branches

# ============================================================
# FILTER DATA
# ============================================================

start_ts = pd.Timestamp(start_date)
end_ts = pd.Timestamp(end_date)

ndf = df[
    (df["date"] >= start_ts)
    & (df["date"] <= end_ts)
    & (df["branch_type"].isin(selected_types))
]

fdf = ndf[
    (ndf["branch_province"].str.lower() == selected_province.lower())
    & (ndf["branch_name"].isin(selected_branches))
]

n_cabang = fdf["branch_name"].nunique()

if fdf.empty:
    st.warning("Tidak ada data.")
    st.stop()

# ============================================================
# KPI
# ============================================================

total_rev = fdf["total_revenue"].sum()
total_prof = fdf["profit"].sum()
avg_margin = fdf["profit_margin"].mean()


# ============================================================
# BRANCH TERLAKU
# ============================================================

branch_profit = (
    fdf.groupby("branch_name", as_index=False)
       .agg(total_profit=("profit", "sum"))
       .sort_values("total_profit", ascending=False)
)

if not branch_profit.empty:
    best_branch = short_label(branch_profit.iloc[0]["branch_name"])
    best_profit = branch_profit.iloc[0]["total_profit"]
else:
    best_branch = "-"
    best_profit = 0

# ============================================================
# UPDATE TITLE
# ============================================================

with kpi_col_rev:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-body">
            <div class="kpi-l">Total Pendapatan</div>
            <div class="kpi-v">{fmt_idr(total_rev)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col_prof:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-body">
            <div class="kpi-l">Total Laba</div>
            <div class="kpi-v">{fmt_idr(total_prof)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col_margin:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-body">
            <div class="kpi-l">Rata-rata Margin Laba</div>
            <div class="kpi-v">{avg_margin*100:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col_best:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-body">
            <div class="kpi-l">Cabang Terlaris</div>
            <div class="kpi-v">{best_branch}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# SHARED HELPERS & COLOR PALETTE
# ============================================================
BG   = "rgba(0,0,0,0)"
CFG  = {"displayModeBar": False}
H_CHART = 215

def base(fig, h, lm=0, rm=0, bm=0, is_cat_y=False):
    fig.update_layout(
        height=h, paper_bgcolor=BG, plot_bgcolor=BG,
        template=TPL, margin=dict(l=lm, r=rm, t=2, b=bm),
        font=dict(family="Plus Jakarta Sans", size=9, color=PLOT_TEXT),
        hoverlabel=dict(bgcolor=CARD_BG, bordercolor=BORDER_COLOR, font=dict(family="Plus Jakarta Sans", size=11, color=TEXT_MAIN)),
    )
    fig.update_xaxes(
        gridcolor=GRID_COLOR, linecolor=BORDER_COLOR, zeroline=False,
        tickfont=dict(color=PLOT_TEXT, size=9), title_font=dict(color=PLOT_TEXT, size=9)
    )
    if is_cat_y:
        fig.update_yaxes(
            gridcolor=GRID_COLOR, linecolor=BORDER_COLOR, zeroline=False,
            type="category", dtick=1, automargin=True,
            tickfont=dict(color=PLOT_TEXT, size=9), title_font=dict(color=PLOT_TEXT, size=9)
        )
    else:
        fig.update_yaxes(
            gridcolor=GRID_COLOR, linecolor=BORDER_COLOR, zeroline=False,
            tickfont=dict(color=PLOT_TEXT, size=9), title_font=dict(color=PLOT_TEXT, size=9)
        )
    fig.update_layout(legend=dict(valign="middle"))
    return fig

# ============================================================
# ROW 1: 3 Column Grid
# ============================================================
r1_col1, r1_col2, r1_col3 = st.columns(3)

with r1_col1:
    with st.container():
        st.markdown('<div class="ct">Tren Pendapatan, Biaya & Profit</div>', unsafe_allow_html=True)

        tr = (fdf.set_index("date").resample("ME")
              .agg(rev=("total_revenue","sum"), cost=("operating_cost","sum"), prof=("profit","sum"))
              .reset_index())
        sc1, sfx1 = idr_scale(tr[["rev","cost","prof"]].stack())
        fig1 = go.Figure()
        # Area gradasi untuk Pendapatan (fill di bawah garis)
        fig1.add_trace(go.Scatter(
            x=tr["date"], y=tr["rev"]/sc1, name="Pendapatan", mode="lines",
            line=dict(color=SA, width=2.5),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.15)"
        ))
        fig1.add_trace(go.Scatter(
            x=tr["date"], y=tr["cost"]/sc1, name="Biaya", mode="lines",
            line=dict(color=SC, width=2, dash="dot")
        ))
        fig1.add_trace(go.Scatter(
            x=tr["date"], y=tr["prof"]/sc1, name="Profit", mode="lines",
            line=dict(color=SB, width=2.5),
            fill="tozeroy", fillcolor="rgba(14,165,233,0.12)"
        ))
        fig1.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, font=dict(size=9, color=PLOT_TEXT)),
            xaxis=dict(tickformat="%Y"),
            yaxis=dict(title=dict(text=f"Nilai Rupiah ({sfx1.strip()})", font=dict(size=9, color=PLOT_TEXT)), tickformat=",.1f"),
        )
        base(fig1, h=H_CHART, lm=55)
        st.plotly_chart(fig1, width="stretch", config=CFG)

with r1_col2:
    with st.container():
        st.markdown('<div class="ct">Pendapatan dan Biaya per Cabang</div>', unsafe_allow_html=True)

        cb = fdf.groupby("branch_name").agg(rev=("total_revenue","sum"), cost=("operating_cost","sum")).reset_index().sort_values("rev", ascending=True)
        cb["lbl"] = short(cb["branch_name"])

        if len(cb) == 1:
            rev_val = cb.iloc[0]["rev"]
            cost_val = cb.iloc[0]["cost"]
            fig2 = go.Figure(data=[go.Pie(
                labels=["Pendapatan", "Biaya"],
                values=[rev_val, cost_val],
                hole=0.62,
                marker=dict(colors=[SA, SC]),
                textinfo="percent",
                textposition="inside",
                sort=False
            )])
            fig2.update_layout(
                showlegend=True,
                legend=dict(orientation="h", x=0, y=0.99, xanchor="left", yanchor="bottom", font=dict(size=9, color=PLOT_TEXT), tracegroupgap=4),
                font=dict(color=PLOT_TEXT),
                margin=dict(l=0, r=0, t=0, b=22)
            )
            fig2.update_traces(domain=dict(x=[0.28, 0.72], y=[0.16, 0.92]))
            base(fig2, h=H_CHART)
        else:
            sc2, sfx2 = idr_scale(cb[["rev","cost"]].stack())
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                name="Biaya", y=cb["lbl"], x=cb["cost"]/sc2, orientation="h",
                marker_color=SC
            ))
            fig2.add_trace(go.Bar(
                name="Pendapatan", y=cb["lbl"], x=cb["rev"]/sc2, orientation="h",
                marker_color=SA
            ))
            fig2.update_layout(
                barmode="group", showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, font=dict(size=9, color=PLOT_TEXT)),
                xaxis=dict(tickformat=",.1f", ticksuffix=sfx2),
                font=dict(color=PLOT_TEXT)
            )
            base(fig2, h=H_CHART, is_cat_y=True)

        st.plotly_chart(fig2, width="stretch", config=CFG)

with r1_col3:
    with st.container():
        st.markdown('<div class="ct">Profit Margin Cabang</div>', unsafe_allow_html=True)

        # Average Margin
        nat_margin = ndf["profit_margin"].mean()

        # Data
        mg = (
            fdf.groupby("branch_name")["profit_margin"]
            .mean()
            .reset_index()
            .sort_values("profit_margin", ascending=True)
        )

        mg["lbl"] = short(mg["branch_name"])

        # Pisahkan menjadi dua trace agar muncul legenda
        mg_green = mg.copy()
        mg_green["value"] = mg_green["profit_margin"].where(
            mg_green["profit_margin"] >= nat_margin
        )

        mg_red = mg.copy()
        mg_red["value"] = mg_red["profit_margin"].where(
            mg_red["profit_margin"] < nat_margin
        )

        fig3 = go.Figure()

        # Bar merah (Di Bawah Rata-rata) — nilai dalam %
        fig3.add_trace(
            go.Bar(
                x=mg_red["value"] * 100,
                y=mg_red["lbl"],
                orientation="h",
                marker_color=SF,
                name="Di Bawah Rata-rata",
            )
        )

        # Bar hijau (Di Atas Rata-rata) — nilai dalam %
        fig3.add_trace(
            go.Bar(
                x=mg_green["value"] * 100,
                y=mg_green["lbl"],
                orientation="h",
                marker_color=SB,
                name="Di Atas Rata-rata",
            )
        )

        # Garis Average
        fig3.add_vline(
            x=nat_margin * 100,
            line_dash="dash",
            line_color=SD,
            line_width=2,
        )

        fig3.add_annotation(
            xref="paper",
            yref="paper",
            x=1.0,
            y=-0.22,
            text=f"— Rata-rata Margin Nasional: {nat_margin*100:.1f}%",
            showarrow=False,
            xanchor="right",
            yanchor="top",
            font=dict(size=8.5, color=SD),
        )

        mg_min = mg["profit_margin"].min() * 100
        mg_max = mg["profit_margin"].max() * 100

        if len(mg) == 1:
            lo = min(mg_min, nat_margin * 100, 0)
            hi = max(mg_max, nat_margin * 100, 0)
            span = hi - lo
            pad = span * 0.4 if span > 0 else max(abs(hi), 2) * 0.4
            x_range = [lo - pad * 0.5, hi + pad]
        else:
            x_range = [mg_min * 0.7, mg_max * 1.25]

        fig3.update_layout(
            barmode="overlay",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.01,
                x=0,
                font=dict(size=9, color=PLOT_TEXT),
            ),
            xaxis=dict(
                showticklabels=True,
                ticksuffix="%",
                tickfont=dict(size=8, color=PLOT_TEXT),
                showgrid=True,
                zeroline=True,
                automargin=True,
                range=x_range,
            ),
            font=dict(color=PLOT_TEXT),
        )

        base(fig3, h=H_CHART, is_cat_y=True, lm=80, rm=45)
        fig3.update_layout(margin=dict(b=52))

        st.plotly_chart(fig3, width="stretch", config=CFG)

# ============================================================
# ROW 2: 3 Column Grid
# ============================================================
r2_col1, r2_col2, r2_col3 = st.columns(3)

with r2_col1:
    with st.container():
        st.markdown('<div class="ct">Rata-rata Nilai Transaksi</div>', unsafe_allow_html=True)

        nat_ticket = ndf["avg_ticket_size"].mean()
        tk = fdf.groupby("branch_name")["avg_ticket_size"].mean().reset_index().sort_values("avg_ticket_size", ascending=True)
        tk["lbl"] = short(tk["branch_name"])

        if len(tk) == 1:
            branch_val = tk.iloc[0]["avg_ticket_size"]
            fig4 = go.Figure(data=[go.Pie(
                labels=["Cabang Ini", "Rata-rata Nasional"],
                values=[branch_val, nat_ticket],
                hole=0.62,
                marker=dict(colors=[TEXT_MAIN, TEXT_MUTED]),
                textinfo="percent",
                textposition="inside",
                sort=False
            )])
            fig4.update_layout(
                showlegend=True,
                legend=dict(orientation="h", x=0, y=0.99, xanchor="left", yanchor="bottom", font=dict(size=9, color=PLOT_TEXT), tracegroupgap=4),
                font=dict(color=PLOT_TEXT),
                margin=dict(l=0, r=0, t=0, b=22)
            )
            fig4.update_traces(domain=dict(x=[0.28, 0.72], y=[0.16, 0.92]))
            base(fig4, h=H_CHART)
        else:
            tkcol = [SA if v >= nat_ticket else SC for v in tk["avg_ticket_size"]]
            sc4, sfx4 = idr_scale(tk["avg_ticket_size"])
            fig4 = go.Figure(go.Bar(
                x=tk["avg_ticket_size"]/sc4, y=tk["lbl"], orientation="h", marker_color=tkcol
            ))
            fig4.add_vline(x=nat_ticket/sc4, line_dash="dash", line_color=SD)
            fig4.add_annotation(
                xref="paper",
                yref="paper",
                x=1.0,
                y=-0.22,
                text=f"— Rata-rata Transaksi Nasional: {fmt_idr(nat_ticket)}",
                showarrow=False,
                xanchor="right",
                yanchor="top",
                font=dict(size=8.5, color=SD),
            )
            base(fig4, h=H_CHART, is_cat_y=True)
            fig4.update_layout(margin=dict(b=52))

        st.plotly_chart(fig4, width="stretch", config=CFG)

with r2_col2:
    with st.container():
        st.markdown('<div class="ct">Komposisi Channel Penjualan</div>', unsafe_allow_html=True)

        ch = fdf.groupby("branch_name")[["dine_in_percent","delivery_percent","takeaway_percent"]].mean().reset_index().sort_values("dine_in_percent", ascending=True)
        ch["lbl"] = short(ch["branch_name"])

        if len(ch) == 1:
            dine_val = ch.iloc[0]["dine_in_percent"]
            del_val = ch.iloc[0]["delivery_percent"]
            tk_val = ch.iloc[0]["takeaway_percent"]
            fig6 = go.Figure(data=[go.Pie(
                labels=["Dine-in", "Delivery", "Takeaway"],
                values=[dine_val, del_val, tk_val],
                hole=0.62,
                marker=dict(colors=[SA, SG, SC]),
                textinfo="percent",
                textposition="inside",
                sort=False
            )])
            fig6.update_layout(
                showlegend=True,
                legend=dict(orientation="h", x=0, y=0.99, xanchor="left", yanchor="bottom", font=dict(size=9, color=PLOT_TEXT), tracegroupgap=4),
                font=dict(color=PLOT_TEXT),
                margin=dict(l=0, r=0, t=0, b=22)
            )
            fig6.update_traces(domain=dict(x=[0.28, 0.72], y=[0.16, 0.92]))
            base(fig6, h=H_CHART)
        else:
            fig6 = go.Figure()
            fig6.add_trace(go.Bar(name="Dine-in", y=ch["lbl"], x=ch["dine_in_percent"], orientation="h", marker_color=SA))
            fig6.add_trace(go.Bar(name="Delivery", y=ch["lbl"], x=ch["delivery_percent"], orientation="h", marker_color=SG))
            fig6.add_trace(go.Bar(name="Takeaway", y=ch["lbl"], x=ch["takeaway_percent"], orientation="h", marker_color=SC))
            fig6.update_layout(
                barmode="stack", showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, font=dict(size=9, color=PLOT_TEXT), traceorder="normal"),
                xaxis=dict(ticksuffix="%"), font=dict(color=PLOT_TEXT)
            )
            base(fig6, h=H_CHART, is_cat_y=True)

        st.plotly_chart(fig6, width="stretch", config=CFG)

with r2_col3:
    with st.container():
        st.markdown(
            '<div class="ct">Transaksi Hari Kerja dan Akhir Pekan</div>',
            unsafe_allow_html=True
        )

        # ============================
        # Data
        # ============================
        chart_df = fdf
        wd = (
            chart_df
            .groupby(["branch_name", "is_weekend"])["total_transactions"]
            .mean()
            .reset_index()
        )
        wd_pivot = (
            wd.pivot(
                index="branch_name",
                columns="is_weekend",
                values="total_transactions"
            )
            .fillna(0)
        )
        if True not in wd_pivot.columns:
            wd_pivot[True] = 0
        if False not in wd_pivot.columns:
            wd_pivot[False] = 0
        wd_pivot = (
            wd_pivot
            .reset_index()
            .rename(columns={
                False: "Hari Kerja",
                True: "Akhir Pekan"
            })
        )
        wd_pivot["lbl"] = short(wd_pivot["branch_name"])
        # ============================
        # PIE CHART
        # ============================
        if len(wd_pivot) == 1:
            weekend = wd_pivot.iloc[0]["Akhir Pekan"]
            weekday = wd_pivot.iloc[0]["Hari Kerja"]
            fig7 = go.Figure(
                data=[
                    go.Pie(
                        labels=["Hari Kerja", "Akhir Pekan"],
                        values=[weekday, weekend],

                        hole=0.62,

                        marker=dict(
                            colors=[TEXT_MAIN, TEXT_MUTED]
                        ),

                        textinfo="percent",

                        textposition="inside",

                        sort=False
                    )
                ]
            )
            fig7.update_layout(
                barmode="group",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    x=0,
                    y=0.99,
                    xanchor="left",
                    yanchor="bottom",
                    font=dict(
                        size=9,
                        color=PLOT_TEXT
                    ),
                    tracegroupgap=4,
                ),
                xaxis=dict(
                    title=dict(
                        text="Jumlah Transaksi",
                        font=dict(
                            size=9,
                            color=PLOT_TEXT
                        )
                    )
                ),
                font=dict(color=PLOT_TEXT),
                margin=dict(
                    l=0,
                    r=0,
                    t=0,
                    b=22
                )
            )
            fig7.update_traces(
                domain=dict(
                    x=[0.28, 0.72],
                    y=[0.16, 0.92]
                )
            )
            base(fig7, h=H_CHART)
        else:
            wd_pivot["diff"] = (
                wd_pivot["Akhir Pekan"] -
                wd_pivot["Hari Kerja"]
            )
            wd_pivot = wd_pivot.sort_values(
                "diff",
                ascending=True
            )

            fig7 = go.Figure()

            fig7.add_trace(
                go.Bar(
                    name="Hari Kerja",
                    y=wd_pivot["lbl"],
                    x=wd_pivot["Hari Kerja"],
                    orientation="h",
                    marker_color=TEXT_MAIN,
                )
            )

            fig7.add_trace(
                go.Bar(
                    name="Akhir Pekan",
                    y=wd_pivot["lbl"],
                    x=wd_pivot["Akhir Pekan"],
                    orientation="h",
                    marker_color=TEXT_MUTED,
                )
            )

            base(
                fig7,
                h=H_CHART,
                is_cat_y=True,
                bm=22
            )
            fig7.update_xaxes(
                title=dict(
                    text="Jumlah Transaksi",
                    font=dict(size=9, color=PLOT_TEXT),
                    standoff=10
                ),
                title_standoff=15
            )
            fig7.update_layout(
                barmode="group",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    x=0,
                    y=1.005,
                    xanchor="left",
                    yanchor="bottom",
                    font=dict(
                        size=9,
                        color=PLOT_TEXT
                    ),
                    bgcolor="rgba(0,0,0,0)"
                ),
                margin=dict(
                    l=0,
                    r=0,
                    t=0,
                    b=22
                )
            )

            fig7.update_yaxes(
                domain=[0.10, 1.00]
            )
        st.plotly_chart(
            fig7,
            width="stretch",
            config=CFG
        )
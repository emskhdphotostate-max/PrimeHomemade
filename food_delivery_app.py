import streamlit as st
from supabase import create_client, Client
import urllib.parse
import webbrowser
import ast
from datetime import datetime, date, timedelta
import pandas as pd

# ============================================================
# SUPABASE CONFIGURATION
# ============================================================
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"

@st.cache_resource
def init_supabase() -> Client:
    if SUPABASE_URL == "YOUR_SUPABASE_URL":
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="Homemade Kitchen | Fine Home Dining", layout="wide", page_icon="🥂", initial_sidebar_state="collapsed")

# ============================================================
# CSS — VIP / PREMIUM THEME
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --gold: #cda86a;
        --gold-light: #e6cd9a;
        --gold-deep: #a9833f;
        --wine: #6e1423;
        --ink: #0a0a0c;
        --panel: #131217;
        --panel-2: #17151b;
        --line: rgba(205,168,106,0.18);
        --text: #f3ecdd;
        --text-dim: #a79c8a;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, h5, h6 { font-family: 'Playfair Display', serif !important; letter-spacing: 0.2px; }

    /* ---------- Streamlit's own top toolbar: make it blend with dark theme ---------- */
    header[data-testid="stHeader"] {
        background: #0a0910 !important;
        box-shadow: none !important;
        border-bottom: 1px solid rgba(205,168,106,0.12);
    }
    header[data-testid="stHeader"] * { color: var(--text) !important; fill: var(--text) !important; }
    div[data-testid="stToolbar"] { color: var(--text) !important; }
    div[data-testid="stDecoration"] { background: linear-gradient(90deg, var(--gold-deep), var(--gold-light), var(--gold-deep)) !important; }
    #MainMenu { color: var(--text) !important; }

    /* Give enough clearance below the fixed header so nothing hides behind it */
    .block-container { padding-top: 5.5rem !important; max-width: 1200px; position: relative; z-index: 1; }

    /* ---------- Floating decorative food icons in the empty side gutters ---------- */
    .food-float {
        position: fixed; top: 0; height: 100vh; width: 90px;
        pointer-events: none; z-index: 0; overflow: hidden;
    }
    .food-float.left { left: 0; }
    .food-float.right { right: 0; }
    .food-float span {
        position: absolute; font-size: 1.9rem; opacity: 0.16;
        filter: grayscale(15%) drop-shadow(0 0 6px rgba(205,168,106,0.25));
        animation: floatY 9s ease-in-out infinite;
    }
    @keyframes floatY {
        0%   { transform: translateY(0px) rotate(-4deg); }
        50%  { transform: translateY(-26px) rotate(4deg); }
        100% { transform: translateY(0px) rotate(-4deg); }
    }

    /* ---------- App background ---------- */
    .stApp {
        background:
            radial-gradient(1100px 550px at 12% -6%, rgba(205,168,106,0.09), transparent 55%),
            radial-gradient(900px 500px at 100% 0%, rgba(110,20,35,0.16), transparent 50%),
            linear-gradient(180deg, #08070a 0%, #0d0c10 55%, #0a0910 100%);
        color: var(--text) !important;
    }
    h1, h2, h3, h4, h5, h6, p, span, label, div { color: var(--text); }

    ::selection { background: rgba(205,168,106,0.35); }

    /* ---------- Hide default sidebar (we use a top navbar) ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #100e12, #17121a) !important;
        border-right: 1px solid var(--line);
    }

    /* ---------- Top navbar ---------- */
    .vip-topbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 14px 26px;
        margin: -1rem -1rem 22px -1rem;
        background: linear-gradient(180deg, rgba(19,18,23,0.95), rgba(15,14,18,0.85));
        border-bottom: 1px solid var(--line);
        backdrop-filter: blur(6px);
    }
    .vip-brand { display:flex; align-items:center; gap:12px; }
    .vip-brand .mark {
        width: 42px; height: 42px; border-radius: 50%;
        display:flex; align-items:center; justify-content:center;
        background: linear-gradient(135deg, var(--gold-light), var(--gold-deep));
        color: #1a1408 !important; font-size: 20px; font-weight:800;
        box-shadow: 0 0 0 1px rgba(205,168,106,0.4), 0 6px 18px rgba(205,168,106,0.25);
    }
    .vip-brand .name { font-family:'Playfair Display', serif; font-size: 1.35rem; font-weight:800; color: var(--gold-light) !important; line-height:1.1; }
    .vip-brand .tag { font-size: 0.68rem; letter-spacing: 2.5px; text-transform: uppercase; color: var(--text-dim) !important; }

    /* Segmented nav (built from a horizontal radio) */
    div[data-testid="stRadio"] { background: transparent; }
    div[role="radiogroup"] {
        display:flex; gap:4px; flex-wrap: wrap; background: rgba(255,255,255,0.035);
        border: 1px solid var(--line); border-radius: 999px; padding: 6px;
    }
    div[role="radiogroup"] label {
        border-radius: 999px !important; padding: 6px 16px !important; margin:0 !important;
        transition: background .18s ease; cursor:pointer;
    }
    div[role="radiogroup"] label:hover { background: rgba(205,168,106,0.1); }
    div[role="radiogroup"] label p {
        font-size: 0.85rem !important; font-weight:600 !important; letter-spacing:.3px;
        color: var(--text-dim) !important;
    }
    div[role="radiogroup"] input:checked + div svg,
    div[role="radiogroup"] [aria-checked="true"] svg { fill: var(--gold) !important; }
    div[role="radiogroup"] label:has(input:checked) { background: rgba(205,168,106,0.16); }
    div[role="radiogroup"] label:has(input:checked) p { color: var(--gold-light) !important; }

    /* ---------- Hero banner ---------- */
    .hero-banner {
        position: relative; overflow:hidden;
        background:
            radial-gradient(600px 260px at 85% -20%, rgba(205,168,106,0.25), transparent 60%),
            linear-gradient(135deg, #1a1620 0%, #241119 60%, #1a1620 100%);
        border: 1px solid var(--line);
        padding: 46px 32px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.45);
    }
    .hero-eyebrow {
        display:inline-block; font-size:0.7rem; letter-spacing:4px; text-transform:uppercase;
        color: var(--gold-light) !important; margin-bottom:10px; font-weight:600;
    }
    .hero-banner h1 {
        font-size: 2.6rem; font-weight: 800; margin: 0 0 10px 0;
        background: linear-gradient(135deg, #fff, var(--gold-light) 60%, var(--gold-deep));
        -webkit-background-clip: text; background-clip:text; -webkit-text-fill-color: transparent;
    }
    .hero-banner p { font-weight: 400; color: var(--text-dim) !important; font-size:0.98rem; margin: 4px 0; }
    .hero-divider { width:64px; height:2px; margin:16px auto; background: linear-gradient(90deg, transparent, var(--gold), transparent); }

    /* ---------- Section labels ---------- */
    .section-label {
        font-family:'Playfair Display', serif; font-size:1.4rem; font-weight:700;
        color: var(--text) !important; margin: 6px 0 16px 0;
        display:flex; align-items:center; gap:10px;
    }
    .section-label::after { content:""; flex:1; height:1px; background: var(--line); }

    /* ---------- Card style for menu items ---------- */
    .menu-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.015));
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 18px;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color .18s ease;
    }
    .menu-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 14px 30px rgba(0,0,0,0.45);
        border-color: rgba(205,168,106,0.55);
    }
    .menu-card img { border-radius: 12px !important; }
    .dish-name { font-family:'Playfair Display', serif; font-size:1.18rem; font-weight:700; margin: 2px 0 4px 0; color: var(--text) !important; }
    .dish-desc { color: var(--text-dim) !important; font-size:0.87rem; line-height:1.5; min-height: 2.6em; }

    .price-badge {
        display: inline-block;
        background: transparent;
        border: 1px solid var(--gold);
        color: var(--gold-light) !important;
        font-weight: 700;
        letter-spacing: .3px;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.92rem;
    }

    /* ---------- Buttons ---------- */
    .stButton button, div.stFormSubmitButton > button {
        background: linear-gradient(135deg, var(--gold-light), var(--gold-deep)) !important;
        color: #1a1408 !important;
        font-weight: 700 !important;
        letter-spacing: .3px;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 6px 16px rgba(205,168,106,0.25) !important;
        transition: all 0.15s ease !important;
    }
    .stButton button:hover, div.stFormSubmitButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(205,168,106,0.4) !important;
        filter: brightness(1.05);
    }
    .stButton button p, div.stFormSubmitButton > button p { color: #1a1408 !important; font-weight:700 !important; }

    /* Logout / secondary look for the small top-right button */
    section.main div[data-testid="stVerticalBlock"] div[data-testid="column"]:last-child .stButton button {
        background: rgba(255,255,255,0.06) !important;
        color: var(--text) !important;
        border: 1px solid var(--line) !important;
        box-shadow: none !important;
    }

    /* ---------- Inputs (kept solid white with dark text for guaranteed readability
         across Streamlit versions — broad selectors so nothing slips through) ---------- */
    input[type="text"], input[type="number"], input[type="password"],
    textarea,
    .stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input,
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea,
    div[data-baseweb="base-input"] input {
        color: #14120f !important;
        background-color: #ffffff !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
        caret-color: #14120f !important;
    }
    input::placeholder, textarea::placeholder { color: #8a8378 !important; opacity: 1 !important; }
    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
        border-color: var(--gold) !important; box-shadow: 0 0 0 1px var(--gold) !important;
    }

    /* Selectbox / dropdown — closed control */
    .stSelectbox div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div {
        color: #14120f !important;
        background-color: #ffffff !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
    }
    .stSelectbox div[data-baseweb="select"] * { color: #14120f !important; fill: #14120f !important; }

    /* Selectbox open dropdown list (rendered in a portal, needs its own rule) */
    div[data-baseweb="popover"] ul[role="listbox"],
    div[data-baseweb="menu"] {
        background-color: #ffffff !important;
    }
    div[data-baseweb="popover"] ul[role="listbox"] li,
    div[data-baseweb="menu"] li,
    div[data-baseweb="popover"] li * {
        color: #14120f !important;
        background-color: #ffffff !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color: rgba(205,168,106,0.18) !important;
    }

    label p { color: var(--text-dim) !important; font-size:0.83rem !important; font-weight:600 !important; }

    /* ---------- KPI metric cards ---------- */
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.045), rgba(255,255,255,0.015));
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 16px 18px;
    }
    div[data-testid="stMetricValue"] { color: var(--gold-light) !important; font-family:'Playfair Display', serif; }
    div[data-testid="stMetricLabel"] { color: var(--text-dim) !important; }

    /* ---------- Tabs ---------- */
    button[data-baseweb="tab"] { font-weight:600 !important; color: var(--text-dim) !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: var(--gold-light) !important; }
    div[data-baseweb="tab-highlight"] { background-color: var(--gold) !important; }
    div[data-baseweb="tab-border"] { background-color: var(--line) !important; }

    /* ---------- Status badges ---------- */
    .badge {
        display: inline-block;
        padding: 3px 13px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.72rem;
        letter-spacing: .4px;
        text-transform: uppercase;
        vertical-align: middle;
    }
    .badge-new { background: rgba(205,168,106,0.18); color: var(--gold-light) !important; border:1px solid var(--gold); }
    .badge-preparing { background: rgba(212,159,58,0.16); color: #e0b158 !important; border:1px solid #d49f3a; }
    .badge-delivery { background: rgba(74,144,196,0.16); color: #7fb8e8 !important; border:1px solid #4a90c4; }
    .badge-completed { background: rgba(60,140,100,0.16); color: #6fcf9c !important; border:1px solid #3c8c64; }

    @keyframes glow {
        0% { box-shadow: 0 0 0 0 rgba(205,168,106,0.35); }
        50% { box-shadow: 0 0 0 8px rgba(205,168,106,0); }
        100% { box-shadow: 0 0 0 0 rgba(205,168,106,0); }
    }
    .blink-box {
        padding: 18px;
        border-radius: 14px;
        animation: glow 1.8s infinite;
        border: 1px solid var(--gold);
        background: linear-gradient(180deg, rgba(205,168,106,0.06), rgba(255,255,255,0.02));
    }

    /* ---------- Login card ---------- */
    .login-wrap { max-width: 420px; margin: 30px auto 0 auto; }
    .login-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.015));
        border: 1px solid var(--line); border-radius: 18px; padding: 34px 30px 8px 30px;
        text-align:center; box-shadow: 0 20px 50px rgba(0,0,0,0.4);
    }
    .login-card .mark {
        width:56px; height:56px; border-radius:50%; margin: 0 auto 14px auto;
        display:flex; align-items:center; justify-content:center; font-size:26px;
        background: linear-gradient(135deg, var(--gold-light), var(--gold-deep)); color:#1a1408;
    }

    hr { border-color: var(--line) !important; }
    .stCaption, [data-testid="stCaptionContainer"] { color: var(--text-dim) !important; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# DECORATIVE FLOATING FOOD ICONS (left / right gutters)
# ============================================================
st.markdown("""
    <div class="food-float left">
        <span style="left:10px; top:8%; animation-delay:0s;">🍲</span>
        <span style="left:35px; top:24%; animation-delay:1.2s; font-size:1.5rem;">🥗</span>
        <span style="left:5px; top:42%; animation-delay:2.4s;">🍜</span>
        <span style="left:38px; top:60%; animation-delay:0.6s; font-size:1.6rem;">🥘</span>
        <span style="left:8px; top:78%; animation-delay:1.8s;">🍰</span>
        <span style="left:32px; top:92%; animation-delay:3s; font-size:1.4rem;">🍹</span>
    </div>
    <div class="food-float right">
        <span style="right:12px; top:12%; animation-delay:0.9s;">🍛</span>
        <span style="right:38px; top:30%; animation-delay:2.1s; font-size:1.5rem;">🧁</span>
        <span style="right:8px; top:48%; animation-delay:0.3s;">🥙</span>
        <span style="right:35px; top:66%; animation-delay:1.5s; font-size:1.6rem;">🍹</span>
        <span style="right:10px; top:84%; animation-delay:2.7s;">🍩</span>
        <span style="right:30px; top:6%; animation-delay:3.3s; font-size:1.3rem;">☕</span>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
if "local_orders" not in st.session_state:
    st.session_state.local_orders = []
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ============================================================
# HELPERS
# ============================================================
def fmt(amount):
    try:
        return f"Rs. {float(amount):,.0f}"
    except Exception:
        return f"Rs. {amount}"

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

def format_order_items(items_raw):
    try:
        items_dict = ast.literal_eval(items_raw) if isinstance(items_raw, str) else items_raw
        formatted = []
        for _id, d in items_dict.items():
            name = d.get('name', 'Item')
            qty = d.get('quantity', 1)
            price = d.get('price', 0)
            formatted.append(f"{qty}x {name} (Rs. {price * qty})")
        return ", ".join(formatted)
    except Exception:
        return str(items_raw)

def send_automated_sms(phone, message):
    try:
        clean_phone = phone.strip().replace("+", "").replace(" ", "")
        if clean_phone.startswith("0"):
            clean_phone = "92" + clean_phone[1:]
        encoded_msg = urllib.parse.quote(message)
        webbrowser.open(f"https://wa.me/{clean_phone}?text={encoded_msg}")
    except Exception as e:
        print(f"WhatsApp automation error: {e}")

# Menu categories — shown as tabs on the storefront and as a dropdown in the admin panel
CATEGORIES = ["Breakfast", "Lunch", "Dinner", "Desserts", "Cold Drinks"]
CATEGORY_ICONS = {"Breakfast": "🍳", "Lunch": "🍛", "Dinner": "🍽️", "Desserts": "🍰", "Cold Drinks": "🥤"}

DEMO_MENU = [
    {"id": 1, "item_name": "Special Chicken Biryani", "price": 350, "cost_price": 220,
     "description": "Ghar ke masalon se bani lazeez biryani", "is_available": True, "category": "Lunch",
     "image_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500"},
    {"id": 2, "item_name": "Aloo Keema & Roti", "price": 280, "cost_price": 160,
     "description": "Fresh minced meat with soft homemade chapatis", "is_available": True, "category": "Dinner",
     "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=500"},
    {"id": 3, "item_name": "Daal Chawal Desi Ghee", "price": 200, "cost_price": 110,
     "description": "Ultimate comfort food cooked with pure desi ghee", "is_available": True, "category": "Lunch",
     "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"},
]

@st.cache_data(ttl=30)
def get_menu_items(only_available=True):
    if supabase:
        try:
            q = supabase.table("menu_items").select("*")
            if only_available:
                q = q.eq("is_available", True)
            res = q.execute()
            if res.data:
                return res.data
        except Exception:
            pass
    return [m for m in DEMO_MENU if (m["is_available"] or not only_available)]

def get_orders():
    orders = list(st.session_state.local_orders)
    if supabase:
        try:
            res = supabase.table("orders").select("*").order("id", desc=True).execute()
            if res.data:
                orders = res.data + orders
        except Exception:
            pass
    if not orders:
        orders = [{
            "id": 101, "customer_name": "Ahmed Ali", "phone": "03001234567",
            "address": "House 24, Block A",
            "items": "{'1': {'name': 'Special Chicken Biryani', 'price': 350, 'quantity': 2}}",
            "total_amount": 700, "status": "New",
            "order_time": datetime.now().isoformat()
        }]
    return orders

def compute_analytics(orders, menu_lookup_cost):
    rows = []
    for o in orders:
        try:
            items_dict = ast.literal_eval(o["items"]) if isinstance(o.get("items"), str) else (o.get("items") or {})
        except Exception:
            items_dict = {}
        cost = 0
        for item_id, d in items_dict.items():
            try:
                key = int(item_id)
            except Exception:
                key = item_id
            unit_cost = menu_lookup_cost.get(key, 0)
            cost += unit_cost * d.get("quantity", 1)

        raw_time = o.get("order_time") or o.get("created_at")
        try:
            ts = pd.to_datetime(raw_time)
        except Exception:
            ts = pd.NaT

        rows.append({
            "id": o.get("id"),
            "revenue": float(o.get("total_amount", 0) or 0),
            "cost": cost,
            "profit": float(o.get("total_amount", 0) or 0) - cost,
            "date": ts,
            "customer": o.get("customer_name", "Unknown"),
        })
    return pd.DataFrame(rows)

# ============================================================
# TOP NAVIGATION BAR
# ============================================================
nav_left, nav_right = st.columns([2, 2])
with nav_left:
    st.markdown("""
        <div class="vip-brand" style="padding-top:6px;">
            <div class="mark">🥂</div>
            <div>
                <div class="name">Homemade Kitchen</div>
                <div class="tag">Fine Home Dining</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
with nav_right:
    st.write("")
    portal_mode = st.radio(
        "Navigate", ["🍽️ Customer Storefront", "🔐 Admin Management Panel"],
        horizontal=True, label_visibility="collapsed"
    )
st.markdown(f"<div style='text-align:right; margin-top:-8px;'><span class='stCaption'>📅 {datetime.now().strftime('%A, %d %b %Y')}</span></div>", unsafe_allow_html=True)
st.markdown("<hr style='margin:14px 0 22px 0;'>", unsafe_allow_html=True)

# ============================================================
# 1. CUSTOMER STOREFRONT
# ============================================================
if portal_mode == "🍽️ Customer Storefront":
    st.markdown("""
        <div class="hero-banner">
            <span class="hero-eyebrow">✦ Est. in your home kitchen ✦</span>
            <h1>Homemade Kitchen</h1>
            <div class="hero-divider"></div>
            <p>Fresh, hygienic, and authentic home-cooked meals — plated with care, delivered with pride.</p>
            <p>⏰ Open daily · 9:00 AM – 10:00 PM</p>
        </div>
    """, unsafe_allow_html=True)

    menu_items = get_menu_items(only_available=True)

    search_col, _ = st.columns([2, 3])
    with search_col:
        search_term = st.text_input("🔍 Search dish", placeholder="e.g. Biryani")

    if search_term:
        menu_items = [m for m in menu_items if search_term.lower() in m["item_name"].lower()]

    col_grid, col_checkout = st.columns([2, 1])

    with col_grid:
        st.markdown('<div class="section-label">📋 Today\'s Fresh Menu</div>', unsafe_allow_html=True)

        def render_dish_card(item):
            st.markdown('<div class="menu-card">', unsafe_allow_html=True)
            cols = st.columns([1, 2])
            with cols[0]:
                st.image(item.get("image_url") or "https://via.placeholder.com/150", use_container_width=True)
            with cols[1]:
                st.markdown(f'<div class="dish-name">{item["item_name"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dish-desc">{item.get("description", "Freshly prepared meal")}</div>', unsafe_allow_html=True)
                st.markdown(f'<span class="price-badge">Rs. {item["price"]}</span>', unsafe_allow_html=True)
                st.write("")
                qty = st.number_input("Quantity", 0, 10, 0, key=f"item_qty_{item['id']}", label_visibility="collapsed")
                if qty > 0:
                    st.session_state.cart[item["id"]] = {
                        "name": item["item_name"], "price": item["price"], "quantity": qty
                    }
                elif item["id"] in st.session_state.cart:
                    del st.session_state.cart[item["id"]]
            st.markdown('</div>', unsafe_allow_html=True)

        # Category filter — a single set of cards/widgets is rendered per run
        # (never duplicated across categories), so there's no risk of duplicate
        # widget keys or the cart quantity getting out of sync.
        cat_options = ["✨ All"] + [f"{CATEGORY_ICONS.get(c, '🍴')} {c}" for c in CATEGORIES]
        cat_choice = st.radio(
            "Category filter", cat_options, horizontal=True, label_visibility="collapsed", key="menu_category_filter"
        )

        if cat_choice == "✨ All":
            filtered_menu = menu_items
        else:
            chosen_cat = cat_choice.split(" ", 1)[1]
            filtered_menu = [m for m in menu_items if m.get("category", "Lunch") == chosen_cat]

        if not filtered_menu:
            st.info("No dishes match your search." if search_term else f"No dishes listed under this category yet.")
        for item in filtered_menu:
            render_dish_card(item)

    with col_checkout:
        st.markdown('<div class="section-label">🛒 Order Summary</div>', unsafe_allow_html=True)
        if not st.session_state.cart:
            st.info("Your cart is empty. Select items from the menu.")
        else:
            st.markdown('<div class="menu-card">', unsafe_allow_html=True)
            total_bill = 0
            for item_id, details in st.session_state.cart.items():
                subtotal = details["price"] * details["quantity"]
                total_bill += subtotal
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px dashed var(--line);'>"
                    f"<span>{details['name']} <span style='color:var(--text-dim);'>× {details['quantity']}</span></span>"
                    f"<span style='color:var(--gold-light);font-weight:600;'>{fmt(subtotal)}</span></div>",
                    unsafe_allow_html=True
                )
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;padding-top:14px;font-family:\"Playfair Display\",serif;font-size:1.3rem;font-weight:700;'>"
                f"<span>Total</span><span style='color:var(--gold-light);'>{fmt(total_bill)}</span></div>",
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-label">📍 Delivery Details</div>', unsafe_allow_html=True)

            with st.form("quick_checkout_form"):
                c_name = st.text_input("Your Name *")
                c_phone = st.text_input("Phone Number * (e.g. 03001234567)")
                c_address = st.text_area("Delivery Address *")
                place_order_btn = st.form_submit_button("🚀 Confirm & Place Order")

                if place_order_btn:
                    if not c_name or not c_phone or not c_address:
                        st.error("Please fill all delivery details!")
                    else:
                        order_id_mock = len(st.session_state.local_orders) + 200
                        order_time = datetime.now().isoformat()
                        new_order = {
                            "id": order_id_mock, "customer_name": c_name, "phone": c_phone,
                            "address": c_address, "items": str(st.session_state.cart),
                            "total_amount": total_bill, "status": "New", "order_time": order_time
                        }
                        st.session_state.local_orders.insert(0, new_order)

                        if supabase:
                            payload = {
                                "customer_name": c_name, "phone": c_phone, "address": c_address,
                                "items": str(st.session_state.cart), "total_amount": total_bill,
                                "status": "New", "order_time": order_time
                            }
                            try:
                                supabase.table("orders").insert(payload).execute()
                            except Exception:
                                payload.pop("order_time", None)
                                try:
                                    supabase.table("orders").insert(payload).execute()
                                except Exception:
                                    pass

                        st.success("🎉 Order placed successfully! Kitchen notified.")
                        st.session_state.cart = {}
                        safe_rerun()

# ============================================================
# 2. ADMIN MANAGEMENT PANEL
# ============================================================
elif portal_mode == "🔐 Admin Management Panel":
    if not st.session_state.admin_logged_in:
        st.markdown("""
            <div class="login-wrap">
                <div class="login-card">
                    <div class="mark">🔐</div>
                    <h2 style="margin-bottom:2px;">Admin Access</h2>
                    <p style="color:var(--text-dim);font-size:0.88rem;margin-top:0;">Sign in to manage your kitchen</p>
        """, unsafe_allow_html=True)
        with st.form("admin_login_form"):
            username = st.text_input("Admin Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login", use_container_width=True)
            if login_btn:
                if username == "admin" and password == "123":
                    st.session_state.admin_logged_in = True
                    st.success("Login successful!")
                    safe_rerun()
                else:
                    st.error("Invalid Username or Password!")
        st.markdown("""
                    <p style="font-size:0.75rem;color:var(--text-dim);">⚠️ Change the default admin username/password before going live.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        top_l, top_r = st.columns([4, 1])
        with top_l:
            st.markdown('<div class="section-label" style="margin-bottom:2px;">✅ Welcome back, Admin</div>', unsafe_allow_html=True)
        with top_r:
            if st.button("Logout"):
                st.session_state.admin_logged_in = False
                safe_rerun()

        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["🍽️ Manage Menu", "🔔 Live Orders", "📊 Sales & Profit Dashboard"])

        # ---------------- TAB 1: MANAGE MENU ----------------
        with tab1:
            st.markdown('<div class="section-label">Add a New Dish</div>', unsafe_allow_html=True)
            with st.form("add_food_form"):
                c1, c2 = st.columns(2)
                with c1:
                    new_name = st.text_input("Food Item Name *")
                    new_price = st.number_input("Selling Price (Rs.) *", min_value=0, step=10)
                    new_category = st.selectbox("Category * (decides which tab it shows under)", CATEGORIES)
                with c2:
                    new_cost = st.number_input("Cost Price (Rs.) — what it costs you to make *", min_value=0, step=10)
                    new_img = st.text_input("Image URL")
                new_desc = st.text_area("Description (Ingredients / Details)")

                if new_price > 0 and new_cost >= 0:
                    margin = new_price - new_cost
                    margin_pct = (margin / new_price * 100) if new_price else 0
                    st.caption(f"💰 Estimated margin per plate: {fmt(margin)} ({margin_pct:.0f}%)")

                submit_food = st.form_submit_button("💾 Save & Publish to Menu")
                if submit_food:
                    if not new_name or new_price <= 0:
                        st.error("Please provide a valid item name and price!")
                    else:
                        payload = {
                            "item_name": new_name, "price": new_price, "cost_price": new_cost,
                            "description": new_desc, "image_url": new_img, "is_available": True,
                            "category": new_category
                        }
                        if supabase:
                            try:
                                supabase.table("menu_items").insert(payload).execute()
                                st.success(f"✅ '{new_name}' added under {new_category} and is now live!")
                                get_menu_items.clear()
                            except Exception as e:
                                # Older tables may not have a "category" column yet — retry without it
                                try:
                                    payload.pop("category", None)
                                    supabase.table("menu_items").insert(payload).execute()
                                    st.success(f"✅ '{new_name}' added and is now live! (Run the updated schema to enable categories.)")
                                    get_menu_items.clear()
                                except Exception as e2:
                                    st.error(f"Failed to add menu item: {e2}")
                        else:
                            st.success(f"✅ '{new_name}' added under {new_category} in Demo mode!")

            st.markdown("---")
            st.markdown('<div class="section-label">Current Menu</div>', unsafe_allow_html=True)
            all_items = get_menu_items(only_available=False)
            for item in all_items:
                st.markdown('<div class="menu-card" style="padding:12px 18px;margin-bottom:10px;">', unsafe_allow_html=True)
                cols = st.columns([3, 1.2, 1.2, 1, 1])
                cat_icon = CATEGORY_ICONS.get(item.get("category", "Lunch"), "🍴")
                cols[0].write(f"**{item['item_name']}**  \n{cat_icon} {item.get('category', 'Lunch')}")
                cols[1].write(f"Price: {fmt(item.get('price', 0))}")
                cols[2].write(f"Cost: {fmt(item.get('cost_price', 0))}")
                is_avail = item.get("is_available", True)
                if cols[3].button("🚫 Hide" if is_avail else "✅ Show", key=f"toggle_{item['id']}"):
                    if supabase:
                        try:
                            supabase.table("menu_items").update({"is_available": not is_avail}).eq("id", item["id"]).execute()
                            get_menu_items.clear()
                        except Exception as e:
                            st.error(str(e))
                    safe_rerun()
                if cols[4].button("🗑️ Delete", key=f"del_{item['id']}"):
                    if supabase:
                        try:
                            supabase.table("menu_items").delete().eq("id", item["id"]).execute()
                            get_menu_items.clear()
                        except Exception as e:
                            st.error(str(e))
                    safe_rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ---------------- TAB 2: LIVE ORDERS ----------------
        with tab2:
            st.markdown('<div class="section-label">Live Kitchen Orders</div>', unsafe_allow_html=True)
            search_q = st.text_input("🔍 Search by customer name or phone")
            orders = get_orders()

            if search_q:
                orders = [o for o in orders if search_q.lower() in str(o.get("customer_name", "")).lower()
                          or search_q in str(o.get("phone", ""))]

            status_tabs = st.tabs(["🚨 New", "👨‍🍳 Preparing", "🚴 Out for Delivery", "✅ Completed", "📋 All"])
            status_map = {0: "New", 1: "Preparing", 2: "Out for Delivery", 3: "Completed"}

            def render_order(order):
                status = order.get("status", "New")
                order_id = order.get("id", 0)
                c_name = order.get("customer_name", "Unknown")
                phone = str(order.get("phone", ""))
                address = order.get("address", "-")
                total = order.get("total_amount", 0)
                clean_items_str = format_order_items(order.get("items", "-"))

                badge_class = {"New": "badge-new", "Preparing": "badge-preparing",
                                "Out for Delivery": "badge-delivery", "Completed": "badge-completed"}.get(status, "badge-new")

                box_class = "blink-box" if status == "New" else "menu-card"
                st.markdown(f"""
                    <div class="{box_class}">
                        <h4>Order #{order_id} — {c_name} <span class="badge {badge_class}">{status}</span></h4>
                        <p><b>Phone:</b> {phone} &nbsp;|&nbsp; <b>Address:</b> {address}</p>
                        <p><b>Items:</b> {clean_items_str}</p>
                        <p><b>Total:</b> {fmt(total)}</p>
                    </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Accept & Prep 👨‍🍳", key=f"adm_prep_{order_id}"):
                        order["status"] = "Preparing"
                        msg = (f"Salam {c_name}! Aapka Order #{order_id} accept ho gaya hai aur tayyar ho raha hai.\n\n"
                               f"Items: {clean_items_str}\nTotal Amount: {fmt(total)}\n\n"
                               f"🕒 Timings: Subha 9:00 AM se Raat 10:00 PM tak\nShukriya Homemade Kitchen se order karne ke liye!")
                        send_automated_sms(phone, msg)
                        st.success(f"Order #{order_id} accepted, WhatsApp message sent!")
                        safe_rerun()
                with col2:
                    if st.button("Out for Delivery 🚴", key=f"adm_del_{order_id}"):
                        order["status"] = "Out for Delivery"
                        msg = f"Salam {c_name}! Aapka Order #{order_id} out for delivery hai. Jald pohnch jayega. Shukriya!"
                        send_automated_sms(phone, msg)
                        safe_rerun()
                with col3:
                    if st.button("Complete ✅", key=f"adm_comp_{order_id}"):
                        order["status"] = "Completed"
                        msg = f"Salam {c_name}! Aapka Order #{order_id} deliver ho chuka hai. Enjoy your meal! 🍽️"
                        send_automated_sms(phone, msg)
                        safe_rerun()
                st.divider()

            for idx, tab in enumerate(status_tabs[:4]):
                with tab:
                    filtered = [o for o in orders if o.get("status", "New") == status_map[idx]]
                    if not filtered:
                        st.info("No orders in this category.")
                    for o in filtered:
                        render_order(o)

            with status_tabs[4]:
                if not orders:
                    st.info("No orders yet.")
                for o in orders:
                    render_order(o)

        # ---------------- TAB 3: SALES & PROFIT DASHBOARD ----------------
        with tab3:
            st.markdown('<div class="section-label">📊 Sales & Profit Dashboard</div>', unsafe_allow_html=True)

            all_menu = get_menu_items(only_available=False)
            cost_lookup = {m["id"]: m.get("cost_price", 0) for m in all_menu}
            orders = get_orders()
            df = compute_analytics(orders, cost_lookup)

            range_choice = st.selectbox("View period", ["Today", "This Week", "This Month", "All Time", "Custom Range"])

            today = date.today()
            if range_choice == "Today":
                mask = df["date"].dt.date == today
            elif range_choice == "This Week":
                start = today - timedelta(days=today.weekday())
                mask = df["date"].dt.date >= start
            elif range_choice == "This Month":
                mask = (df["date"].dt.month == today.month) & (df["date"].dt.year == today.year)
            elif range_choice == "Custom Range":
                c1, c2 = st.columns(2)
                start_d = c1.date_input("From", today - timedelta(days=7))
                end_d = c2.date_input("To", today)
                mask = (df["date"].dt.date >= start_d) & (df["date"].dt.date <= end_d)
            else:
                mask = pd.Series([True] * len(df))

            df_filtered = df[mask.fillna(False)] if len(df) else df

            total_orders = len(df_filtered)
            total_revenue = df_filtered["revenue"].sum() if total_orders else 0
            total_cost = df_filtered["cost"].sum() if total_orders else 0
            total_profit = total_revenue - total_cost
            margin_pct = (total_profit / total_revenue * 100) if total_revenue else 0
            avg_order = (total_revenue / total_orders) if total_orders else 0

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("🧾 Orders", total_orders)
            k2.metric("💵 Revenue", fmt(total_revenue))
            k3.metric("🍳 Cost (ingredients etc.)", fmt(total_cost))
            k4.metric("📈 Profit", fmt(total_profit), f"{margin_pct:.0f}% margin")
            k5.metric("🧮 Avg. Order Value", fmt(avg_order))

            st.markdown("---")

            if total_orders:
                c1, c2 = st.columns(2)
                with c1:
                    st.write("**Revenue over time**")
                    daily = df_filtered.dropna(subset=["date"]).copy()
                    if not daily.empty:
                        daily["day"] = daily["date"].dt.date
                        daily_grouped = daily.groupby("day")[["revenue", "cost", "profit"]].sum()
                        st.line_chart(daily_grouped)
                    else:
                        st.info("No dated orders to chart yet — add 'order_time' to your Supabase orders table.")
                with c2:
                    st.write("**Revenue vs Cost vs Profit**")
                    st.bar_chart(pd.DataFrame({
                        "Amount": [total_revenue, total_cost, total_profit]
                    }, index=["Revenue", "Cost", "Profit"]))
            else:
                st.info("No orders found for this period yet.")

            st.markdown("---")
            st.caption(
                "ℹ️ For full accuracy, add an **order_time** (timestamp) column to your `orders` table and a "
                "**cost_price** (numeric) column to your `menu_items` table in Supabase. The app already writes "
                "to these columns automatically if they exist."
            )

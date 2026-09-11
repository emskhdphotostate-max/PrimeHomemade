import streamlit as st
import urllib.parse
import webbrowser
import ast
from datetime import datetime, date, timedelta
import pandas as pd
import psycopg2
import psycopg2.extras

# ============================================================
# NEON DATABASE CONFIGURATION
# ============================================================
NEON_CONN_STRING = st.secrets.get("NEON_CONN_STRING", "postgresql://user:password@host/dbname?sslmode=require")

def get_db_connection():
    try:
        return psycopg2.connect(NEON_CONN_STRING)
    except Exception as e:
        return None

st.set_page_config(page_title="Homemade Kitchen | Order & Eat", layout="wide", page_icon="🍔", initial_sidebar_state="collapsed")

# ============================================================
# CSS — DARK / YELLOW FOOD-DELIVERY APP THEME (FIXED)
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --yellow: #FFC839;
        --yellow-light: #FFDB77;
        --yellow-deep: #F5A623;
        --navy: #0B0E1B;
        --panel: #141A2E;
        --panel-2: #1B2238;
        --line: rgba(255,200,57,0.16);
        --text: #F4F6FB;
        --text-dim: #8B93A7;
        --blue: #4DA3FF;
        --green: #3ECF8E;
        --ink: #1A1408;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, h5, h6 { font-family: 'Poppins', sans-serif !important; letter-spacing: 0.2px; }

    header[data-testid="stHeader"] {
        background: var(--navy) !important;
        box-shadow: none !important;
        border-bottom: 1px solid var(--line);
    }
    header[data-testid="stHeader"] * { color: var(--text) !important; fill: var(--text) !important; }
    div[data-testid="stToolbar"] { color: var(--text) !important; }
    div[data-testid="stDecoration"] { background: linear-gradient(90deg, var(--yellow-deep), var(--yellow-light), var(--yellow-deep)) !important; }
    #MainMenu { color: var(--text) !important; }

    .block-container { padding-top: 5.5rem !important; max-width: 1200px; position: relative; z-index: 1; }

    .stApp {
        background:
            radial-gradient(1000px 520px at 10% -8%, rgba(255,200,57,0.10), transparent 55%),
            radial-gradient(900px 480px at 100% 0%, rgba(77,163,255,0.08), transparent 50%),
            linear-gradient(180deg, #080a13 0%, #0b0e1b 55%, #090b15 100%);
        color: var(--text) !important;
    }
    h1, h2, h3, h4, h5, h6, p, span, label, div { color: var(--text); }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0e1120, #141a2e) !important;
        border-right: 1px solid var(--line);
    }

    .vip-brand { display:flex; align-items:center; gap:12px; }
    .vip-brand .mark {
        width: 44px; height: 44px; border-radius: 14px;
        display:flex; align-items:center; justify-content:center;
        background: linear-gradient(135deg, var(--yellow-light), var(--yellow-deep));
        color: var(--ink) !important; font-size: 21px; font-weight:800;
        box-shadow: 0 0 0 1px rgba(255,200,57,0.4), 0 6px 18px rgba(255,200,57,0.25);
    }
    .vip-brand .name { font-family:'Poppins', sans-serif; font-size: 1.35rem; font-weight:800; color: var(--yellow-light) !important; line-height:1.1; }
    .vip-brand .tag { font-size: 0.68rem; letter-spacing: 2.5px; text-transform: uppercase; color: var(--text-dim) !important; }

    .hero-banner {
        position: relative; overflow:hidden;
        background:
            linear-gradient(100deg, rgba(6,8,16,0.94) 0%, rgba(6,8,16,0.78) 42%, rgba(6,8,16,0.25) 68%, rgba(6,8,16,0.05) 100%),
            url('https://images.unsplash.com/photo-1544025162-d76694265947?w=1400&q=80') center/cover no-repeat;
        border: 1px solid var(--line);
        padding: 64px 42px;
        min-height: 340px;
        border-radius: 24px;
        text-align: left;
        margin-bottom: 30px;
        display: flex; flex-direction: column; justify-content: center;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }
    .hero-eyebrow {
        display:inline-block; font-size:0.72rem; letter-spacing:4px; text-transform:uppercase;
        color: var(--yellow) !important; margin-bottom:12px; font-weight:800;
    }
    .hero-banner h1 {
        font-size: 3rem; line-height: 1.08; font-weight: 900; margin: 0 0 14px 0; max-width: 620px;
        color: #ffffff !important; -webkit-text-fill-color: #ffffff;
    }
    .hero-banner p { font-weight: 500; color: #d7dae4 !important; font-size:1rem; margin: 4px 0; max-width: 560px; }

    .section-label {
        font-family:'Poppins', sans-serif; font-size:1.35rem; font-weight:700;
        color: var(--text) !important; margin: 6px 0 16px 0;
        display:flex; align-items:center; gap:10px;
    }
    .section-label::after { content:""; flex:1; height:1px; background: var(--line); }

    .menu-card {
        background: linear-gradient(180deg, var(--panel-2), var(--panel));
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 18px;
        margin-bottom: 18px;
    }
    .dish-name { font-family:'Poppins', sans-serif; font-size:1.12rem; font-weight:700; margin: 2px 0 4px 0; color: var(--text) !important; }
    .dish-desc { color: var(--text-dim) !important; font-size:0.87rem; line-height:1.5; min-height: 2.6em; }

    .price-badge {
        display: inline-block;
        background: rgba(255,200,57,0.12);
        color: var(--yellow) !important;
        font-weight: 800;
        padding: 5px 16px;
        border-radius: 999px;
        font-size: 0.98rem;
    }

    /* Standardized button styling so buttons are visible and styled properly */
    .stButton button, div.stFormSubmitButton > button {
        background: linear-gradient(135deg, var(--yellow-light), var(--yellow-deep)) !important;
        color: var(--ink) !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 0.6rem 1.3rem !important;
        box-shadow: 0 8px 18px rgba(255,200,57,0.3) !important;
    }
    .stButton button p, div.stFormSubmitButton > button p { color: var(--ink) !important; font-weight:800 !important; }

    /* Fix input fields to not affect pills / container widgets */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        color: #14120f !important;
        background-color: #ffffff !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
    }
    
    .badge {
        display: inline-block; padding: 3px 13px; border-radius: 999px;
        font-weight: 700; font-size: 0.72rem; text-transform: uppercase;
    }
    .badge-new { background: rgba(255,200,57,0.18); color: var(--yellow-light) !important; border:1px solid var(--yellow); }
    .badge-preparing { background: rgba(245,166,35,0.16); color: #ffb85c !important; border:1px solid #f5a623; }
    .badge-delivery { background: rgba(77,163,255,0.16); color: #8fc2ff !important; border:1px solid var(--blue); }
    .badge-completed { background: rgba(62,207,142,0.16); color: #7fe6b6 !important; border:1px solid var(--green); }

    .blink-box {
        padding: 18px; border-radius: 18px; border: 1px solid var(--yellow);
        background: linear-gradient(180deg, rgba(255,200,57,0.08), var(--panel));
    }

    .login-wrap { max-width: 420px; margin: 30px auto 0 auto; }
    .login-card {
        background: linear-gradient(180deg, var(--panel-2), var(--panel));
        border: 1px solid var(--line); border-radius: 22px; padding: 34px 30px 8px 30px;
        text-align:center; box-shadow: 0 20px 50px rgba(0,0,0,0.45);
    }
    .login-card .mark {
        width:56px; height:56px; border-radius:16px; margin: 0 auto 14px auto;
        display:flex; align-items:center; justify-content:center; font-size:26px;
        background: linear-gradient(135deg, var(--yellow-light), var(--yellow-deep)); color: var(--ink);
    }
    </style>
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
if "order_success_msg" not in st.session_state:
    st.session_state.order_success_msg = ""

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

CATEGORIES = ["Breakfast", "Lunch", "Dinner", "Desserts", "Cold Drinks"]
CATEGORY_ICONS = {"Breakfast": "🍳", "Lunch": "🍛", "Dinner": "🍽️", "Desserts": "🍰", "Cold Drinks": "🥤"}

DEMO_MENU = [
    {"id": 1, "item_name": "Special Chicken Biryani", "price": 350, "cost_price": 220, "description": "Ghar ke masalon se bani lazeez biryani", "is_available": True, "category": "Lunch", "image_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500"},
    {"id": 2, "item_name": "Aloo Keema & Roti", "price": 280, "cost_price": 160, "description": "Fresh minced meat with soft homemade chapatis", "is_available": True, "category": "Dinner", "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=500"},
    {"id": 3, "item_name": "Daal Chawal Desi Ghee", "price": 200, "cost_price": 110, "description": "Ultimate comfort food cooked with pure desi ghee", "is_available": True, "category": "Lunch", "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"},
]

def get_menu_items(only_available=True):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            query = "SELECT * FROM menu_items"
            if only_available:
                query += " WHERE is_available = TRUE"
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            if data:
                return data
        except Exception:
            if conn:
                conn.close()
    return [m for m in DEMO_MENU if (m["is_available"] or not only_available)]

def get_orders():
    orders = list(st.session_state.local_orders)
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM orders ORDER BY id DESC")
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            if data:
                orders = data + orders
        except Exception:
            if conn:
                conn.close()
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
            <div class="mark">🍔</div>
            <div>
                <div class="name">Homemade Kitchen</div>
                <div class="tag">Hungry? Order &amp; Eat.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
with nav_right:
    st.write("")
    portal_mode = st.pills(
        "Navigate", ["🍽️ Customer Storefront", "🔐 Admin Management Panel"],
        default="🍽️ Customer Storefront", required=True, label_visibility="collapsed", key="portal_nav"
    )
st.markdown(f"<div style='text-align:right; margin-top:-8px;'><span class='stCaption'>📅 {datetime.now().strftime('%A, %d %b %Y')}</span></div>", unsafe_allow_html=True)
st.markdown("<hr style='margin:14px 0 22px 0;'>", unsafe_allow_html=True)

# ============================================================
# 1. CUSTOMER STOREFRONT
# ============================================================
if portal_mode == "🍽️ Customer Storefront":
    st.markdown("""
        <div class="hero-banner">
            <span class="hero-eyebrow">🔥 Chef's Special · Fresh Daily</span>
            <h1>Enjoy Our<br>Delicious Meal</h1>
            <p>Fresh, hygienic, and authentic home-cooked meals — plated with care, delivered with pride.</p>
            <p>⏰ Open daily · 9:00 AM – 10:00 PM</p>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.order_success_msg:
        st.success(st.session_state.order_success_msg)
        st.session_state.order_success_msg = ""

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
                price_col, qty_col = st.columns([1, 1])
                with price_col:
                    st.markdown(f'<span class="price-badge">Rs. {item["price"]}</span>', unsafe_allow_html=True)
                with qty_col:
                    qty = st.number_input("Quantity", 0, 10, 0, key=f"item_qty_{item['id']}", label_visibility="collapsed")
                if qty > 0:
                    st.session_state.cart[item["id"]] = {
                        "name": item["item_name"], "price": item["price"], "quantity": qty
                    }
                elif item["id"] in st.session_state.cart:
                    del st.session_state.cart[item["id"]]
            st.markdown('</div>', unsafe_allow_html=True)

        cat_options = ["✨ All"] + [f"{CATEGORY_ICONS.get(c, '🍴')} {c}" for c in CATEGORIES]
        cat_choice = st.pills(
            "Category filter", cat_options, default="✨ All", required=True,
            label_visibility="collapsed", key="menu_category_filter"
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
                    f"<span style='color:var(--yellow-light);font-weight:700;'>{fmt(subtotal)}</span></div>",
                    unsafe_allow_html=True
                )
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;padding-top:14px;font-family:\"Poppins\",sans-serif;font-size:1.3rem;font-weight:800;'>"
                f"<span>Total</span><span style='color:var(--yellow-light);'>{fmt(total_bill)}</span></div>",
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

                        conn = get_db_connection()
                        if conn:
                            try:
                                cursor = conn.cursor()
                                cursor.execute(
                                    "INSERT INTO orders (customer_name, phone, address, items, total_amount, status) VALUES (%s, %s, %s, %s, %s, %s)",
                                    (c_name, c_phone, c_address, str(st.session_state.cart), total_bill, "New")
                                )
                                conn.commit()
                                cursor.close()
                                conn.close()
                            except Exception as e:
                                if conn:
                                    conn.close()

                        st.session_state.order_success_msg = "🎉 Order placed successfully! Kitchen notified."
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
                    <h2 style="margin-bottom:2px;color:var(--yellow-light) !important;">Admin Access</h2>
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
                    new_category = st.selectbox("Category *", CATEGORIES)
                with c2:
                    new_cost = st.number_input("Cost Price (Rs.) *", min_value=0, step=10)
                    new_img = st.text_input("Image URL")
                new_desc = st.text_area("Description")

                submit_food = st.form_submit_button("💾 Save & Publish to Menu")
                if submit_food:
                    if not new_name or new_price <= 0:
                        st.error("Please provide a valid item name and price!")
                    else:
                        conn = get_db_connection()
                        if conn:
                            try:
                                cursor = conn.cursor()
                                cursor.execute(
                                    "INSERT INTO menu_items (item_name, price, cost_price, description, is_available, category, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                    (new_name, new_price, new_cost, new_desc, True, new_category, new_img)
                                )
                                conn.commit()
                                cursor.close()
                                conn.close()
                                st.success(f"✅ '{new_name}' added under {new_category} and is now live!")
                            except Exception as e:
                                if conn:
                                    conn.close()
                                st.error(f"Failed to add menu item: {e}")
                        else:
                            st.success(f"✅ '{new_name}' added in Demo mode!")

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
                    conn = get_db_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE menu_items SET is_available = %s WHERE id = %s", (not is_avail, item["id"]))
                            conn.commit()
                            cursor.close()
                            conn.close()
                        except Exception:
                            if conn:
                                conn.close()
                    safe_rerun()
                if cols[4].button("🗑️ Delete", key=f"del_{item['id']}"):
                    conn = get_db_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM menu_items WHERE id = %s", (item["id"],))
                            conn.commit()
                            cursor.close()
                            conn.close()
                        except Exception:
                            if conn:
                                conn.close()
                    safe_rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ---------------- TAB 2: LIVE ORDERS ----------------
        with tab2:
            st.markdown('<div class="section-label">Live Kitchen Orders</div>', unsafe_allow_html=True)
            search_q = st.text_input("🔍 Search by customer name or phone")
            orders = get_orders()

            if search_q:
                orders = [o for o in orders if search_q.lower() in str(o.get("customer_name", "")).lower() or search_q in str(o.get("phone", ""))]

            status_tabs = st.tabs(["🚨 New", "👨‍🍳 Preparing", "🚴 Out for Delivery", "✅ Completed", "📋 All"])
            status_map = {0: "New", 1: "Preparing", 2: "Out for Delivery", 3: "Completed"}

            def render_order(order, tab_name="general"):
                status = order.get("status", "New")
                order_id = order.get("id", 0)
                c_name = order.get("customer_name", "Unknown")
                phone = str(order.get("phone", ""))
                address = order.get("address", "-")
                total = order.get("total_amount", 0)
                clean_items_str = format_order_items(order.get("items", "-"))

                badge_class = {"New": "badge-new", "Preparing": "badge-preparing", "Out for Delivery": "badge-delivery", "Completed": "badge-completed"}.get(status, "badge-new")
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
                    # Guaranteed unique key per tab and per order instance
                    if st.button("Accept & Prep 👨‍🍳", key=f"prep_{tab_name}_{order_id}_{id(order)}"):
                        order["status"] = "Preparing"
                        msg = f"Salam {c_name}! Aapka Order #{order_id} accept ho gaya hai aur tayyar ho raha hai."
                        send_automated_sms(phone, msg)
                        safe_rerun()
                with col2:
                    if st.button("Out for Delivery 🚴", key=f"deliv_{tab_name}_{order_id}_{id(order)}"):
                        order["status"] = "Out for Delivery"
                        msg = f"Salam {c_name}! Aapka Order #{order_id} out for delivery hai."
                        send_automated_sms(phone, msg)
                        safe_rerun()
                with col3:
                    if st.button("Complete ✅", key=f"comp_{tab_name}_{order_id}_{id(order)}"):
                        order["status"] = "Completed"
                        msg = f"Salam {c_name}! Aapka Order #{order_id} deliver ho chuka hai. Enjoy!"
                        send_automated_sms(phone, msg)
                        safe_rerun()
                st.divider()

            for idx, tab in enumerate(status_tabs[:4]):
                with tab:
                    filtered = [o for o in orders if o.get("status", "New") == status_map[idx]]
                    if not filtered:
                        st.info("No orders in this category.")
                    for o in filtered:
                        render_order(o, tab_name=f"status_tab_{status_map[idx]}")

            with status_tabs[4]:
                if not orders:
                    st.info("No orders yet.")
                for o in orders:
                    render_order(o, tab_name="all_tab")

        # ---------------- TAB 3: SALES & PROFIT DASHBOARD ----------------
        with tab3:
            st.markdown('<div class="section-label">📊 Sales & Profit Dashboard</div>', unsafe_allow_html=True)

            all_menu = get_menu_items(only_available=False)
            cost_lookup = {m["id"]: m.get("cost_price", 0) for m in all_menu}
            orders = get_orders()
            df = compute_analytics(orders, cost_lookup)

            range_choice = st.selectbox("View period", ["Today", "This Week", "This Month", "All Time"])
            today = date.today()

            if range_choice == "Today":
                mask = df["date"].dt.date == today
            elif range_choice == "This Week":
                start = today - timedelta(days=today.weekday())
                mask = df["date"].dt.date >= start
            elif range_choice == "This Month":
                mask = (df["date"].dt.month == today.month) & (df["date"].dt.year == today.year)
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
            k3.metric("🍳 Cost", fmt(total_cost))
            k4.metric("📈 Profit", fmt(total_profit), f"{margin_pct:.0f}% margin")
            k5.metric("🧮 Avg. Order", fmt(avg_order))

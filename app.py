import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from fpdf import FPDF

st.set_page_config(page_title="Enterprise POS", page_icon="💳", layout="wide", initial_sidebar_state="expanded")

# -----------------------------
# 1. TRANSLATION ENGINE
# -----------------------------
TRANSLATIONS = {
    "English": {
        "dashboard": "📊 Dashboard", "inventory": "📦 Inventory", "pos": "🛒 Point of Sale", 
        "staff": "👥 Staff", "analytics": "📈 Analytics", "logout": "🚪 Logout",
        "search": "🔍 Search Products...", "cart": "🧾 Cart", "empty_cart": "Cart is Empty",
        "subtotal": "Subtotal", "discount": "Discount", "tax": "Tax", "total": "Total",
        "checkout": "💳 Checkout & Generate PDF", "customer": "Customer Name", "add": "Add", "stock": "Stock"
    },
    "Hindi": {
        "dashboard": "📊 डैशबोर्ड", "inventory": "📦 इन्वेंटरी", "pos": "🛒 बिक्री केंद्र (POS)", 
        "staff": "👥 स्टाफ", "analytics": "📈 एनालिटिक्स", "logout": "🚪 लॉग आउट",
        "search": "🔍 उत्पाद खोजें...", "cart": "🧾 कार्ट", "empty_cart": "कार्ट खाली है",
        "subtotal": "उप-योग", "discount": "छूट", "tax": "कर", "total": "कुल",
        "checkout": "💳 चेकआउट और बिल (PDF)", "customer": "ग्राहक का नाम", "add": "जोड़ें", "stock": "स्टॉक"
    },
    "Telugu": {
        "dashboard": "📊 డాష్‌బోర్డ్", "inventory": "📦 ఇన్వెంటరీ", "pos": "🛒 విక్రయ కేంద్రం (POS)", 
        "staff": "👥 సిబ్బంది", "analytics": "📈 విశ్లేషణలు", "logout": "🚪 లాగ్ అవుట్",
        "search": "🔍 ఉత్పత్తులను శోధించండి...", "cart": "🧾 బండి", "empty_cart": "బండి ఖాళీగా ఉంది",
        "subtotal": "ఉపమొత్తం", "discount": "డిస్కౌంట్", "tax": "పన్ను", "total": "మొత్తం",
        "checkout": "💳 చెక్అవుట్ & బిల్లు (PDF)", "customer": "కస్టమర్ పేరు", "add": "జోడించు", "stock": "స్టాక్"
    },
    "Kannada": {
        "dashboard": "📊 ಡ್ಯಾಶ್‌ಬೋರ್ಡ್", "inventory": "📦 ದಾಸ್ತಾನು", "pos": "🛒 ಮಾರಾಟ ಕೇಂದ್ರ (POS)", 
        "staff": "👥 ಸಿಬ್ಬಂದಿ", "analytics": "📈 ವಿಶ್ಲೇಷಣೆ", "logout": "🚪 ಲಾಗ್‌ಔಟ್",
        "search": "🔍 ಉತ್ಪನ್ನಗಳನ್ನು ಹುಡುಕಿ...", "cart": "🧾 ಕಾರ್ಟ್", "empty_cart": "ಕಾರ್ಟ್ ಖಾಲಿಯಾಗಿದೆ",
        "subtotal": "ಉಪಮೊತ್ತ", "discount": "ರಿಯಾಯಿತಿ", "tax": "ತೆರಿಗೆ", "total": "ಒಟ್ಟು",
        "checkout": "💳 ಚೆಕ್ಔಟ್ ಮತ್ತು ಬಿಲ್ (PDF)", "customer": "ಗ್ರಾಹಕರ ಹೆಸರು", "add": "ಸೇರಿಸಿ", "stock": "ಸ್ಟಾಕ್"
    }
}

# -----------------------------
# 2. STYLING & DATABASE INIT
# -----------------------------
def apply_theme():
    st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="metric-container"] {
        background: #ffffff; border: 1px solid #e2e8f0; padding: 20px;
        border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #4F46E5;
    }
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background: white; border-radius: 10px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

def init_db():
    defaults = {
        "users": {
            "shanmukh": {"password": "owner123", "role": "Owner"},
            "manager": {"password": "manager123", "role": "Manager"},
            "staff": {"password": "staff123", "role": "Staff"}
        },
        "logged_in": False, "current_user": None, "lang": "English",
        "low_stock_threshold": 5,
        "inventory": pd.DataFrame(columns=["id", "sku", "name", "price", "quantity", "image"]),
        "cart": [], "sales": [], "staff_list": []
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

apply_theme()
init_db()
t = TRANSLATIONS[st.session_state.lang] # Active Dictionary Shortcut

# -----------------------------
# 3. PDF GENERATOR HELPER
# -----------------------------
def generate_pdf_receipt(sale_id, date_str, customer, cart, subtotal, discount, tax, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "SHANMUKH ENTERPRISES", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(190, 5, "========================================", ln=True, align='C')
    pdf.cell(190, 5, f"Bill ID: {sale_id}  |  Date: {date_str}  |  Customer: {customer}", ln=True)
    pdf.cell(190, 5, "----------------------------------------------------------------", ln=True)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 5, "Item", 0, 0); pdf.cell(30, 5, "Qty", 0, 0, 'C'); pdf.cell(70, 5, "Price", 0, 1, 'R')
    pdf.set_font("Arial", '', 10)
    pdf.cell(190, 5, "----------------------------------------------------------------", ln=True)
    
    for item in cart:
        pdf.cell(90, 5, item['name'][:25], 0, 0)
        pdf.cell(30, 5, str(item['quantity']), 0, 0, 'C')
        pdf.cell(70, 5, f"Rs. {item['subtotal']:,.2f}", 0, 1, 'R')
        
    pdf.cell(190, 5, "----------------------------------------------------------------", ln=True)
    pdf.cell(120, 5, "", 0, 0); pdf.cell(35, 5, "Subtotal:", 0, 0); pdf.cell(35, 5, f"Rs. {subtotal:,.2f}", 0, 1, 'R')
    if discount > 0:
        pdf.cell(120, 5, "", 0, 0); pdf.cell(35, 5, "Discount:", 0, 0); pdf.cell(35, 5, f"-Rs. {discount:,.2f}", 0, 1, 'R')
    pdf.cell(120, 5, "", 0, 0); pdf.cell(35, 5, "Tax (5%):", 0, 0); pdf.cell(35, 5, f"+Rs. {tax:,.2f}", 0, 1, 'R')
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(120, 8, "", 0, 0); pdf.cell(35, 8, "TOTAL:", 0, 0); pdf.cell(35, 8, f"Rs. {total:,.2f}", 0, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# -----------------------------
# 4. PAGE MODULES
# -----------------------------
def dashboard():
    st.title(t["dashboard"])
    df_inv = st.session_state.inventory
    total_items = df_inv["quantity"].sum() if not df_inv.empty else 0
    total_rev = sum(s["total"] for s in st.session_state.sales)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Products", len(df_inv))
    c2.metric("Units in Stock", total_items)
    c3.metric("Gross Revenue", f"₹{total_rev:,.2f}")
    
    st.divider()
    st.subheader("⚡ Low Stock Alerts")
    if not df_inv.empty:
        low_stock = df_inv[df_inv["quantity"] <= st.session_state.low_stock_threshold]
        if not low_stock.empty:
            st.warning(f"{len(low_stock)} items are running critically low!")
            st.dataframe(low_stock[["name", "sku", "quantity"]], use_container_width=True, hide_index=True)

def inventory():
    st.title(t["inventory"])
    with st.expander("➕ Register New Product"):
        with st.form("new_product", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Product Name*")
            sku = col2.text_input("SKU / Barcode*")
            price = col1.number_input("Price (₹)", min_value=0.0)
            qty = col2.number_input("Initial Quantity", min_value=0)
            uploaded_image = st.file_uploader("Upload Product Photo (Optional)", type=["png", "jpg", "jpeg"])
            
            if st.form_submit_button("Save to Database", type="primary"):
                if name and sku:
                    img_bytes = uploaded_image.read() if uploaded_image else None
                    new_row = {"id": str(uuid.uuid4())[:8], "sku": sku, "name": name, "price": price, "quantity": qty, "image": img_bytes}
                    st.session_state.inventory = pd.concat([st.session_state.inventory, pd.DataFrame([new_row])], ignore_index=True)
                    st.rerun()

    st.subheader("📋 Database (Double-Click to Edit)")
    if not st.session_state.inventory.empty:
        st.session_state.inventory = st.data_editor(
            st.session_state.inventory, use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config={"id": st.column_config.TextColumn("System ID", disabled=True), "image": None}
        )

def pos():
    st.title(t["pos"])
    df_inv = st.session_state.inventory
    if df_inv.empty: st.warning("Inventory empty. Add products first."); return

    col_pos, col_cart = st.columns([2, 1.2])

    with col_pos:
        search = st.text_input(t["search"])
        display_df = df_inv if not search else df_inv[df_inv['name'].str.contains(search, case=False) | df_inv['sku'].str.contains(search, case=False)]

        cols = st.columns(3)
        for idx, row in display_df.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    if row.get('image') is not None: st.image(row['image'], use_container_width=True)
                    st.markdown(f"**{row['name']}**")
                    color = "red" if row['quantity'] <= st.session_state.low_stock_threshold else "gray"
                    st.markdown(f"<span style='color:{color}'>{t['stock']}: {row['quantity']}</span>", unsafe_allow_html=True)
                    st.markdown(f"#### ₹{row['price']:,.2f}")
                    
                    qty = st.number_input("Qty", 1, max(int(row['quantity']), 1), key=f"q_{row['id']}", label_visibility="collapsed")
                    if st.button(t["add"], key=f"btn_{row['id']}", type="primary", use_container_width=True):
                        if row['quantity'] >= qty:
                            item = next((i for i in st.session_state.cart if i["id"] == row["id"]), None)
                            if item:
                                item["quantity"] += qty
                                item["subtotal"] = item["price"] * item["quantity"]
                            else:
                                st.session_state.cart.append({"id": row["id"], "name": row["name"], "price": row["price"], "quantity": qty, "subtotal": row["price"] * qty})
                            st.rerun()

    with col_cart:
        with st.container(border=True):
            st.subheader(t["cart"])
            if not st.session_state.cart: st.info(t["empty_cart"])
            else:
                subtotal = sum(i["subtotal"] for i in st.session_state.cart)
                for idx, item in enumerate(st.session_state.cart):
                    c1, c2, c3 = st.columns([3, 1.5, 1])
                    c1.write(f"{item['quantity']}x {item['name']}")
                    c2.write(f"₹{item['subtotal']:,.2f}")
                    if c3.button("✖", key=f"rm_{idx}"): st.session_state.cart.pop(idx); st.rerun()
                
                st.divider()
                discount_pct = st.slider(f"{t['discount']} (%)", 0, 100, 0)
                discount_amt = subtotal * (discount_pct / 100)
                tax_amt = (subtotal - discount_amt) * 0.05
                grand_total = (subtotal - discount_amt) + tax_amt
                
                st.caption(f"{t['subtotal']}: ₹{subtotal:,.2f} | {t['tax']}: +₹{tax_amt:,.2f} | {t['discount']}: -₹{discount_amt:,.2f}")
                st.markdown(f"### {t['total']}: ₹{grand_total:,.2f}")
                
                customer = st.text_input(t["customer"], "Walk-in")
                if st.button(t["checkout"], type="primary", use_container_width=True):
                    sale_id = str(uuid.uuid4())[:8].upper()
                    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    for c_item in st.session_state.cart:
                        idx = df_inv.index[df_inv['id'] == c_item['id']].tolist()[0]
                        st.session_state.inventory.at[idx, 'quantity'] -= c_item['quantity']

                    st.session_state.sales.append({"id": sale_id, "customer": customer, "total": grand_total, "date": date_str})
                    pdf_bytes = generate_pdf_receipt(sale_id, date_str, customer, st.session_state.cart, subtotal, discount_amt, tax_amt, grand_total)

                    st.session_state['last_pdf'] = pdf_bytes
                    st.session_state['last_sale_id'] = sale_id
                    st.session_state.cart.clear()
                    st.rerun()

        if 'last_pdf' in st.session_state:
            st.download_button("📄 Download PDF", data=st.session_state['last_pdf'], file_name=f"bill_{st.session_state['last_sale_id']}.pdf", mime="application/pdf", type="primary", use_container_width=True)

def staff():
    st.title(t["staff"])
    with st.form("new_staff", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full Name")
        role = c2.selectbox("Role", ["Cashier", "Storekeeper", "Manager"])
        if st.form_submit_button("Add Staff", type="primary") and name:
            st.session_state.staff_list.append({"id": str(uuid.uuid4())[:8], "name": name, "role": role})
            st.rerun()
    if st.session_state.staff_list: 
        st.dataframe(pd.DataFrame(st.session_state.staff_list), use_container_width=True, hide_index=True)

def analytics():
    st.title(t["analytics"])
    if not st.session_state.sales: st.info("No sales yet."); return
    df_sales = pd.DataFrame(st.session_state.sales)
    df_sales['date'] = pd.to_datetime(df_sales['date']).dt.date
    st.bar_chart(df_sales.groupby('date')['total'].sum(), color="#4F46E5")
    st.download_button("📥 Export CSV", data=df_sales.to_csv(index=False).encode('utf-8'), file_name='sales.csv', type="primary")

# -----------------------------
# 5. APP ROUTING & LOGIN
# -----------------------------
if not st.session_state.logged_in:
    st.markdown("<br><br><br><h1 style='text-align: center;'>💳 MSME POS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.container(border=True):
            user = st.text_input("Username").strip().lower()
            pwd = st.text_input("Password", type="password")
            if st.button("Login", type="primary", use_container_width=True):
                if user in st.session_state.users and st.session_state.users[user]["password"] == pwd:
                    st.session_state.logged_in = True
                    st.session_state.current_user = {"username": user, "role": st.session_state.users[user]["role"]}
                    st.rerun()
                else: 
                    st.error("Invalid credentials.")
else:
    with st.sidebar:
        # Language Selector
        new_lang = st.selectbox("🌐 Language / भाषा / భాష / ಭಾಷೆ", ["English", "Hindi", "Telugu", "Kannada"], index=["English", "Hindi", "Telugu", "Kannada"].index(st.session_state.lang))
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.rerun()
            
        st.divider()
        role = st.session_state.current_user["role"]
        st.subheader(f"👤 {st.session_state.current_user['username'].title()}")
        st.caption(f"Role: **{role}**")
        st.divider()
        
        # Build menu based on language
        menu = {t["pos"]: pos, t["inventory"]: inventory}
        if role in ["Manager", "Owner"]:
            menu = {t["dashboard"]: dashboard} | menu | {t["staff"]: staff}
        if role == "Owner":
            menu[t["analytics"]] = analytics

        choice = st.radio("Navigation", list(menu.keys()), label_visibility="collapsed")
        st.divider()
        if st.button(t["logout"], use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    menu[choice]()

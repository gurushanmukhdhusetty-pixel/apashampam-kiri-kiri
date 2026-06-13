import streamlit as st
from utils.init_db import initialize_database

st.set_page_config(page_title="Enterprise POS", page_icon="💳", layout="wide")
initialize_database()

# Define the pages based on your folder structure
dashboard_page = st.Page("pages/dashboard.py", title="Dashboard", icon="📊")
pos_page = st.Page("pages/pos.py", title="Point of Sale", icon="🛒")
inventory_page = st.Page("pages/inventory.py", title="Inventory", icon="📦")
staff_page = st.Page("pages/staff.py", title="Staff", icon="👥")
analytics_page = st.Page("pages/analytics.py", title="Analytics", icon="📈")

def login_screen():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<h1 style='text-align: center;'>💳 MSME POS</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            st.caption("Default Owner: **shanmukh** | **owner123**")
            user = st.text_input("Username").strip().lower()
            pwd = st.text_input("Password", type="password")
            
            if st.button("Login", type="primary", use_container_width=True):
                account = st.session_state.users.get(user)
                if account and account["password"] == pwd:
                    st.session_state.logged_in = True
                    st.session_state.current_user = {"username": user, "role": account["role"]}
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

if not st.session_state.logged_in:
    login_screen()
else:
    # Role-based Access Control
    role = st.session_state.current_user["role"]
    
    # Staff gets basic access
    pages = [pos_page, inventory_page]
    
    # Managers get staff + dashboard
    if role in ["Manager", "Owner"]:
        pages.insert(0, dashboard_page)
        pages.append(staff_page)
        
    # Owners get everything
    if role == "Owner":
        pages.append(analytics_page)

    # Sidebar Profile & Logout
    with st.sidebar:
        st.subheader(f"👤 {st.session_state.current_user['username'].title()}")
        st.caption(f"Role: **{role}**")
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()

    # Run the dynamic navigation
    pg = st.navigation(pages)
    pg.run()

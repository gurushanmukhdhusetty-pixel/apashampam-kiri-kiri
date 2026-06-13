import streamlit as st
import pandas as pd

def initialize_database():
    defaults = {
        "users": {
            "shanmukh": {"password": "owner123", "role": "Owner"},
            "manager": {"password": "manager123", "role": "Manager"},
            "staff": {"password": "staff123", "role": "Staff"}
        },
        "logged_in": False,
        "current_user": None,
        "inventory": pd.DataFrame(columns=["id", "sku", "name", "price", "quantity"]),
        "cart": [],
        "sales": [],
        "staff_list": []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

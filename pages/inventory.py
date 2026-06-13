import streamlit as st
import pandas as pd
import uuid

st.title("📦 Inventory Management")

with st.expander("➕ Add New Product", expanded=False):
    with st.form("new_product", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        name = c1.text_input("Name*")
        sku = c2.text_input("SKU*")
        price = c3.number_input("Price (₹)", min_value=0.0)
        qty = c4.number_input("Qty", min_value=0)
        
        if st.form_submit_button("Save to DB", type="primary"):
            if name and sku:
                new_row = {"id": str(uuid.uuid4())[:8], "sku": sku, "name": name, "price": price, "quantity": qty}
                st.session_state.inventory = pd.concat([st.session_state.inventory, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Product added!")
                st.rerun()
            else:
                st.error("Name and SKU required.")

st.subheader("📋 Live Database")
st.caption("Double-click any cell to edit. Changes save automatically.")

if not st.session_state.inventory.empty:
    edited_df = st.data_editor(
        st.session_state.inventory,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "id": st.column_config.TextColumn("System ID", disabled=True),
            "sku": "Barcode/SKU",
            "name": "Product Name",
            "price": st.column_config.NumberColumn("Price (₹)", format="₹%.2f"),
            "quantity": st.column_config.NumberColumn("Stock Qty", min_value=0)
        }
    )
    st.session_state.inventory = edited_df
else:
    st.info("No products found.")

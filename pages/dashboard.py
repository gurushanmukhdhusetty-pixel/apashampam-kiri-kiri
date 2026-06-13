import streamlit as st

st.title("📊 Dashboard")

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
    low_stock = df_inv[df_inv["quantity"] <= 5]
    if not low_stock.empty:
        st.warning(f"{len(low_stock)} items are running critically low!")
        st.dataframe(low_stock[["name", "sku", "quantity"]], use_container_width=True, hide_index=True)
    else:
        st.success("All stock levels are healthy.")
else:
    st.info("Inventory is empty.")

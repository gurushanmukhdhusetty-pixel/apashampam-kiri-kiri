import streamlit as st
import uuid
from datetime import datetime

st.title("🛒 Terminal & Checkout")

df_inv = st.session_state.inventory
if df_inv.empty:
    st.warning("Inventory is empty. Add products in the Inventory tab first.")
    st.stop()

col_pos, col_cart = st.columns([2, 1.2])

# LEFT: POS Grid
with col_pos:
    search = st.text_input("🔍 Search Products", placeholder="Type name or SKU...")
    display_df = df_inv if not search else df_inv[df_inv['name'].str.contains(search, case=False) | df_inv['sku'].str.contains(search, case=False)]

    cols = st.columns(3)
    for idx, row in display_df.iterrows():
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"**{row['name']}**")
                st.caption(f"Stock: {row['quantity']}")
                st.markdown(f"#### ₹{row['price']:,.2f}")
                
                qty = st.number_input("Qty", min_value=1, max_value=max(int(row['quantity']), 1), key=f"q_{row['id']}", label_visibility="collapsed")
                
                if st.button("Add", key=f"btn_{row['id']}", type="primary", use_container_width=True):
                    if row['quantity'] >= qty:
                        item = next((i for i in st.session_state.cart if i["id"] == row["id"]), None)
                        if item:
                            item["quantity"] += qty
                            item["subtotal"] = item["price"] * item["quantity"]
                        else:
                            st.session_state.cart.append({
                                "id": row["id"], "name": row["name"], 
                                "price": row["price"], "quantity": qty, 
                                "subtotal": row["price"] * qty
                            })
                        st.rerun()
                    else:
                        st.error("Not enough stock!")

# RIGHT: Cart & Billing
with col_cart:
    with st.container(border=True):
        st.subheader("🧾 Current Cart")
        
        if not st.session_state.cart:
            st.info("Cart is empty.")
        else:
            subtotal = sum(i["subtotal"] for i in st.session_state.cart)
            
            for idx, item in enumerate(st.session_state.cart):
                c1, c2, c3 = st.columns([3, 1.5, 1])
                c1.write(f"{item['quantity']}x {item['name']}")
                c2.write(f"₹{item['subtotal']:,.2f}")
                if c3.button("✖", key=f"rm_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
            
            st.divider()
            discount_pct = st.slider("Discount (%)", 0, 100, 0)
            discount_amt = subtotal * (discount_pct / 100)
            tax_rate = 0.05
            tax_amt = (subtotal - discount_amt) * tax_rate
            grand_total = (subtotal - discount_amt) + tax_amt
            
            st.caption(f"Subtotal: ₹{subtotal:,.2f}")
            st.caption(f"Tax (5%): +₹{tax_amt:,.2f}")
            if discount_amt > 0: st.caption(f"Discount: -₹{discount_amt:,.2f}")
            st.markdown(f"### Total: ₹{grand_total:,.2f}")
            
            customer = st.text_input("Customer Name", placeholder="Walk-in")
            
            if st.button("💳 Checkout & Generate Bill", type="primary", use_container_width=True):
                sale_id = str(uuid.uuid4())[:8].upper()
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Deduct Stock
                for c_item in st.session_state.cart:
                    idx = df_inv.index[df_inv['id'] == c_item['id']].tolist()[0]
                    st.session_state.inventory.at[idx, 'quantity'] -= c_item['quantity']

                st.session_state.sales.append({
                    "id": sale_id, "customer": customer or "Walk-in", 
                    "total": grand_total, "date": date_str
                })
                
                # Generate Receipt Format
                receipt = f"================================\n"
                receipt += f"      SHANMUKH ENTERPRISES\n"
                receipt += f"================================\n"
                receipt += f"Bill ID: {sale_id}\n"
                receipt += f"Date: {date_str}\n"
                receipt += f"Customer: {customer or 'Walk-in'}\n"
                receipt += f"--------------------------------\n"
                receipt += f"{'Item':<15} {'Qty':<5} {'Price'}\n"
                receipt += f"--------------------------------\n"
                for i in st.session_state.cart:
                    receipt += f"{i['name'][:14]:<15} {i['quantity']:<5} ₹{i['subtotal']:,.2f}\n"
                receipt += f"--------------------------------\n"
                receipt += f"Subtotal:              ₹{subtotal:,.2f}\n"
                receipt += f"Discount:             -₹{discount_amt:,.2f}\n"
                receipt += f"Tax (5%):             +₹{tax_amt:,.2f}\n"
                receipt += f"================================\n"
                receipt += f"TOTAL:                 ₹{grand_total:,.2f}\n"
                receipt += f"================================\n"
                receipt += f"       Thank you for shopping!   \n"

                st.session_state.cart.clear()
                st.session_state['last_receipt'] = receipt
                st.success("Payment Successful!")
                st.rerun()

    # Display Print Bill Option if a receipt exists
    if 'last_receipt' in st.session_state:
        st.subheader("🖨️ Latest Bill")
        st.code(st.session_state['last_receipt'], language="text")
        st.download_button(
            label="Download Bill (.txt)",
            data=st.session_state['last_receipt'],
            file_name="receipt.txt",
            mime="text/plain",
            type="primary",
            use_container_width=True
        )

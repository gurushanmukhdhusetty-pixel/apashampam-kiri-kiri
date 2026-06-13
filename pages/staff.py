import streamlit as st
import pandas as pd
import uuid

st.title("👥 Staff Directory")

with st.expander("➕ Register New Employee"):
    c1, c2 = st.columns(2)
    name = c1.text_input("Full Name")
    role = c2.selectbox("Role", ["Cashier", "Storekeeper", "Manager"])
    if st.button("Add Staff", type="primary"):
        if name:
            st.session_state.staff_list.append({"id": str(uuid.uuid4())[:8], "name": name, "role": role})
            st.success("Staff member added.")
            st.rerun()

if st.session_state.staff_list:
    st.dataframe(pd.DataFrame(st.session_state.staff_list), use_container_width=True, hide_index=True)
else:
    st.info("No staff records found.")

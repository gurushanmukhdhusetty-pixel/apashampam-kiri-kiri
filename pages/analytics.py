import streamlit as st
import pandas as pd

st.title("📈 Business Analytics")

sales = st.session_state.sales
if not sales:
    st.info("No sales data available yet. Head to POS to make a sale!")
    st.stop()
    
df_sales = pd.DataFrame(sales)

c1, c2 = st.columns(2)
with c1:
    st.subheader("Revenue Timeline")
    # Clean dates for chart
    df_sales['date'] = pd.to_datetime(df_sales['date']).dt.date
    chart_data = df_sales.groupby('date')['total'].sum().reset_index()
    st.bar_chart(chart_data.set_index('date'), color="#4F46E5")
    
with c2:
    st.subheader("Recent Transactions")
    st.dataframe(df_sales[['date', 'customer', 'total']].tail(10), use_container_width=True, hide_index=True)

st.divider()
csv = df_sales.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Export Full Sales Report (CSV)",
    data=csv,
    file_name='master_sales_report.csv',
    mime='text/csv',
    type="primary"
)

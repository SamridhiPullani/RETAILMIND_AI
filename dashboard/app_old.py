import streamlit as st
import pandas as pd

st.set_page_config(page_title="RetailMind AI", layout="wide")

customers = pd.read_csv("dataset/olist_customers_dataset.csv")
orders = pd.read_csv("dataset/olist_orders_dataset.csv")
payments = pd.read_csv("dataset/olist_order_payments_dataset.csv")

st.title("🛒 RetailMind AI Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Customers", len(customers))
col2.metric("Orders", len(orders))
col3.metric("Revenue", f"${payments['payment_value'].sum():,.2f}")

st.subheader("Order Status Distribution")

order_status = orders["order_status"].value_counts()
st.bar_chart(order_status)

st.subheader("Payment Method Distribution")

payment_types = payments["payment_type"].value_counts()
st.bar_chart(payment_types)

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)

monthly_orders = orders.groupby(
    orders["order_purchase_timestamp"].dt.to_period("M")
).size()

st.subheader("Monthly Orders Trend")
st.line_chart(monthly_orders)
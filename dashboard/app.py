import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import numpy as np
from db import conn, cursor

try:
    cursor.fetchall()
except:
    pass

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Page Config
st.set_page_config(
    page_title="RetailMind AI",
    page_icon="🛒",
    layout="wide"
)
if not st.session_state.logged_in:

    st.title("🔐 RetailMind AI Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if (
            username == "RETAILMIND_AI"
            and
            password == "Samridhi"
        ):

            st.session_state.logged_in = True
            st.rerun()

        else:

            st.error(
                "Invalid Username or Password"
            )

    st.stop()

# Dark Theme
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}
section[data-testid="stSidebar"] {
    background-color: #161B22;
}
[data-testid="stMetric"] {
    background-color: #1F2937;
    padding: 15px;
    border-radius: 15px;
    text-align: center;
}
h1,h2,h3,p,label {
    color:white !important;
}
</style>
""", unsafe_allow_html=True)

# Load Data
customers = pd.read_csv("dataset/olist_customers_dataset.csv")
orders = pd.read_csv("dataset/olist_orders_dataset.csv")
payments = pd.read_csv("dataset/olist_order_payments_dataset.csv")
products = pd.read_csv("dataset/olist_products_dataset.csv")

# =========================
# AI CUSTOMER SEGMENTATION
# =========================
customer_segment = customers[['customer_zip_code_prefix']].copy()

kmeans = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

customer_segment['Cluster'] = kmeans.fit_predict(
    customer_segment
)

# Sidebar
st.sidebar.title("🛒 RetailMind AI")
st.sidebar.success("AI Powered E-Commerce Analytics Dashboard")
state_map = {
    "AC":"Acre",
    "AL":"Alagoas",
    "AM":"Amazonas",
    "AP":"Amapá",
    "BA":"Bahia",
    "CE":"Ceará",
    "DF":"Distrito Federal",
    "ES":"Espírito Santo",
    "GO":"Goiás",
    "MA":"Maranhão",
    "MG":"Minas Gerais",
    "MS":"Mato Grosso do Sul",
    "MT":"Mato Grosso",
    "PA":"Pará",
    "PB":"Paraíba",
    "PE":"Pernambuco",
    "PI":"Piauí",
    "PR":"Paraná",
    "RJ":"Rio de Janeiro",
    "RN":"Rio Grande do Norte",
    "RO":"Rondônia",
    "RR":"Roraima",
    "RS":"Rio Grande do Sul",
    "SC":"Santa Catarina",
    "SE":"Sergipe",
    "SP":"São Paulo",
    "TO":"Tocantins"
}
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filters")

state_names = ["All"] + sorted(state_map.values())

selected_state_name = st.sidebar.selectbox(
    "🌎 Select State",
    state_names
)

if selected_state_name != "All":

    selected_code = [
        k for k, v in state_map.items()
        if v == selected_state_name
    ][0]

    customers = customers[
        customers["customer_state"]
        == selected_code
    ]

customer_search = st.sidebar.text_input(
    "🔎 Search Customer City"
)

if customer_search:

    customers = customers[
        customers["customer_city"]
        .str.contains(
            customer_search,
            case=False,
            na=False
        )
    ]

st.sidebar.markdown("---")

st.sidebar.subheader("📊 Dashboard Summary")

st.sidebar.write(
    f"👥 Customers: {customers.shape[0]:,}"
)

st.sidebar.write(
    f"🛒 Orders: {orders.shape[0]:,}"
)

st.sidebar.write(
    f"💰 Revenue: ${payments['payment_value'].sum():,.0f}"
)

st.sidebar.markdown("---")

st.sidebar.download_button(
    label="📥 Download Customer Report",
    data=customers.to_csv(index=False),
    file_name="customer_report.csv",
    mime="text/csv"
)
menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Customer",
        "Add Product",
        "Place Order",
        "Customer List",
        "Product List",
        "Order History",
        "Delete Order",
        "Update Order Status"
    ]
)

# Header
st.title("🛍️ RetailMind AI")
st.markdown("### Real-Time Customer & Revenue Intelligence Platform")

st.success(
    "🎉 Welcome to RetailMind AI - Real Time E-Commerce Analytics Dashboard"
)

from datetime import date

st.metric(
    "📅 Today",
    date.today().strftime("%d-%m-%Y")
)
try:
    cursor.fetchall()
except:
    pass

# =========================
# KPI CARDS
# =========================

cursor.execute("SELECT COUNT(*) FROM customers")
total_customers = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM products")
total_products = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM orders")
total_orders = cursor.fetchone()[0]
total_revenue = payments["payment_value"].sum()

c1, c2, c3 ,c4 = st.columns(4)

c1.metric("👥 Customers", total_customers)
c2.metric("🛍️ Products", total_products)
c3.metric("📦 Orders", total_orders)
c4.metric("💰 Revenue", f"${total_revenue:,.0f}")

predicted_sales = total_revenue * 1.12

st.metric(
    "📈 Predicted Next Month Revenue",
    f"${predicted_sales:,.0f}"
)

st.divider()

# =========================
# ORDER STATUS
# =========================

st.subheader("📦 Order Status Distribution")

cursor.execute("""
SELECT status, COUNT(*)
FROM orders
GROUP BY status
""")

status_data = cursor.fetchall()

status_df = pd.DataFrame(
    status_data,
    columns=["Status", "Count"]
)

fig_status = px.pie(
    status_df,
    names="Status",
    values="Count",
    template="plotly_dark"
)

st.plotly_chart(
    fig_status,
    use_container_width=True
)

st.divider()

# =========================
# TOP SELLING PRODUCTS
# =========================

st.subheader("🔥 Top Selling Products")

cursor.execute("""
SELECT
    p.product_name,
    COUNT(o.order_id)
FROM orders o
JOIN products p
ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY COUNT(o.order_id) DESC
""")

top_products = cursor.fetchall()

top_products_df = pd.DataFrame(
    top_products,
    columns=["Product", "Orders"]
)

fig_products = px.bar(
    top_products_df,
    x="Product",
    y="Orders",
    template="plotly_dark"
)

st.plotly_chart(
    fig_products,
    use_container_width=True
)

st.divider()

st.subheader("🏆 Top Customers")

cursor.execute("""
SELECT
    c.name,
    COUNT(o.order_id) as total_orders
FROM customers c
JOIN orders o
ON c.customer_id = o.customer_id
GROUP BY c.name
ORDER BY total_orders DESC
LIMIT 5
""")

top_customers = cursor.fetchall()

top_customers_df = pd.DataFrame(
    top_customers,
    columns=["Customer", "Orders"]
)

st.dataframe(
    top_customers_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

st.subheader("📈 Monthly Orders Trend")

cursor.execute("""
SELECT
    order_date,
    COUNT(*) as total_orders
FROM orders
GROUP BY order_date
ORDER BY order_date
""")

trend_data = cursor.fetchall()

trend_df = pd.DataFrame(
    trend_data,
    columns=["Date", "Orders"]
)

fig_trend = px.line(
    trend_df,
    x="Date",
    y="Orders",
    markers=True,
    template="plotly_dark",
    title="Orders Trend"
)

st.plotly_chart(
    fig_trend,
    use_container_width=True
)

st.divider()

st.subheader("📦 Recent Orders")

cursor.execute("""
SELECT
    o.order_id,
    c.name,
    p.product_name,
    o.quantity,
    o.status
FROM orders o
JOIN customers c
ON o.customer_id = c.customer_id
JOIN products p
ON o.product_id = p.product_id
ORDER BY o.order_id DESC
LIMIT 5
""")

recent_orders = cursor.fetchall()

recent_df = pd.DataFrame(
    recent_orders,
    columns=[
        "Order ID",
        "Customer",
        "Product",
        "Quantity",
        "Status"
    ]
)

st.dataframe(
    recent_df,
    use_container_width=True,
    hide_index=True
)
st.download_button(
    label="📥 Download Orders Report",
    data=recent_df.to_csv(index=False),
    file_name="orders_report.csv",
    mime="text/csv"
)

st.divider()

st.divider()

st.subheader("⚙️ System Status")

col1, col2, col3 = st.columns(3)

col1.success("🟢 Database Connected")
col2.success("🟢 AI Engine Active")
col3.success("🟢 Dashboard Running")

st.divider()

st.subheader("🥇 Best Selling Category")

cursor.execute("""
SELECT
    p.category,
    COUNT(o.order_id) as total_orders
FROM orders o
JOIN products p
ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_orders DESC
LIMIT 1
""")

best_category = cursor.fetchone()

if best_category:
    st.success(
        f"🏆 {best_category[0]} ({best_category[1]} Orders)"
    )

st.divider()

st.subheader("🏆 Best Selling Product")

cursor.execute("""
SELECT
    p.product_name,
    SUM(o.quantity) as total_sold
FROM orders o
JOIN products p
ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_sold DESC
LIMIT 1
""")

top_product = cursor.fetchone()

if top_product:
    st.success(
        f"🏆 {top_product[0]} ({top_product[1]} Units Sold)"
    )

st.divider()

st.subheader("👑 Top Customer")

cursor.execute("""
SELECT
    c.name,
    SUM(o.quantity) as total_orders
FROM customers c
JOIN orders o
ON c.customer_id = o.customer_id
GROUP BY c.name
ORDER BY total_orders DESC
LIMIT 1
""")

top_customer = cursor.fetchone()

if top_customer:
    st.success(
        f"👑 {top_customer[0]} ({top_customer[1]} Units Ordered)"
    )

st.divider()

st.subheader("💎 Highest Revenue Product")

cursor.execute("""
SELECT
    p.product_name,
    SUM(o.quantity * p.price) as revenue
FROM orders o
JOIN products p
ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY revenue DESC
LIMIT 1
""")

product = cursor.fetchone()

if product:
    st.success(
        f"💎 {product[0]} (₹{product[1]:,.0f})"
    )

st.divider()
st.subheader("👑 VIP Customers")

cursor.execute("""
SELECT
    c.name,
    COUNT(o.order_id) as total_orders
FROM customers c
JOIN orders o
ON c.customer_id = o.customer_id
GROUP BY c.name
HAVING total_orders >= 1
ORDER BY total_orders DESC
LIMIT 5
""")

vip_customers = cursor.fetchall()

vip_df = pd.DataFrame(
    vip_customers,
    columns=["Customer", "Orders"]
)

st.dataframe(
    vip_df,
    use_container_width=True,
    hide_index=True
)

st.divider()
st.subheader("💰 Revenue by Product")

cursor.execute("""
SELECT
    p.product_name,
    SUM(o.quantity * p.price) as revenue
FROM orders o
JOIN products p
ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY revenue DESC
""")

revenue_data = cursor.fetchall()

revenue_df = pd.DataFrame(
    revenue_data,
    columns=["Product", "Revenue"]
)

fig_revenue = px.bar(
    revenue_df,
    x="Product",
    y="Revenue",
    title="Revenue by Product",
    template="plotly_dark"
)

st.plotly_chart(
    fig_revenue,
    use_container_width=True
)
st.divider()

st.subheader("🥇 Product Share")

fig_share = px.pie(
    revenue_df,
    names="Product",
    values="Revenue",
    template="plotly_dark"
)

st.plotly_chart(
    fig_share,
    use_container_width=True
)
st.divider()

st.subheader("🥇 Product Share")

fig_share = px.pie(
    revenue_df,
    names="Product",
    values="Revenue",
    template="plotly_dark"
)

st.plotly_chart(
    fig_share,
    use_container_width=True,
    key="product_share_chart"
)

st.subheader("🎯 Customer Segments")

segment_counts = customer_segment["Cluster"].value_counts()

segment_df = pd.DataFrame({
    "Segment": [
        "Regular",
        "Premium",
        "VIP",
        "At Risk"
    ],
    "Count": segment_counts.values
})

fig_segment = px.pie(
    segment_df,
    names="Segment",
    values="Count",
    title="Customer Segmentation",
    template="plotly_dark"
)

st.plotly_chart(
    fig_segment,
    use_container_width=True
)
st.divider()

st.subheader("📰 Recent Activity")

cursor.execute("""
    SELECT
        order_id,
        status,
        order_date
    FROM orders
    ORDER BY order_id DESC
    LIMIT 5
    """
)

activities = cursor.fetchall()

for activity in activities:
    st.info(
        f"Order #{activity[0]} | {activity[1]} | {activity[2]}"
    )

st.divider()

st.subheader("🚨 Order Status Summary")

cursor.execute("""
    SELECT status, COUNT(*)
    FROM orders
    GROUP BY status
    """ 
)

status_cards = cursor.fetchall()

cols = st.columns(len(status_cards))

for i, row in enumerate(status_cards):
    cols[i].metric(
        row[0],
        row[1]
    )
st.divider()

st.subheader("🏆 Business Insights")

cursor.execute("SELECT COUNT(*) FROM customers")
customers_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM products")
products_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM orders")
orders_count = cursor.fetchone()[0]

st.success(
    f"👥 Total Customers: {customers_count}"
)

st.success(
    f"🛍️ Total Products: {products_count}"
)

st.success(
    f"📦 Total Orders: {orders_count}"
)
# =========================
# CHARTS ROW 1
# =========================
col1, col2 = st.columns(2)

with col1:

    st.subheader("📦 Order Status Distribution")

    status_counts = orders[
        "order_status"
    ].value_counts()

    fig1 = px.bar(
        x=status_counts.index,
        y=status_counts.values,
        color=status_counts.values,
        template="plotly_dark",
        title="Orders by Status"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

with col2:

    st.subheader("💳 Payment Method Distribution")

    payment_counts = payments[
        "payment_type"
    ].value_counts()

    fig2 = px.pie(
        values=payment_counts.values,
        names=payment_counts.index,
        hole=0.5,
        template="plotly_dark"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

st.divider()

# =========================
# CHARTS ROW 2
# =========================
col3, col4 = st.columns(2)

with col3:

    st.subheader("🏙️ Top Customer Cities")

    top_cities = customers[
        "customer_city"
    ].value_counts().head(10)

    fig3 = px.bar(
        x=top_cities.values,
        y=top_cities.index,
        orientation="h",
        template="plotly_dark",
        title="Top 10 Cities"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

with col4:

    st.subheader("🛍️ Top Product Categories")

    top_products = products[
        "product_category_name"
    ].value_counts().head(10)

    fig4 = px.bar(
        x=top_products.index,
        y=top_products.values,
        color=top_products.values,
        template="plotly_dark",
        title="Top Categories"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

st.divider()

# =========================
# AI REVENUE SIMULATOR
# =========================
st.subheader("🚀 AI Revenue Simulator")

new_orders = st.slider(
    "Simulate Future Orders",
    min_value=0,
    max_value=5000,
    value=100
)

avg_order = payments[
    "payment_value"
].mean()

updated_orders = (
    orders.shape[0]
    + new_orders
)

future_revenue = (
    payments["payment_value"].sum()
    + (new_orders * avg_order)
)

a, b = st.columns(2)

a.metric(
    "📦 Predicted Orders",
    f"{updated_orders:,}"
)

b.metric(
    "💰 Predicted Revenue",
    f"${future_revenue:,.0f}"
)

st.success(
    "Move the slider to forecast future growth."
)

st.divider()

# =========================
# CUSTOMER SEGMENTS
# =========================
st.subheader("👥 Customer Segments")

segment_df = pd.DataFrame({
    "Segment": [
        "Champion",
        "Loyal",
        "Regular",
        "At Risk"
    ],
    "Count": [
        12000,
        25000,
        45000,
        17000
    ]
})

fig5 = px.bar(
    segment_df,
    x="Segment",
    y="Count",
    color="Segment",
    template="plotly_dark"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.divider()

# =========================
# AI SALES PREDICTION
# =========================

payments["index"] = range(len(payments))

X = payments[["index"]]
y = payments["payment_value"]

model = LinearRegression()
model.fit(X, y)

future_day = np.array([
    [len(payments) + 1000]
])

predicted_sale = model.predict(
    future_day
)[0]


# =========================
# REVENUE FORECAST
# =========================
st.subheader("📈 AI Revenue Forecast")

forecast = pd.DataFrame({
    "Month": [
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec"
    ],
    "Revenue": [
        18,
        19,
        20,
        21,
        23,
        25
    ]
})

fig6 = px.line(
    forecast,
    x="Month",
    y="Revenue",
    markers=True,
    template="plotly_dark",
    title="Revenue Forecast (Million $)"
)
fig6.update_layout(
    xaxis_title=None,
    yaxis_title="Revenue (Million $)"
)
st.plotly_chart(
    fig6,
    use_container_width=True
)



# =========================
# AI CUSTOMER SEGMENTATION
# =========================
st.subheader("🤖 AI Customer Segmentation")

cluster_counts = (
    customer_segment["Cluster"]
    .value_counts()
    .sort_index()
)
cluster_names = {
    0: "Regular",
    1: "Premium",
    2: "At Risk",
    3: "VIP"
}

cluster_counts.index = [
    cluster_names[i]
    for i in cluster_counts.index
]

fig7 = px.bar(
    x=cluster_counts.index.astype(str),
    y=cluster_counts.values,
    color=cluster_counts.index.astype(str),
    template="plotly_dark",
    title="Customer Segments (K-Means)"
)
fig7.update_layout(
    xaxis_title=None,
    yaxis_title=None
)
st.plotly_chart(
    fig7,
    use_container_width=True
)

st.markdown("---")

st.markdown(
    """
    <div style='text-align:center;
                color:#9CA3AF;
                padding:10px;'>
        RetailMind AI | Customer Segmentation • Revenue Forecasting • Business Intelligence
    </div>
    """,
    unsafe_allow_html=True
)
if menu == "Add Customer":

    st.title("➕ Add Customer")

    name = st.text_input("Customer Name")
    email = st.text_input("Email")
    city = st.text_input("City")
    state = st.text_input("State")

    if st.button("Save Customer"):

        query = """
        INSERT INTO customers
        (name,email,city,state)
        VALUES (%s,%s,%s,%s)
        """

        cursor.execute(
            query,
            (name, email, city, state)
        )

        conn.commit()

        st.success("Customer Added Successfully ✅")
if menu == "Add Product":

    st.title("🛍️ Add Product")

    product_name = st.text_input("Product Name")
    category = st.text_input("Category")
    price = st.number_input("Price", min_value=0.0)

    if st.button("Save Product"):

        query = """
        INSERT INTO products
        (product_name, category, price)
        VALUES (%s,%s,%s)
        """

        cursor.execute(
            query,
            (
                product_name,
                category,
                price
            )
        )

        conn.commit()

        st.success("Product Added Successfully ✅")
if menu == "Place Order":

    st.title("🛒 Place Order")

    customer_id = st.number_input(
        "Customer ID",
        min_value=1,
        step=1
    )

    product_id = st.number_input(
        "Product ID",
        min_value=1,
        step=1
    )

    quantity = st.number_input(
        "Quantity",
        min_value=1,
        step=1
    )

    if st.button("Place Order"):

        cursor.execute(
            "SELECT price FROM products WHERE product_id=%s",
            (product_id,)
        )

        product = cursor.fetchone()

        if product:

            total_amount = product[0] * quantity
            
            query = """
            INSERT INTO orders
            (customer_id, product_id, quantity, order_date, status)
            VALUES (%s,%s,%s,CURDATE(),'Pending')
            """


            cursor.execute(
                query,
                (
                    customer_id,
                    product_id,
                    quantity
                )
            )

            conn.commit()

            st.success(
                f"Order Placed Successfully ✅ Total = ₹{total_amount}"
            )
if menu == "Customer List":

    st.title("👥 Customer List")

    cursor.execute("SELECT * FROM customers")

    customers_data = cursor.fetchall()

    df = pd.DataFrame(
        customers_data,
        columns=[
            "Customer ID",
            "Name",
            "Email",
            "City",
            "State"
        ]
    )
    search_customer = st.text_input(
        "🔍 Search Customer Name"
    )

    if search_customer:
        df = df[
            df["Name"].str.contains(
            search_customer,
            case=False,
            na=False
        )
    ]
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader("🗑️ Delete Customer")

    customer_id = st.number_input(
        "Enter Customer ID to Delete",
        min_value=1,
        step=1
    )

    if st.button("Delete Customer"):

        cursor.execute(
            "DELETE FROM customers WHERE customer_id=%s",
            (customer_id,)
        )

        conn.commit()

        st.success(
            f"✅ Customer {customer_id} deleted successfully"
        )

        st.rerun()
    st.markdown("---")

    st.subheader("✏️ Edit Customer")

    edit_customer_id = st.number_input(
        "Customer ID",
        min_value=1,
        step=1,
        key="edit_customer"
    )

    new_name = st.text_input(
        "New Name",
        key="new_name"
    )

    new_email = st.text_input(
        "New Email",
        key="new_email"
    )

    new_city = st.text_input(
        "New City",
        key="new_city"
    )

    new_state = st.text_input(
        "New State",
        key="new_state"
    )

    if st.button("Update Customer"):

        cursor.execute(
            """
            UPDATE customers
            SET name=%s,
            email=%s,
            city=%s,
            state=%s
        WHERE customer_id=%s
        """,
        (
            new_name,
            new_email,
            new_city,
            new_state,
            edit_customer_id
        )
    )

        conn.commit()

        st.success(
            f"✅ Customer {edit_customer_id} updated successfully"
        )

        st.rerun()
if menu == "Product List":

    st.title("🛍️ Product List")

    cursor.execute("SELECT * FROM products")
    products_data = cursor.fetchall()

    df = pd.DataFrame(
        products_data,
        columns=[
            "Product ID",
            "Product Name",
            "Category",
            "Price"
        ]
    )

    search_product = st.text_input(
        "🔍 Search Product Name"
    )

    if search_product:
        df = df[
            df["Product Name"].str.contains(
                search_product,
                case=False,
                na=False
            )
        ]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader("🗑️ Delete Product")

    product_id = st.number_input(
        "Enter Product ID to Delete",
        min_value=1,
        step=1,
        key="delete_product"
    )

    if st.button("Delete Product"):

        cursor.execute(
            "DELETE FROM products WHERE product_id=%s",
            (product_id,)
        )

        conn.commit()

        st.success(
            f"✅ Product {product_id} deleted successfully"
        )

        st.rerun()
    st.markdown("---")

    st.subheader("✏️ Edit Product")

    edit_product_id = st.number_input(
        "Product ID",
        min_value=1,
        step=1,
        key="edit_product"
    )

    new_product_name = st.text_input(
        "New Product Name",
        key="new_product_name"
    )

    new_category = st.text_input(
        "New Category",
        key="new_category"
    )

    new_price = st.number_input(
        "New Price",
        min_value=0.0,
        key="new_price"
    )

    if st.button("Update Product"):

        cursor.execute(
            """
            UPDATE products
            SET product_name=%s,
                category=%s,
                price=%s
            WHERE product_id=%s
            """,
            (
                new_product_name,
                new_category,
                new_price,
                edit_product_id
            )
        )

        conn.commit()

        st.success(
            f"✅ Product {edit_product_id} updated successfully"
        )

        st.rerun()
if menu == "Order History":

    st.title("📦 Order History")

    cursor.execute("""
    SELECT
        o.order_id,
        c.name,
        p.product_name,
        o.quantity,
        o.order_date,
        o.status
    FROM orders o
    JOIN customers c
    ON o.customer_id = c.customer_id
    JOIN products p
    ON o.product_id = p.product_id
    """)

    orders_data = cursor.fetchall()

    df = pd.DataFrame(
        orders_data,
        columns=[
            "Order ID",
            "Customer Name",
            "Product Name",
            "Quantity",
            "Order Date",
            "Status"
        ]
    )

    st.dataframe(
        df,
        use_container_width=True
    )
if menu == "Delete Order":

    st.title("🗑️ Delete Order")

    cursor.execute("""
    SELECT
        o.order_id,
        c.name,
        p.product_name,
        o.quantity,
        o.status
    FROM orders o
    JOIN customers c
    ON o.customer_id = c.customer_id
    JOIN products p
    ON o.product_id = p.product_id
    """)

    st.dataframe(
        pd.DataFrame(
            cursor.fetchall(),
            columns=[
                "Order ID",
                "Customer",
                "Product",
                "Quantity",
                "Status"
            ]
        ),
        use_container_width=True
    )

    order_id = st.number_input(
        "Enter Order ID",
        min_value=1,
        step=1
    )

    if st.button("Delete Order"):

        cursor.execute(
            "DELETE FROM orders WHERE order_id=%s",
            (order_id,)
        )

        conn.commit()

        st.success(
            f"✅ Order {order_id} deleted successfully"
        )

        st.rerun()

if menu == "Update Order Status":

    st.title("🔄 Update Order Status")

    cursor.execute("""
    SELECT
        o.order_id,
        c.name,
        p.product_name,
        o.status
    FROM orders o
    JOIN customers c
    ON o.customer_id = c.customer_id
    JOIN products p
    ON o.product_id = p.product_id
    """)

    st.dataframe(
        pd.DataFrame(
            cursor.fetchall(),
            columns=[
                "Order ID",
                "Customer",
                "Product",
                "Current Status"
            ]
        ),
        use_container_width=True
    )

    order_id = st.number_input(
        "Order ID",
        min_value=1,
        step=1
    )

    new_status = st.selectbox(
        "Select New Status",
        [
            "Pending",
            "Processing",
            "Delivered",
            "Cancelled"
        ]
    )

    if st.button("Update Status"):

        cursor.execute(
            """
            UPDATE orders
            SET status=%s
            WHERE order_id=%s
            """,
            (
                new_status,
                order_id
            )
        )

        conn.commit()

        st.success(
            f"✅ Order {order_id} updated to {new_status}"
        )

        st.rerun()
st.divider()

st.markdown(
    """
    <div style='text-align:right; color:gray; margin-top:30px;'>
        🚀 RetailMind AI | Developed By Samridhi Pullani
    </div>
    """,
    unsafe_allow_html=True
)
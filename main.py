import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from functools import reduce

# Configure page settings
st.set_page_config(page_title="ShopEasy Dashboard", layout="wide")
st.title("📊 ShopEasy Sales Analytics & Inventory Management Dashboard")


# ==========================================
# Data Preparation Module (Automatically generate 50+ records)
# ==========================================
@st.cache_data
def load_or_create_data():
    # 1. Generate sales dataset (at least 50 records)
    np.random.seed(42)
    categories = ['Electronics', 'Clothing', 'Home & Kitchen', 'Books', 'Beauty']
    products_pool = {
        'Electronics': ['Smartphone', 'Laptop', 'Headphones', 'Smartwatch', 'Tablet'],
        'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Sneakers', 'Socks'],
        'Home & Kitchen': ['Blender', 'Coffee Maker', 'Air Fryer', 'Toaster', 'Vacuum'],
        'Books': ['Fiction Novel', 'Sci-Fi Book', 'Biography', 'Cookbook', 'Tech Guide'],
        'Beauty': ['Lipstick', 'Sunscreen', 'Perfume', 'Moisturizer', 'Shampoo']
    }

    sales_records = []
    start_date = datetime(2026, 1, 1)

    for i in range(60):  # Generate 60 records
        cat = np.random.choice(categories)
        prod = np.random.choice(products_pool[cat])
        qty = int(np.random.randint(1, 10))
        unit_p = float(np.random.randint(15, 1200))
        days_offset = int(np.random.randint(0, 150))
        sale_date = start_date + timedelta(days=days_offset)

        sales_records.append({
            "Product Name": prod,
            "Category": cat,
            "Quantity Sold": qty,
            "Unit Price": unit_p,
            "Date of Sale": sale_date.date()
        })

    df_sales = pd.DataFrame(sales_records)
    df_sales["Revenue"] = df_sales["Quantity Sold"] * df_sales["Unit Price"]

    # 2. Generate a separate inventory dataset
    inventory_records = []
    for cat, prods in products_pool.items():
        for prod in prods:
            inventory_records.append({
                "Product Name": prod,
                "Category": cat,
                "Stock Quantity": int(np.random.randint(5, 50))
            })
    df_inventory = pd.DataFrame(inventory_records)

    return df_sales, df_inventory


# Load datasets
df_sales, df_inventory = load_or_create_data()

# Automatically export CSV files
df_sales.to_csv("sales_data.csv", index=False)
df_inventory.to_csv("inventory_data.csv", index=False)

# ==========================================
# Sidebar Filters
# ==========================================
st.sidebar.header("🔍 Filter Options")

# Category filter
all_categories = ['All'] + list(df_sales['Category'].unique())
selected_category = st.sidebar.selectbox("Select Product Category", all_categories)

# Date range filter
min_date = df_sales['Date of Sale'].min()
max_date = df_sales['Date of Sale'].max()
date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Apply filtering logic
df_sales_filtered = df_sales.copy()
if selected_category != 'All':
    df_sales_filtered = df_sales_filtered[
        df_sales_filtered['Category'] == selected_category
    ]

if len(date_range) == 2:
    start_dt, end_dt = date_range
    df_sales_filtered = df_sales_filtered[
        (df_sales_filtered['Date of Sale'] >= start_dt) &
        (df_sales_filtered['Date of Sale'] <= end_dt)
    ]

# ==========================================
# Section B(a): Key Business Metrics and Dynamic Table
# ==========================================
st.subheader("📈 Key Business Metrics & Filtered Data")

# Calculate KPI metrics
if not df_sales_filtered.empty:
    total_revenue = df_sales_filtered['Revenue'].sum()
    total_units_sold = df_sales_filtered['Quantity Sold'].sum()
    avg_selling_price = df_sales_filtered['Unit Price'].mean()
else:
    total_revenue, total_units_sold, avg_selling_price = 0, 0, 0

# Display metric cards
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Units Sold", f"{total_units_sold:,}")
col3.metric("Average Selling Price", f"${avg_selling_price:,.2f}")

# Display filtered sales table
st.write("#### Filtered Sales Dataset")
st.dataframe(df_sales_filtered, use_container_width=True)

# ==========================================
# Section B(b): Data Visualization
# ==========================================
st.markdown("---")
st.subheader("📊 Visualizations")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.write("#### Total Revenue by Product Category")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    rev_by_cat = df_sales_filtered.groupby('Category')['Revenue'].sum().reset_index()
    sns.barplot(data=rev_by_cat, x='Category', y='Revenue',
                palette='Blues_r', ax=ax1)
    ax1.set_ylabel("Revenue ($)")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

with col_chart2:
    st.write("#### Sales Trend Over Time (Weekly)")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    df_sales_filtered['Date_Parsed'] = pd.to_datetime(
        df_sales_filtered['Date of Sale']
    )
    trend_df = df_sales_filtered.set_index(
        'Date_Parsed'
    ).resample('W')['Revenue'].sum().reset_index()

    sns.lineplot(
        data=trend_df,
        x='Date_Parsed',
        y='Revenue',
        marker='o',
        color='green',
        ax=ax2
    )

    ax2.set_xlabel("Date")
    ax2.set_ylabel("Revenue ($)")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

# Optional third chart: Revenue market share pie chart
st.write("#### Product Category Market Share (Revenue %)")
fig3, ax3 = plt.subplots(figsize=(5, 5))
cat_share = df_sales_filtered.groupby('Category')['Revenue'].sum()

ax3.pie(
    cat_share,
    labels=cat_share.index,
    autopct='%1.1f%%',
    colors=sns.color_palette('pastel'),
    startangle=90
)

ax3.axis('equal')
st.pyplot(fig3)

# ==========================================
# Section B(c): Inventory Management (Functional Programming Application)
# ==========================================
st.markdown("---")
st.subheader("📦 Inventory Management Section")

# User-defined inventory threshold
threshold = st.slider(
    "Set Low-Stock Alert Threshold",
    min_value=5,
    max_value=40,
    value=20
)

# Convert DataFrame to list of dictionaries for functional programming
inventory_list = df_inventory.to_dict('records')

# Use functional programming (filter) to identify low-stock items
low_stock_items = list(
    filter(lambda x: x['Stock Quantity'] < threshold, inventory_list)
)

# Apply category filter to inventory alerts
if selected_category != 'All':
    low_stock_items = list(
        filter(lambda x: x['Category'] == selected_category, low_stock_items)
    )

# Display warning alerts
if len(low_stock_items) > 0:
    st.warning(
        f"⚠️ Alert: There are {len(low_stock_items)} items below the threshold of {threshold} units!"
    )
else:
    st.success("✅ All stock levels are sufficient.")


# Highlight inventory rows based on stock status
def highlight_stock(row):
    return [
        'background-color: #ffcccc'
        if row['Stock Quantity'] < threshold
        else 'background-color: #d4edda'
        for _ in row
    ]


st.write("#### Full Inventory Status Table (Red indicates Low Stock)")
df_inventory_filtered = df_inventory.copy()

if selected_category != 'All':
    df_inventory_filtered = df_inventory_filtered[
        df_inventory_filtered['Category'] == selected_category
    ]

st.dataframe(
    df_inventory_filtered.style.apply(highlight_stock, axis=1),
    use_container_width=True
)
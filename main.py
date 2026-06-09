import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from functools import reduce

# 设置页面配置
st.set_page_config(page_title="ShopEasy Dashboard", layout="wide")
st.title("📊 ShopEasy Sales Analytics & Inventory Management Dashboard")


# ==========================================
# 数据准备模块 (自动生成符合要求的50+行数据)
# ==========================================
@st.cache_data
def load_or_create_data():
    # 1. 生成销售数据 (至少50行)
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

    for i in range(60):  # 生成60行数据
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

    # 2. 生成独立的库存数据
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


# 加载数据
df_sales, df_inventory = load_or_create_data()

# ==========================================
# 侧边栏过滤器 (Sidebar Filters)
# ==========================================
st.sidebar.header("🔍 Filter Options")

# 类别过滤
all_categories = ['All'] + list(df_sales['Category'].unique())
selected_category = st.sidebar.selectbox("Select Product Category", all_categories)

# 日期范围过滤
min_date = df_sales['Date of Sale'].min()
max_date = df_sales['Date of Sale'].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# 应用过滤逻辑
df_sales_filtered = df_sales.copy()
if selected_category != 'All':
    df_sales_filtered = df_sales_filtered[df_sales_filtered['Category'] == selected_category]

if len(date_range) == 2:
    start_dt, end_dt = date_range
    df_sales_filtered = df_sales_filtered[
        (df_sales_filtered['Date of Sale'] >= start_dt) & (df_sales_filtered['Date of Sale'] <= end_dt)]

# ==========================================
# Section B(a): 核心业务指标与动态表格
# ==========================================
st.subheader("📈 Key Business Metrics & Filtered Data")

# 计算指标
if not df_sales_filtered.empty:
    total_revenue = df_sales_filtered['Revenue'].sum()
    total_units_sold = df_sales_filtered['Quantity Sold'].sum()
    avg_selling_price = df_sales_filtered['Unit Price'].mean()
else:
    total_revenue, total_units_sold, avg_selling_price = 0, 0, 0

# 显示Metric Cards
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Units Sold", f"{total_units_sold:,}")
col3.metric("Average Selling Price", f"${avg_selling_price:,.2f}")

# 显示动态数据表
st.write("#### Filtered Sales Dataset")
st.dataframe(df_sales_filtered, use_container_width=True)

# ==========================================
# Section B(b): 数据可视化部分
# ==========================================
st.markdown("---")
st.subheader("📊 Visualizations")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.write("#### Total Revenue by Product Category")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    rev_by_cat = df_sales_filtered.groupby('Category')['Revenue'].sum().reset_index()
    sns.barplot(data=rev_by_cat, x='Category', y='Revenue', palette='Blues_r', ax=ax1)
    ax1.set_ylabel("Revenue ($)")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

with col_chart2:
    st.write("#### Sales Trend Over Time (Weekly)")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    df_sales_filtered['Date_Parsed'] = pd.to_datetime(df_sales_filtered['Date of Sale'])
    trend_df = df_sales_filtered.set_index('Date_Parsed').resample('W')['Revenue'].sum().reset_index()
    sns.lineplot(data=trend_df, x='Date_Parsed', y='Revenue', marker='o', color='green', ax=ax2)
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Revenue ($)")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

# 自选第三个图表：饼图展示销售额占比
st.write("#### Product Category Market Share (Revenue %)")
fig3, ax3 = plt.subplots(figsize=(5, 5))
cat_share = df_sales_filtered.groupby('Category')['Revenue'].sum()
ax3.pie(cat_share, labels=cat_share.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'), startangle=90)
ax3.axis('equal')
st.pyplot(fig3)

# ==========================================
# Section B(c): 库存管理部分（函数式编程应用）
# ==========================================
st.markdown("---")
st.subheader("📦 Inventory Management Section")

# 用户定义阈值
threshold = st.slider("Set Low-Stock Alert Threshold", min_value=5, max_value=40, value=20)

# 将DataFrame转换为字典列表以应用函数式编程
inventory_list = df_inventory.to_dict('records')

# 使用 functional programming (filter) 识别低库存
low_stock_items = list(filter(lambda x: x['Stock Quantity'] < threshold, inventory_list))

# 侧边栏对库存的过滤（联动响应）
if selected_category != 'All':
    low_stock_items = list(filter(lambda x: x['Category'] == selected_category, low_stock_items))

# 提示警告弹窗
if len(low_stock_items) > 0:
    st.warning(f"⚠️ Alert: There are {len(low_stock_items)} items below the threshold of {threshold} units!")
else:
    st.success("✅ All stock levels are sufficient.")


# 高亮显示库存状态的表格
def highlight_stock(row):
    return ['background-color: #ffcccc' if row['Stock Quantity'] < threshold else 'background-color: #d4edda' for _ in
            row]


st.write("#### Full Inventory Status Table (Red indicates Low Stock)")
df_inventory_filtered = df_inventory.copy()
if selected_category != 'All':
    df_inventory_filtered = df_inventory_filtered[df_inventory_filtered['Category'] == selected_category]

st.dataframe(df_inventory_filtered.style.apply(highlight_stock, axis=1), use_container_width=True)
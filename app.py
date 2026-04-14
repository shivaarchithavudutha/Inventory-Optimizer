import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="FMCG Supply Chain Optimizer", layout="wide")
st.title("FMCG Supply Chain Inventory Optimizer")
st.markdown("### Decision Support System for Inventory & Procurement")

# 2. Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('supply_chain_data.csv')
    # Pre-calculating the stats 
    stats = df.groupby('Product').agg(
        Annual_Demand=('Units_Sold', 'sum'),
        Daily_Std=('Units_Sold', 'std'),
        Avg_Daily=('Units_Sold', 'mean'),
        Unit_Cost=('Unit_Cost', 'first'),
        Holding_Cost=('Holding_Cost_Per_Unit', 'first'),
        Lead_Time=('Lead_Time_Days', 'first'),
        Order_Cost=('Ordering_Cost', 'first')
    ).reset_index()
    
    # Apply formulas
    stats['EOQ'] = stats.apply(lambda x: round(((2 * x['Annual_Demand'] * x['Order_Cost']) / x['Holding_Cost'])**0.5), axis=1)
    stats['Safety_Stock'] = stats.apply(lambda x: round(1.65 * x['Daily_Std'] * (x['Lead_Time']**0.5)), axis=1)
    stats['Reorder_Point'] = round((stats['Avg_Daily'] * stats['Lead_Time']) + stats['Safety_Stock'])
    return df, stats

df, stats = load_data()

# 3. Sidebar Filters
product_list = stats['Product'].unique()
selected_product = st.sidebar.selectbox("Select Product to Analyze", product_list)

# 4. Top Level Metrics
st.header(f"Insights for: {selected_product}")
p_stats = stats[stats['Product'] == selected_product].iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Optimal Order (EOQ)", f"{p_stats['EOQ']} units")
col2.metric("Safety Stock", f"{p_stats['Safety_Stock']} units")
col3.metric("Reorder Point", f"{p_stats['Reorder_Point']} units")
col4.metric("Avg Daily Demand", f"{round(p_stats['Avg_Daily'])} units")

# 5. Visualizations
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Sales Trend (Last 30 Days)")
    product_df = df[df['Product'] == selected_product].tail(30)
    fig = px.line(product_df, x='Date', y='Units_Sold', title="Daily Units Sold")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Efficiency Metrics")
    # Comparison of EOQ vs Annual Demand
    fig2 = px.bar(stats, x='Product', y='EOQ', color='Product', title="EOQ by Product Category")
    st.plotly_chart(fig2, use_container_width=True)

# 6. Actionable Advice
st.info(f" **Procurement Advice:** You should place a new order for **{selected_product}** whenever your warehouse stock hits **{p_stats['Reorder_Point']}** units. Your most cost-effective order size is **{p_stats['EOQ']}** units.")

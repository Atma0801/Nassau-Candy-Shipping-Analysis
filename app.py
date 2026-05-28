import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Nassau Candy Dashboard",
    layout="wide"
)

# -----------------------------------
# TITLE
# -----------------------------------
st.markdown(
    """
    <h1 style='text-align: center; color: #FF4B4B;'>
    Nassau Candy Shipping Route Efficiency Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# LOAD DATA
# -----------------------------------
df = pd.read_csv("Nassau Candy Distributor.csv")

# -----------------------------------
# DATE CONVERSION
# -----------------------------------
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)

# -----------------------------------
# LEAD TIME
# -----------------------------------
df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

# -----------------------------------
# SIDEBAR FILTERS
# -----------------------------------
st.sidebar.header("Filters")

selected_region = st.sidebar.multiselect(
    "Select Region",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

selected_ship_mode = st.sidebar.multiselect(
    "Select Ship Mode",
    options=df['Ship Mode'].unique(),
    default=df['Ship Mode'].unique()
)

# Apply filters
filtered_df = df[
    (df['Region'].isin(selected_region)) &
    (df['Ship Mode'].isin(selected_ship_mode))
]

# -----------------------------------
# KPI SECTION
# -----------------------------------
avg_lead = round(filtered_df['Lead Time'].mean(), 2)
total_shipments = len(filtered_df)

delay_threshold = 1300
filtered_df['Delayed'] = filtered_df['Lead Time'] > delay_threshold

delay_percentage = round(
    filtered_df['Delayed'].mean() * 100,
    2
)

st.subheader("Key Performance Indicators")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Average Lead Time",
    avg_lead
)

col2.metric(
    "Total Shipments",
    total_shipments
)

col3.metric(
    "Delay Percentage",
    f"{delay_percentage}%"
)

# -----------------------------------
# SHIP MODE ANALYSIS
# -----------------------------------
st.markdown("---")
st.header("Ship Mode Performance Analysis")

ship_mode_analysis = filtered_df.groupby(
    'Ship Mode'
).agg(
    Average_Lead_Time=('Lead Time', 'mean')
).reset_index()

fig1, ax1 = plt.subplots(figsize=(8,5))

colors1 = ['#FF6B6B', '#4ECDC4', '#FFD93D', '#1A936F']

ax1.bar(
    ship_mode_analysis['Ship Mode'],
    ship_mode_analysis['Average_Lead_Time'],
    color=colors1
)

ax1.set_title(
    'Average Lead Time by Ship Mode',
    fontsize=14,
    fontweight='bold'
)

ax1.set_xlabel('Ship Mode')
ax1.set_ylabel('Average Lead Time')

st.pyplot(fig1)

# -----------------------------------
# REGION ANALYSIS
# -----------------------------------
st.markdown("---")
st.header("Regional Shipping Analysis")

region_analysis = filtered_df.groupby(
    'Region'
).agg(
    Average_Lead_Time=('Lead Time', 'mean')
).reset_index()

fig2, ax2 = plt.subplots(figsize=(8,5))

colors2 = ['#6A4C93', '#1982C4', '#8AC926', '#FFCA3A']

ax2.pie(
    region_analysis['Average_Lead_Time'],
    labels=region_analysis['Region'],
    autopct='%1.1f%%',
    colors=colors2
)

ax2.set_title(
    'Regional Lead Time Distribution',
    fontsize=14,
    fontweight='bold'
)

st.pyplot(fig2)

# -----------------------------------
# TOP 10 SLOWEST ROUTES
# -----------------------------------
st.markdown("---")
st.header("Top 10 Slowest Shipping Routes")

# Factory Mapping
factory_map = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack",
    "Fizzy Lifting Drinks": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Hair Toffee": "The Other Factory",
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory",
    "Kazookles": "The Other Factory"
}

# Create Factory Column
filtered_df['Factory'] = filtered_df['Product Name'].map(factory_map)

# Create Route
filtered_df['Route'] = (
    filtered_df['Factory']
    + " → "
    + filtered_df['State/Province']
)

# Route Analysis
route_analysis = filtered_df.groupby('Route').agg(
    Average_Lead_Time=('Lead Time', 'mean'),
    Total_Shipments=('Order ID', 'count')
).reset_index()

# Slowest Routes
slowest_routes = route_analysis.sort_values(
    by='Average_Lead_Time',
    ascending=False
).head(10)

# Plot
fig6, ax6 = plt.subplots(figsize=(14,6))

ax6.barh(
    slowest_routes['Route'],
    slowest_routes['Average_Lead_Time'],
    color='darkred'
)

ax6.set_title(
    'Top 10 Slowest Shipping Routes',
    fontsize=14,
    fontweight='bold'
)

ax6.set_xlabel('Average Lead Time')
ax6.set_ylabel('Route')

plt.gca().invert_yaxis()

st.pyplot(fig6)

# -----------------------------------
# STATE BOTTLENECK ANALYSIS
# -----------------------------------
st.markdown("---")
st.header("Top 10 Bottleneck States")

state_analysis = filtered_df.groupby(
    'State/Province'
).agg(
    Average_Lead_Time=('Lead Time', 'mean'),
    Total_Shipments=('Order ID', 'count')
).reset_index()

top_states = state_analysis.sort_values(
    by='Average_Lead_Time',
    ascending=False
).head(10)

fig3, ax3 = plt.subplots(figsize=(12,6))

ax3.barh(
    top_states['State/Province'],
    top_states['Average_Lead_Time'],
    color='crimson'
)

ax3.set_title(
    'Top 10 States with Highest Average Lead Time',
    fontsize=14,
    fontweight='bold'
)

ax3.set_xlabel('Average Lead Time')
ax3.set_ylabel('State')

st.pyplot(fig3)

# -----------------------------------
# TOP SHIPMENT STATES
# -----------------------------------
st.markdown("---")
st.header("Top Shipment Volume States")

top_volume_states = state_analysis.sort_values(
    by='Total_Shipments',
    ascending=False
).head(10)

fig4, ax4 = plt.subplots(figsize=(12,6))

ax4.plot(
    top_volume_states['State/Province'],
    top_volume_states['Total_Shipments'],
    marker='o',
    linewidth=3,
    color='#FF4B4B'
)

ax4.set_title(
    'Top States by Shipment Volume',
    fontsize=14,
    fontweight='bold'
)

ax4.set_xlabel('State')
ax4.set_ylabel('Total Shipments')

plt.xticks(rotation=45)

st.pyplot(fig4)

# -----------------------------------
# DELAY ANALYSIS
# -----------------------------------
st.markdown("---")
st.header("Delay Distribution Analysis")

delay_counts = filtered_df['Delayed'].value_counts()

fig5, ax5 = plt.subplots(figsize=(7,7))

colors5 = ['#2ECC71', '#E74C3C']

ax5.pie(
    delay_counts,
    labels=['Not Delayed', 'Delayed'],
    autopct='%1.1f%%',
    colors=colors5,
    explode=(0, 0.1),
    shadow=True
)

ax5.set_title(
    'Delayed vs Non-Delayed Shipments',
    fontsize=14,
    fontweight='bold'
)

st.pyplot(fig5)

# -----------------------------------
# DATA PREVIEW
# -----------------------------------
st.markdown("---")
st.header("Dataset Preview")

st.dataframe(filtered_df.head(20))

# -----------------------------------
# FOOTER
# -----------------------------------
st.markdown("---")

st.markdown(
    """
    <center>
    <h4 style='color: gray;'>
    Developed using Python, Pandas, Matplotlib & Streamlit
    </h4>
    </center>
    """,
    unsafe_allow_html=True
)
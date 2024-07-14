import pandas as pd
import streamlit as st
import altair as alt
import json
import os

# Define file paths
frontend_data_path = os.path.join(os.path.dirname(__file__), 'frontend_data.json')
currency_data_path = os.path.join(os.path.dirname(__file__), 'currency.json')

# Load data from JSON files
try:
    with open(frontend_data_path) as f:
        data = json.load(f)
except FileNotFoundError:
    st.error(f"File not found: {frontend_data_path}")
    st.stop()

try:
    with open(currency_data_path) as f:
        currency_data = json.load(f)
except FileNotFoundError:
    st.error(f"File not found: {currency_data_path}")
    st.stop()

# Ensure correct timestamp format
for item in data:
    if isinstance(item['timestamp'], dict) and '$date' in item['timestamp']:
        item['timestamp'] = item['timestamp']['$date']

# Normalize MongoDB data to DataFrame
df = pd.DataFrame(data)
currency_df = pd.json_normalize(currency_data)

# Attempt to find the correct path for timestamp
timestamp_column = None
for col in df.columns:
    if 'timestamp' in col:
        timestamp_column = col
        break

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df[timestamp_column])

# Convert to naive datetime if timezone-aware
if df['timestamp'].dt.tz:
    df['timestamp'] = df['timestamp'].dt.tz_convert(None)

# Streamlit app
st.markdown(f"<h1 style='text-align: center;'>WETH Daily Inflows and Accumulation</h1>", unsafe_allow_html=True)

# Date filter
start_date = st.date_input('Start date', df['timestamp'].min().date())
end_date = st.date_input('End date', df['timestamp'].max().date())

# Convert start_date and end_date to Timestamps
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)

# Filter data based on date input
filtered_df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]

# Sort data by timestamp ascending
filtered_df = filtered_df.sort_values(by='timestamp', ascending=True)

# Calculate cumulative sum of weth_marketplace
filtered_df['cumulative_weth_marketplace'] = filtered_df['weth_marketplace'].cumsum()

# Format values to 2 decimal places
filtered_df['weth_marketplace'] = filtered_df['weth_marketplace'].round(2)
filtered_df['cumulative_weth_marketplace'] = filtered_df['cumulative_weth_marketplace'].round(2)

# Fetch WETH price from the latest document in the "currency" collection
latest_weth_price = currency_df['weth_price'].iloc[0]

# Calculate total value in USD
total_weth_marketplace = filtered_df['weth_marketplace'].sum()
total_value_usd = total_weth_marketplace * latest_weth_price

st.markdown(f"<h3 style='text-align: center;'>Total WETH: {total_weth_marketplace:,.2f} (${total_value_usd:,.2f})</h3>", unsafe_allow_html=True)

# Define a selection interval for zooming and panning
selection = alt.selection_interval(bind='scales')

# Create Altair line chart for cumulative WETH marketplace value
cumulative_chart = alt.Chart(filtered_df).mark_bar().encode(
    x=alt.X('timestamp:T', axis=alt.Axis(format='%d-%m-%Y', title='Date')),
    y=alt.Y('cumulative_weth_marketplace:Q', title='Cumulative WETH')
).properties(
    title='Cumulative Sum of WETH Values'
).add_params(
    selection
)

st.altair_chart(cumulative_chart, use_container_width=True)

# Create Altair bar chart for daily WETH marketplace value
daily_chart = alt.Chart(filtered_df).mark_bar().encode(
    x=alt.X('timestamp:T', axis=alt.Axis(format='%d-%m-%Y', title='Date')),
    y=alt.Y('weth_marketplace:Q', title='Daily WETH')
).properties(
    title='Daily WETH Values'
).add_params(
    selection
)

st.altair_chart(daily_chart, use_container_width=True)

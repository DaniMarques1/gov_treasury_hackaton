import pandas as pd
import streamlit as st
import altair as alt
import json
import os

# Define paths for data files
frontend_data_path = os.path.join(os.path.dirname(__file__), 'frontend_data.json')
currency_data_path = os.path.join(os.path.dirname(__file__), 'currency.json')

# Load data from JSON files
with open(frontend_data_path) as f:
    data = json.load(f)

with open(currency_data_path) as f:
    currency_data = json.load(f)

# Ensure correct timestamp format
for item in data:
    if isinstance(item['timestamp'], dict) and '$date' in item['timestamp']:
        item['timestamp'] = item['timestamp']['$date']

# Create DataFrame
df = pd.DataFrame(data)

# Ensure timestamp is in datetime format
if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
    df['timestamp'] = pd.to_datetime(df['timestamp'])

# Rename 'timestamp' to 'Date'
df.rename(columns={'timestamp': 'Date'}, inplace=True)

# Sort DataFrame by Date
df = df.sort_values('Date')

# Compute cumulative and daily values
df['Ascension'] = df['axs_ascending'].cumsum()
df['Breeding'] = df['axs_breeding'].cumsum()
df['Parts Evolution'] = df['axs_partsEvol'].cumsum()
df['R&C Mint'] = df['axs_r&cMint'].cumsum()
df['Daily AXS'] = df[['axs_ascending', 'axs_breeding', 'axs_partsEvol', 'axs_r&cMint']].sum(axis=1)
df['Cumulative Total AXS'] = df['Daily AXS'].cumsum()

# Reshape data for cumulative chart
cumulative_df = df[['Date', 'Ascension', 'Breeding', 'Parts Evolution', 'R&C Mint', 'Cumulative Total AXS', 'axs_ascending', 'axs_breeding', 'axs_partsEvol', 'axs_r&cMint']].melt(
    id_vars=['Date', 'Cumulative Total AXS', 'axs_ascending', 'axs_breeding', 'axs_partsEvol', 'axs_r&cMint'],
    var_name='Category',
    value_name='AXS'
)

# Map the original column names to the desired category names
category_map = {
    'axs_ascending': 'Ascension',
    'axs_breeding': 'Breeding',
    'axs_partsEvol': 'Parts Evolution',
    'axs_r&cMint': 'R&C Mint'
}

# Reshape data for daily chart
daily_df = df[['Date', 'axs_ascending', 'axs_breeding', 'axs_partsEvol', 'axs_r&cMint', 'Daily AXS']].melt(
    id_vars=['Date', 'Daily AXS'],
    var_name='Category',
    value_name='AXS'
)

# Map the original column names to the desired category names in the daily_df
daily_df['Category'] = daily_df['Category'].map(category_map)

# Add other daily values to the reshaped DataFrame for tooltips
daily_df = daily_df.merge(df[['Date', 'axs_ascending', 'axs_breeding', 'axs_partsEvol', 'axs_r&cMint']], on='Date', how='left')

st.markdown(f"<h1 style='text-align: center;'>AXS Daily Inflows and Accumulation</h1>", unsafe_allow_html=True)

# Date input
start_date = st.date_input('Start date', value=pd.to_datetime('2024-01-01').date(), min_value=pd.to_datetime('2024-01-01').date())
end_date = st.date_input('End date', value=df['Date'].max().date())

# Filter data based on selected date range
filtered_cumulative_df = cumulative_df[(cumulative_df['Date'].dt.date >= start_date) & (cumulative_df['Date'].dt.date <= end_date)]
filtered_daily_df = daily_df[(daily_df['Date'].dt.date >= start_date) & (daily_df['Date'].dt.date <= end_date)]

# Calculate accumulated sums for each inflow type using the filter
accumulated_ascension = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['axs_ascending'].sum()
accumulated_breeding = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['axs_breeding'].sum()
accumulated_parts_evol = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['axs_partsEvol'].sum()
accumulated_rc_mint = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['axs_r&cMint'].sum()
accumulated_total_axs = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['Daily AXS'].sum()

# Function to get the latest AXS price from the currency data
def get_current_axs_price():
    latest_currency = currency_data[-1]
    if 'axs_price' in latest_currency:
        return latest_currency['axs_price']
    else:
        return None

# Get the current AXS price and calculate total value in USD
current_axs_price = get_current_axs_price()
if current_axs_price is not None:
    total_value_usd = accumulated_total_axs * current_axs_price
else:
    total_value_usd = None

# Display the accumulated total AXS in a single metric box above the others
if total_value_usd is not None:
    st.markdown(f"<h3 style='text-align: center;'>Total AXS: {accumulated_total_axs:,.2f} (${total_value_usd:,.2f})</h3>", unsafe_allow_html=True)
else:
    st.markdown(f"<h3 style='text-align: center;'>Total AXS: {accumulated_total_axs:,.2f} (Price data not available)</h3>", unsafe_allow_html=True)

# Display the accumulated sums in metric boxes side by side
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Ascension", value=f"{accumulated_ascension:,.2f}")
col2.metric(label="Breeding", value=f"{accumulated_breeding:,.2f}")
col3.metric(label="Parts Evolution", value=f"{accumulated_parts_evol:,.2f}")
col4.metric(label="R&C Mint", value=f"{accumulated_rc_mint:,.2f}")

# Define tooltip for cumulative and daily charts
tooltip_cumulative = [
    alt.Tooltip('Date:T', title='Date'),
    alt.Tooltip('Cumulative Total AXS:Q', title='Cumulative Total AXS', format=",.2f"),
    alt.Tooltip('axs_ascending:Q', title='Daily Ascension', format=",.2f"),
    alt.Tooltip('axs_breeding:Q', title='Daily Breeding', format=",.2f"),
    alt.Tooltip('axs_partsEvol:Q', title='Daily Parts Evolution', format=",.2f"),
    alt.Tooltip('axs_r&cMint:Q', title='Daily R&C Mint', format=",.2f"),
]

tooltip_daily = [
    alt.Tooltip('Date:T', title='Date'),
    alt.Tooltip('Daily AXS:Q', title='Total Daily AXS', format=",.2f"),
    alt.Tooltip('axs_ascending:Q', title='Daily Ascension', format=",.2f"),
    alt.Tooltip('axs_breeding:Q', title='Daily Breeding', format=",.2f"),
    alt.Tooltip('axs_partsEvol:Q', title='Daily Parts Evolution', format=",.2f"),
    alt.Tooltip('axs_r&cMint:Q', title='Daily R&C Mint', format=",.2f")
]

# Chart 1: Cumulative Sum of AXS Values
chart_cumulative = alt.Chart(filtered_cumulative_df).mark_bar().encode(
    x='Date:T',
    y=alt.Y('AXS:Q', title='Cumulative AXS'),
    color='Category:N',
    tooltip=tooltip_cumulative
).properties(
    title='Cumulative Sum of AXS Values'
).interactive()

st.altair_chart(chart_cumulative, use_container_width=True)

# Chart 2: Daily Sum of AXS Values
chart_daily_axs = alt.Chart(filtered_daily_df).mark_bar().encode(
    x='Date:T',
    y=alt.Y('AXS:Q', title='Daily AXS'),
    color='Category:N',
    tooltip=tooltip_daily
).properties(
    title='Daily AXS Values by Category'
).interactive()

st.altair_chart(chart_daily_axs, use_container_width=True)

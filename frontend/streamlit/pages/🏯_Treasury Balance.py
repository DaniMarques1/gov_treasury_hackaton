import json
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Path to the JSON files
treasury_data_path = os.path.join(os.path.dirname(__file__), 'balance.json')
currency_data_path = os.path.join(os.path.dirname(__file__), 'currency.json')
frontend_data_path = os.path.join(os.path.dirname(__file__), 'frontend_data.json')

# Read the JSON file for treasury data
with open(treasury_data_path, 'r') as f:
    treasury_data = json.load(f)

# Read the JSON file for currency data
try:
    with open(currency_data_path) as f:
        currency_data = json.load(f)
except FileNotFoundError:
    st.error(f"File not found: {currency_data_path}")
    st.stop()

# Convert the currency data to a pandas DataFrame
currency_df = pd.json_normalize(currency_data)

# Extract the most recent entry from the treasury data
most_recent_entry = treasury_data[-1]  # Assuming the most recent entry is the last one in the list
items = most_recent_entry['result']['items']

# Convert data to a pandas DataFrame
df = pd.DataFrame(items)

# Filter for tokenSymbol "AXS" and "WETH"
df = df[df['tokenSymbol'].isin(['AXS', 'WETH'])]

# Ensure the std_value values are in numerical format
df['std_value'] = df['std_value'].astype(float)

# Extract the most recent currency exchange rates
latest_currency_entry = currency_data[-1]
axs_to_usd_rate = latest_currency_entry['axs_price']
weth_to_usd_rate = latest_currency_entry['weth_price']

# Extract the latest timestamp from the currency data
latest_currency_timestamp = latest_currency_entry['timestamp']
# Convert to human-readable format
latest_currency_timestamp_human = datetime.fromisoformat(latest_currency_timestamp).strftime('%d %B %Y, %H:%M:%S')

# Calculate converted values
df.loc[df['tokenSymbol'] == 'AXS', 'converted_value'] = df['std_value'] * axs_to_usd_rate
df.loc[df['tokenSymbol'] == 'WETH', 'converted_value'] = df['std_value'] * weth_to_usd_rate

# Streamlit page configuration
st.markdown(f"<h1 style='color: #4CAF50;'>Treasury Balance</h1>", unsafe_allow_html=True)
st.markdown(f"<h5 style='color: #777;'>As of: {latest_currency_timestamp_human}</h5>", unsafe_allow_html=True)

# Add WETH and AXS prices below the 'As of:' line
st.markdown(
    f"<p style='font-size: 1.2em; color: #555;'>"
    f"<strong>WETH Price:</strong> ${weth_to_usd_rate:,.2f} | "
    f"<strong>AXS Price:</strong> ${axs_to_usd_rate:,.2f}"
    f"</p>",
    unsafe_allow_html=True
)

weth_value = df[df['tokenSymbol'] == 'WETH']['std_value'].values[0]
weth_converted_value = df[df['tokenSymbol'] == 'WETH']['converted_value'].values[0]
st.markdown(f"<h3>WETH: {weth_value:,.2f} <span style='font-size: 0.8em;'>(<strong>${weth_converted_value:,.2f}</strong>)</span></h3>", unsafe_allow_html=True)

axs_value = df[df['tokenSymbol'] == 'AXS']['std_value'].values[0]
axs_converted_value = df[df['tokenSymbol'] == 'AXS']['converted_value'].values[0]
st.markdown(f"<h3>AXS: {axs_value:,.2f} <span style='font-size: 0.8em;'>(<strong>${axs_converted_value:,.2f}</strong>)</span></h3>", unsafe_allow_html=True)

# Read the JSON file for frontend data
try:
    with open(frontend_data_path) as f:
        frontend_data = json.load(f)
except FileNotFoundError:
    st.error(f"File not found: {frontend_data_path}")
    st.stop()

# Convert the frontend data to a pandas DataFrame
frontend_df = pd.json_normalize(frontend_data)

# Ensure the weth_marketplace values are in numerical format
frontend_df['weth_marketplace'] = frontend_df['weth_marketplace'].astype(float)

# Calculate the sum of all weth_marketplace values
total_weth_marketplace = frontend_df['weth_marketplace'].sum()
missing_weth = weth_value - total_weth_marketplace
missing_percentage = (1 - total_weth_marketplace / weth_value) * 100

# Display the sum of weth_marketplace values
st.markdown(f"<h4>WETH Accumulated Since the Hack: {total_weth_marketplace:,.2f}</h4>", unsafe_allow_html=True)
st.markdown(f"<h4>Unbacked WETH from the Hack: {missing_weth:,.2f} <span style='font-size: 0.8em;'>(<strong>{missing_percentage:.2f}%</strong>)</span></h4>", unsafe_allow_html=True)

# Add the additional information
st.markdown(
    f"<p style='font-size: 1.1em;'>The <strong>{missing_weth:,.2f} ETH</strong> compromised from the Axie DAO treasury will remain undercollateralized as Sky Mavis works with law enforcement to recover the funds. "
    "If the funds are not fully recovered within two years, the Axie DAO will vote on next steps for the treasury.</p>", unsafe_allow_html=True
)

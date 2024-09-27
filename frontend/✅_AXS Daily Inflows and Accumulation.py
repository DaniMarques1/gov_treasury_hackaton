import pandas as pd
import streamlit as st
import altair as alt
import json
import os
import datetime

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
df['Altar Restore'] = df['axs_atia'].cumsum()  # New field for Atia
df['Daily AXS'] = df[['axs_ascending', 'axs_breeding', 'axs_partsEvol', 'axs_r&cMint', 'axs_atia']].sum(axis=1)  # Include axs_atia
df['Cumulative Total AXS'] = df['Daily AXS'].cumsum()

# Reshape data for cumulative chart
cumulative_df = df[['Date', 'Ascension', 'Breeding', 'Parts Evolution', 'R&C Mint', 'Altar Restore', 'Cumulative Total AXS', 'axs_ascending', 'axs_breeding', 'axs_partsEvol', 'axs_r&cMint', 'axs_atia']].melt(
    id_vars=['Date', 'Cumulative Total AXS', 'axs_ascending', 'axs_breeding', 'axs_partsEvol', 'axs_r&cMint', 'axs_atia'],
    var_name='Category',
    value_name='AXS'
)

# Reshape data for daily chart
daily_df = df[['Date', 'axs_ascending', 'axs_breeding', 'axs_partsEvol', 'axs_r&cMint', 'axs_atia', 'Daily AXS']].melt(
    id_vars=['Date', 'Daily AXS'],
    var_name='Category',
    value_name='AXS'
)

# Map the original column names to the desired category names in the daily_df
category_map = {
    'axs_ascending': 'Ascension',
    'axs_breeding': 'Breeding',
    'axs_partsEvol': 'Parts Evolution',
    'axs_r&cMint': 'R&C Mint',
    'axs_atia': 'Altar Restore'  # Add the new category for Atia
}

# Apply the category map
daily_df['Category'] = daily_df['Category'].map(category_map)

# Add other daily values to the reshaped DataFrame for tooltips
daily_df = daily_df.merge(df[['Date', 'axs_ascending', 'axs_breeding', 'axs_partsEvol', 'axs_r&cMint','axs_atia']], on='Date', how='left')

st.markdown(f"<h1 style='text-align: center;'>AXS Daily Inflows and Accumulation</h1>", unsafe_allow_html=True)

# Date input
start_date = st.date_input('Start date', value=pd.to_datetime('2024-01-01').date(), min_value=pd.to_datetime('2022-03-29').date())

end_date = st.date_input(
    'End date',
    value=df['Date'].max().date(),  # Use the latest date in the data
    min_value=df['Date'].min().date(),  # Ensure the end date can't be earlier than the earliest date
    max_value=df['Date'].max().date()  # Set the maximum selectable date to the latest date
)

# Filter data based on selected date range
filtered_cumulative_df = cumulative_df[(cumulative_df['Date'].dt.date >= start_date) & (cumulative_df['Date'].dt.date <= end_date)]
filtered_daily_df = daily_df[(daily_df['Date'].dt.date >= start_date) & (daily_df['Date'].dt.date <= end_date)]
breeding_df = daily_df[(daily_df['Category'] == 'Breeding') & (daily_df['Date'].dt.date >= start_date) & (daily_df['Date'].dt.date <= end_date)]
rc_mint_df = daily_df[(daily_df['Category'] == 'R&C Mint') & (daily_df['Date'].dt.date >= start_date) & (daily_df['Date'].dt.date <= end_date)]
parts_evol_df = daily_df[(daily_df['Category'] == 'Parts Evolution') & (daily_df['Date'].dt.date >= start_date) & (daily_df['Date'].dt.date <= end_date)]
ascension_df = daily_df[(daily_df['Category'] == 'Ascension') & (daily_df['Date'].dt.date >= start_date) & (daily_df['Date'].dt.date <= end_date)]

# Calculate accumulated sums for each inflow type using the filter
accumulated_ascension = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['axs_ascending'].sum()
accumulated_breeding = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['axs_breeding'].sum()
accumulated_parts_evol = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['axs_partsEvol'].sum()
accumulated_rc_mint = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['axs_r&cMint'].sum()
accumulated_atia = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['axs_atia'].sum()
accumulated_total_axs = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['Daily AXS'].sum()

# Function to get the latest AXS price and timestamp from the currency data
def get_current_axs_price_and_timestamp():
    latest_currency = currency_data[-1]  # Assuming the last entry is the most recent
    if 'axs_price' in latest_currency and 'timestamp' in latest_currency:
        axs_price = latest_currency['axs_price']
        axs_timestamp = pd.to_datetime(latest_currency['timestamp']['$date']) if isinstance(latest_currency['timestamp'], dict) and '$date' in latest_currency['timestamp'] else pd.to_datetime(latest_currency['timestamp'])
        return axs_price, axs_timestamp
    else:
        return None, None

# Get the current AXS price and timestamp
current_axs_price, axs_timestamp = get_current_axs_price_and_timestamp()

# Display the accumulated total AXS in a single metric box above the others
if current_axs_price is not None and axs_timestamp is not None:
    total_value_usd = accumulated_total_axs * current_axs_price
    st.markdown(f"<h3 style='text-align: center;'>Total AXS: {accumulated_total_axs:,.2f} (${total_value_usd:,.2f})</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: grey;'>AXS price: ${current_axs_price:.2f} ({axs_timestamp.strftime('%Y-%m-%d')})</p>", unsafe_allow_html=True)
else:
    st.markdown(f"<h3 style='text-align: center;'>Total AXS: {accumulated_total_axs:,.2f} (Price data not available)</h3>", unsafe_allow_html=True)
    if axs_timestamp is not None:
        st.markdown(f"<p style='text-align: center; color: grey;'>Current AXS Price: N/A (as of {axs_timestamp.strftime('%Y-%m-%d %H:%M:%S')})</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='text-align: center; color: grey;'>Current AXS Price: N/A</p>", unsafe_allow_html=True)

def format_large_number(num):
    if abs(num) >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif abs(num) >= 1_000:
        return f"{num / 1_000:.1f}k"
    else:
        return f"{num:.2f}"

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(label="Ascension", value=format_large_number(accumulated_ascension))
col2.metric(label="Breeding", value=format_large_number(accumulated_breeding))
col3.metric(label="Parts Evolution", value=format_large_number(accumulated_parts_evol))
col4.metric(label="R&C Mint", value=format_large_number(accumulated_rc_mint))
col5.metric(label="Altar Restore", value=format_large_number(accumulated_atia))


# Define tooltip for cumulative and daily charts
tooltip_cumulative = [
    alt.Tooltip('Date:T', title='Date'),
    alt.Tooltip('Cumulative Total AXS:Q', title='Cumulative Total AXS', format=",.2f"),
    alt.Tooltip('axs_ascending:Q', title='Daily Ascension', format=",.2f"),
    alt.Tooltip('axs_breeding:Q', title='Daily Breeding', format=",.2f"),
    alt.Tooltip('axs_partsEvol:Q', title='Daily Parts Evolution', format=",.2f"),
    alt.Tooltip('axs_r&cMint:Q', title='Daily R&C Mint', format=",.2f"),
    alt.Tooltip('axs_atia:Q', title='Daily Altar Restore', format=",.2f")  # Add Atia tooltip
]

tooltip_daily = [
    alt.Tooltip('Date:T', title='Date'),
    alt.Tooltip('Daily AXS:Q', title='Total Daily AXS', format=",.2f"),
    alt.Tooltip('axs_ascending:Q', title='Daily Ascension', format=",.2f"),
    alt.Tooltip('axs_breeding:Q', title='Daily Breeding', format=",.2f"),
    alt.Tooltip('axs_partsEvol:Q', title='Daily Parts Evolution', format=",.2f"),
    alt.Tooltip('axs_r&cMint:Q', title='Daily R&C Mint', format=",.2f"),
    alt.Tooltip('axs_atia:Q', title='Daily Altar Restore', format=",.2f")  # Add Atia tooltip
]

# Define tooltip for the Breeding chart
tooltip_breeding = [
    alt.Tooltip('Date:T', title='Date'),
    alt.Tooltip('AXS:Q', title='Daily Breeding AXS', format=",.2f")
]

# Define tooltip for the R&C Mint chart
tooltip_rc_mint = [
    alt.Tooltip('Date:T', title='Date'),
    alt.Tooltip('AXS:Q', title='Daily R&C Mint AXS', format=",.2f")
]

tooltip_parts_evol = [
    alt.Tooltip('Date:T', title='Date'),
    alt.Tooltip('AXS:Q', title='Daily Parts Evolution AXS', format=",.2f")
]

tooltip_ascension = [
    alt.Tooltip('Date:T', title='Date'),
    alt.Tooltip('AXS:Q', title='Daily Ascension AXS', format=",.2f")
]

# Filter data based on selected date range for both cumulative and daily data
filtered_cumulative_df = cumulative_df[(cumulative_df['Date'].dt.date >= start_date) & (cumulative_df['Date'].dt.date <= end_date)]
filtered_daily_df = daily_df[(daily_df['Date'].dt.date >= start_date) & (daily_df['Date'].dt.date <= end_date)]

# Calculate accumulated sums for each inflow type using the filter
accumulated_ascension = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['axs_ascending'].sum()
accumulated_breeding = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['axs_breeding'].sum()
accumulated_parts_evol = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['axs_partsEvol'].sum()
accumulated_rc_mint = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['axs_r&cMint'].sum()
accumulated_atia = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['axs_atia'].sum()
accumulated_total_axs = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]['Daily AXS'].sum()

# Chart 1: Daily Sum of AXS Values
# Calculate the average for Daily AXS values
daily_axs_average = filtered_daily_df['Daily AXS'].mean()

# Create the chart for Daily AXS values
chart_daily_axs = alt.Chart(filtered_daily_df).mark_bar().encode(
    x='Date:T',
    y=alt.Y('AXS:Q', title='Daily AXS'),
    color=alt.Color('Category:N', scale=alt.Scale(domain=[
        'Altar Restore', 'Ascension', 'Breeding', 'Parts Evolution', 'R&C Mint'],
        range=['#8c7bf4', '#80c6fb', '#0068c8', '#ffabab', '#ff2b2b'])),
    tooltip=tooltip_daily
).properties(
    title='Daily AXS Values by Category'
).interactive()

# Average Line for Daily AXS values
average_line_daily_axs = alt.Chart(filtered_daily_df).mark_rule(color='red', strokeDash=[4,2]).encode(
    y=alt.Y('mean(Daily AXS):Q', title='Average AXS'),
    size=alt.value(2),
    tooltip=[alt.Tooltip('mean(Daily AXS):Q', title='Average Daily AXS', format=",.2f")]
).transform_window(
    mean='mean(Daily AXS)',
    frame=[None, None]
)

# Combine the charts
chart_daily_axs_with_average = chart_daily_axs + average_line_daily_axs

st.altair_chart(chart_daily_axs_with_average, use_container_width=True)

# Chart 2: Cumulative Sum of AXS Values (Filtered)
chart_cumulative = alt.Chart(filtered_cumulative_df).mark_bar().encode(
    x='Date:T',
    y=alt.Y('AXS:Q', title='Cumulative AXS'),
    color=alt.Color('Category:N', scale=alt.Scale(domain=[
        'Altar Restore', 'Ascension', 'Breeding', 'Parts Evolution', 'R&C Mint'],
        range=['#8c7bf4', '#80c6fb', '#0068c8', '#ffabab', '#ff2b2b'])),
    tooltip=tooltip_cumulative
).properties(
    title='Cumulative Sum of AXS Values'
).interactive()

st.altair_chart(chart_cumulative, use_container_width=True)

# Chart 3: Daily Breeding Values (Line Chart with Median Line)
# Filter data based on selected date range and non-zero AXS values
filtered_breeding_df = breeding_df[(breeding_df['Date'].dt.date >= start_date) & (breeding_df['Date'].dt.date <= end_date) & (breeding_df['AXS'] > 0)]

# Check if there are any records for Breeding after filtering
if not filtered_breeding_df.empty:
    # Calculate the average for Breeding based on the filtered data
    breeding_mean = filtered_breeding_df['AXS'].mean()

    # Line Chart for Daily Breeding Values
    chart_breeding = alt.Chart(filtered_breeding_df).mark_line().encode(
        x='Date:T',
        y=alt.Y('AXS:Q', title='Daily Breeding AXS'),
        tooltip=tooltip_breeding
    ).properties(
        title='Daily Breeding AXS Values'
    ).interactive()

    # Average Line with two decimal places in the tooltip
    mean_line = alt.Chart(filtered_breeding_df).mark_rule(color='blue', strokeDash=[4,2]).encode(
        y=alt.Y('mean(AXS):Q', title='Average AXS'),
        size=alt.value(2),
        tooltip=[alt.Tooltip('mean(AXS):Q', title='Average AXS', format='.2f')]
    ).transform_window(
        mean='mean(AXS)',
        frame=[None, None]
    )

    # Combine the charts
    chart_breeding_with_mean = chart_breeding + mean_line

    # Display the combined chart for Breeding
    st.altair_chart(chart_breeding_with_mean, use_container_width=True)
else:
    st.write("No data available for Breeding in the selected date range.")



# Chart 4: Daily R&C Mint Values (Line Chart with Median Line)
# Filter data based on selected date range and non-zero AXS values
filtered_rc_mint_df = rc_mint_df[(rc_mint_df['Date'].dt.date >= start_date) & (rc_mint_df['Date'].dt.date <= end_date) & (rc_mint_df['AXS'] > 0)]

# Check if there are any records for R&C Mint after filtering
if not filtered_rc_mint_df.empty:
    # Calculate the average for R&C Mint based on the filtered data
    rc_mint_avg = filtered_rc_mint_df['AXS'].mean()

    # Create the chart for R&C Mint, starting when there are non-zero records
    chart_rc_mint = alt.Chart(filtered_rc_mint_df).mark_line().encode(
        x='Date:T',
        y=alt.Y('AXS:Q', title='Daily R&C Mint AXS'),
        tooltip=tooltip_rc_mint
    ).properties(
        title='Daily R&C Mint AXS Values'
    ).interactive()

    # Average Line for R&C Mint
    average_line_rc_mint = alt.Chart(filtered_rc_mint_df).mark_rule(color='blue', strokeDash=[4,2]).encode(
        y=alt.Y('mean(AXS):Q', title='Average AXS'),
        size=alt.value(2),
        tooltip=[alt.Tooltip('mean(AXS):Q', title='Average AXS', format=",.2f")]
    ).transform_window(
        mean='mean(AXS)',
        frame=[None, None]
    )

    # Combine the charts
    chart_rc_mint_with_average = chart_rc_mint + average_line_rc_mint

    # Display the combined chart for R&C Mint
    st.altair_chart(chart_rc_mint_with_average, use_container_width=True)
else:
    st.write("No data available for R&C Mint in the selected date range.")


# Chart 5: Daily Parts Evolution Values (Line Chart with Median Line)
# Filter data based on selected date range and non-zero AXS values
filtered_parts_evol_df = parts_evol_df[(parts_evol_df['Date'].dt.date >= start_date) & (parts_evol_df['Date'].dt.date <= end_date) & (parts_evol_df['AXS'] > 0)]

# Check if there are any records for Parts Evolution after filtering
if not filtered_parts_evol_df.empty:
    # Calculate the average for Parts Evolution based on the filtered data
    parts_evol_average = filtered_parts_evol_df['AXS'].mean()

    # Create the chart for Parts Evolution, starting when there are non-zero records
    chart_parts_evol = alt.Chart(filtered_parts_evol_df).mark_line().encode(
        x='Date:T',
        y=alt.Y('AXS:Q', title='Daily Parts Evolution AXS'),
        tooltip=tooltip_parts_evol
    ).properties(
        title='Daily Parts Evolution AXS Values'
    ).interactive()

    # Average Line for Parts Evolution
    average_line_parts_evol = alt.Chart(filtered_parts_evol_df).mark_rule(color='green', strokeDash=[4,2]).encode(
        y=alt.Y('mean(AXS):Q', title='Average AXS'),
        size=alt.value(2),
        tooltip=[alt.Tooltip('mean(AXS):Q', title='Average AXS', format=",.2f")]
    ).transform_window(
        mean='mean(AXS)',
        frame=[None, None]
    )

    # Combine the charts
    chart_parts_evol_with_average = chart_parts_evol + average_line_parts_evol

    # Display the combined chart for Parts Evolution
    st.altair_chart(chart_parts_evol_with_average, use_container_width=True)
else:
    st.write("No data available for Parts Evolution in the selected date range.")


# Chart 6: Daily Ascension Values (Line Chart)
# Filter data based on selected date range and non-zero AXS values
filtered_ascension_df = ascension_df[(ascension_df['Date'].dt.date >= start_date) & (ascension_df['Date'].dt.date <= end_date) & (ascension_df['AXS'] > 0)]

# Check if there are any records for Ascension after filtering
if not filtered_ascension_df.empty:
    # Calculate the average for Ascension based on the filtered data
    ascension_average = filtered_ascension_df['AXS'].mean()

    # Create the chart for Ascension, starting when there are non-zero records
    chart_ascension = alt.Chart(filtered_ascension_df).mark_line().encode(
        x='Date:T',
        y=alt.Y('AXS:Q', title='Daily Ascension AXS'),
        tooltip=tooltip_ascension
    ).properties(
        title='Daily Ascension AXS Values'
    ).interactive()

    # Average Line for Ascension
    average_line_ascension = alt.Chart(filtered_ascension_df).mark_rule(color='orange', strokeDash=[4,2]).encode(
        y=alt.Y('mean(AXS):Q', title='Average AXS'),
        size=alt.value(2),
        tooltip=[alt.Tooltip('mean(AXS):Q', title='Average AXS', format=",.2f")]
    ).transform_window(
        mean='mean(AXS)',
        frame=[None, None]
    )

    # Combine the charts
    chart_ascension_with_average = chart_ascension + average_line_ascension

    # Display the combined chart for Ascension
    st.altair_chart(chart_ascension_with_average, use_container_width=True)
else:
    st.write("No data available for Ascension in the selected date range.")


# Filter data to include only rows where 'Altar Restore' has non-zero values
filtered_altar_restore_df = daily_df[(daily_df['Category'] == 'Altar Restore') & (daily_df['AXS'] > 0)]

# Filter data based on selected date range
filtered_daily_df = daily_df[(daily_df['Date'].dt.date >= start_date) & (daily_df['Date'].dt.date <= end_date)]

# Filter data for Altar Restore, excluding zero or NaN values
filtered_altar_restore_df = filtered_daily_df[(filtered_daily_df['Category'] == 'Altar Restore') & (filtered_daily_df['AXS'] > 0)]

# Check if there are any records for Altar Restore after filtering
if not filtered_altar_restore_df.empty:
    # Chart 7: Daily Altar Restore Values (Line Chart)
    # Calculate the average for Altar Restore based on the filtered data
    altar_restore_average = filtered_altar_restore_df['AXS'].mean()

    # Create the chart for Altar Restore, starting when there are non-zero records
    chart_altar_restore = alt.Chart(filtered_altar_restore_df).mark_line().encode(
        x='Date:T',
        y=alt.Y('AXS:Q', title='Daily Altar Restore AXS'),
        tooltip=[
            alt.Tooltip('Date:T', title='Date'),
            alt.Tooltip('AXS:Q', title='Daily Altar Restore AXS', format=",.2f")
        ]
    ).properties(
        title='Daily Altar Restore AXS Values'
    ).interactive()

    # Average Line for Altar Restore
    average_line_altar_restore = alt.Chart(filtered_altar_restore_df).mark_rule(color='purple', strokeDash=[4, 2]).encode(
        y=alt.Y('mean(AXS):Q', title='Average AXS'),
        size=alt.value(2),
        tooltip=[alt.Tooltip('mean(AXS):Q', title='Average AXS', format=",.2f")]
    ).transform_window(
        mean='mean(AXS)',
        frame=[None, None]
    )

    # Combine the charts
    chart_altar_restore_with_average = chart_altar_restore + average_line_altar_restore

    # Display the combined chart for Altar Restore
    st.altair_chart(chart_altar_restore_with_average, use_container_width=True)
else:
    st.write("No data available for Altar Restore in the selected date range.")







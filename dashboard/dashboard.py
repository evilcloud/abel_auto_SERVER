import streamlit as st
import requests
import pandas as pd
import json
import humanize
import time
from datetime import datetime, timedelta
from collections import Counter


# Function to convert time intervals to hours
def interval_to_hours(interval):
    if interval.endswith('h'):
        return int(interval[:-1])
    elif interval.endswith('d'):
        return int(interval[:-1]) * 24
    elif interval.endswith('w'):
        return int(interval[:-1]) * 24 * 7
    elif interval.endswith('m'):
        return int(interval[:-1]) * 24 * 30
    else:  # 'all'
        return None


# Load the configuration file
with open('/app/data/config.json') as config_file:
    config = json.load(config_file)

# Fetch the data from the API
api_url = config["api_url"]
response = requests.get(api_url)

# Load data into DataFrame
if response.status_code == 200:
    # Load Rig data
    data = response.json()
    # Fetch balance data from the API
    balance_api_url = api_url.replace('/api/report', '/api/balance')
    balance_response = requests.get(balance_api_url)
    if balance_response.status_code == 200:
        balance_data = balance_response.json()
        balance = balance_data['balance']
    else:
        balance = None  # or some default value

    if not data and balance is None:
        # Display a message if no data
        st.error("No API data available.")
        st.stop()
    else:
        # Columns according to the API response
        columns = ["id", "name", "gpus", "hashrate_mh", "power_w", "created_at"]
        df = pd.DataFrame(data, columns=columns)
        df["created_at"] = pd.to_datetime(df["created_at"])  # Convert to datetime object
else:
    st.error("Failed to fetch data from the API")
    st.stop()


# Function to format time delta
def format_time_delta(delta):
    total_seconds = int(delta.total_seconds())
    return humanize.naturaldelta(total_seconds)


# # Display total hashrate, total power, total active rigs, and balance in four columns
# header1, header2, header3, header4 = st.columns(4)
# header1.title("Hashrate")
# header2.title("Power")
# header3.title("Rigs")
# header4.title("Balance")



# Select boxes for time_range and time_interval
time_controls = st.columns(2)
time_range = time_controls[0].selectbox(
    "Rig Statistics Range",
    config["dashboard_settings"]["data_intervals"],
    index=config["dashboard_settings"]["data_intervals"].index(config.get("prev_time_range", "1h"))
)

time_interval = time_controls[1].selectbox(
    "Historic Data Interval",
    config["dashboard_settings"]["data_intervals"],
    index=config["dashboard_settings"]["data_intervals"].index(config.get("prev_time_interval", "1h"))
)

# Convert time intervals to hours for further calculations
time_range_hours = interval_to_hours(time_range)
time_interval_hours = interval_to_hours(time_interval)

# Calculate total hashrate and total power from the latest reading of each rig within the selected time range
cutoff_time = datetime.now() if time_range == 'all' else datetime.now() - timedelta(hours=time_range_hours)
latest_readings = df[df["created_at"] > cutoff_time].groupby('name').last()
total_hashrate = latest_readings["hashrate_mh"].sum()
total_power = latest_readings["power_w"].sum()
total_rigs = latest_readings.shape[0]
st_balance = "∅" if balance is None else f"{format(int(balance), ',')}"


headers = {
    "Hashrate": total_hashrate,
    "Power": total_power,
    "Balance": st_balance
}

# Display total hashrate, total power, total active rigs, and balance in four columns
# header1, header2, header3, header4 = st.columns(3)
header1, header2, header4 = st.columns(3)
header1.title("Hashrate")
header2.title("Power")
# header3.title("Rigs")
header4.title("Balance")


# Update total hashrate, total power, total active rigs, and balance values
header1.header(f"{format(int(total_hashrate), ',')} MH")
header2.header(f"{format(int(total_power), ',')} W")
# header3.header(f"{total_rigs} ({time_range})")
header4.header(f"{st_balance} ABEL")

# Check if balance is None before converting to integer
# if balance is not None:
#     str_balance = f"{format(int(balance), ',')} ABEL"
# else:
#     str_balance = "N/A"


# header1, header2, header3, header4 = st.columns(4)
# header1.metric(label="Hashrate", value=f"{format(int(total_hashrate))} MH")
# header2.metric(label="Power", value=f"{format(int(total_power))} Watt")
# header3.metric(label="Rigs", value=f"{total_rigs} {time_range}")
# header4.metric(label="Balance", value=f"{str_balance} ABEL")


# Save selected time range and interval back to config
config["prev_time_range"] = time_range
config["prev_time_interval"] = time_interval

with open('/app/data/config.json', 'w') as config_file:
    json.dump(config, config_file)

# Calculate historic hashrate and power consumption
# Group by the selected time interval for finer granularity
if time_interval != 'all':
    df["group_time"] = df["created_at"].dt.floor(f"{time_interval_hours}H")
    historic_hashrate = df.groupby("group_time")["hashrate_mh"].sum()
    historic_power = df.groupby("group_time")["power_w"].sum()
else:
    historic_hashrate = df.groupby("created_at")["hashrate_mh"].sum()
    historic_power = df.groupby("created_at")["power_w"].sum()

# Combine historic hashrate and power consumption into a single DataFrame
historic_data = pd.DataFrame({
    "hashrate_mh": historic_hashrate,
    "power_w": historic_power
})

st.markdown("---")

# Plot line charts for historic hashrate and power consumption in a single chart
st.subheader("Historic Hashrate and Power Consumption")
st.line_chart(historic_data, use_container_width=True, height=200)

if not df.empty:
    # Group by server_name to get rig data and calculate last update time
    rigs = df.groupby("name").agg({
        "hashrate_mh": "last",
        "power_w": "last",
        "created_at": "max"
    })

    rigs["last_update"] = (datetime.now() - rigs["created_at"]).apply(format_time_delta)

    # Display rig data in a table
    st.subheader("Rigs Overview")
    rigs["hashrate_mh"] = rigs["hashrate_mh"].astype(int)
    rigs["power_w"] = rigs["power_w"].astype(int)
    st.table(rigs[["hashrate_mh", "power_w", "last_update"]])
else:
    st.subheader("No rigs data available.")

st.markdown("---")
# ...

# Display GPU information for each unique rig
st.subheader("Rigs GPU Information")

unique_rigs = sorted(df["name"].unique())  # Sorted list of unique rig names

# Create a set of columns
columns = st.columns(3)

for i, rig in enumerate(unique_rigs):
    # Get the column for the current rig
    column = columns[i % 3]

    with column:
        # Filter data for the current rig
        rig_data = df[df["name"] == rig]

        # Count the occurrences of each GPU
        gpu_counts = {}
        for gpus_str in rig_data["gpus"]:
            try:
                # Convert the JSON string representation of the list into an actual list
                gpus_list = json.loads(gpus_str)
                gpu_counts = Counter(gpus_list)  # use Counter to get the counts
            except Exception as e:
                print(f"Error: {str(e)}, gpus_str: {gpus_str}")

        # Convert GPU counts into a DataFrame
        gpu_counts_df = pd.DataFrame(gpu_counts.items(), columns=["GPUs", "Count"])

        # Set the GPUs column as the index to remove ordinal numbers
        gpu_counts_df = gpu_counts_df.set_index("GPUs")

        # Display the rig name and the GPU counts DataFrame
        column.markdown(f"### Rig {rig}")
        column.table(gpu_counts_df)
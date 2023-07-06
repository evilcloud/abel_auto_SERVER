import streamlit as st
import requests
import pandas as pd
import json
import humanize
from datetime import datetime, timedelta
import ast


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

# Function to format time delta
def format_time_delta(delta):
    total_seconds = int(delta.total_seconds())
    return humanize.naturaldelta(total_seconds)

# Load data into DataFrame
if response.status_code == 200:
    data = response.json()
    # Columns according to the API response
    columns = ["id", "name", "gpus", "hashrate_mh", "power_w", "created_at"]
    df = pd.DataFrame(data, columns=columns)
    df["created_at"] = pd.to_datetime(df["created_at"])  # Convert to datetime object
else:
    st.error("Failed to fetch data from the API")
    df = pd.DataFrame()

# Get previous state or use default from config.json
prev_time_interval = config.get("prev_time_interval", config["dashboard_settings"]["data_intervals"][0])
prev_time_range = config.get("prev_time_range", "1h")

# Slider for time_interval
time_interval = st.selectbox(
    "Historic Data Interval",
    config["dashboard_settings"]["data_intervals"],
    index=config["dashboard_settings"]["data_intervals"].index(prev_time_interval)
)

# Slider for time_range
time_range = st.selectbox(
    "Rig Statistics Range",
    config["dashboard_settings"]["data_intervals"],
    index=config["dashboard_settings"]["data_intervals"].index(prev_time_range)
)

# Convert time intervals to hours for further calculations
time_interval_hours = interval_to_hours(time_interval)
time_range_hours = interval_to_hours(time_range)

# Calculate total hashrate and total power from the latest reading of each rig within the selected time range
cutoff_time = datetime.now() if time_range == 'all' else datetime.now() - timedelta(hours=time_range_hours)
latest_readings = df[df["created_at"] > cutoff_time].groupby('name').last()
total_hashrate = latest_readings["hashrate_mh"].sum()
total_power = latest_readings["power_w"].sum()
total_rigs = latest_readings.shape[0]

# Display total hashrate, total power, and total active rigs in three columns
header1, header2, header3 = st.columns(3)
header1.title("Hashrate")
header1.subheader(f"{int(total_hashrate)} MH")
header2.title("Power")
header2.subheader(f"{int(total_power)} W")
header3.title(f"Rigs ({time_range})")
header3.subheader(f"{total_rigs}")

# Calculate historic hashrate and power consumption
# Group by the selected time interval for finer granularity
if time_interval != 'all':
    df["group_time"] = df["created_at"].dt.floor(f"{time_interval_hours}H")
    historic_hashrate = df.groupby("group_time")["hashrate_mh"].sum()
    historic_power = df.groupby("group_time")["power_w"].sum()
else:
    historic_hashrate = df.groupby("created_at")["hashrate_mh"].sum()
    historic_power = df.groupby("created_at")["power_w"].sum()

st.divider()


# Plot line charts for historic hashrate and power consumption side by side
st.subheader("Historic Hashrate and Power Consumption")
col1, col2 = st.columns(2)
with col1:
    st.line_chart(historic_hashrate, use_container_width=True, height=200)

with col2:
    st.line_chart(historic_power, use_container_width=True, height=200)

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


st.divider()


# Display GPU information for each unique rig
st.subheader("Rigs GPU Information")

unique_rigs = df["name"].unique()

# Create a set of columns
columns = st.columns(3)

for i, rig in enumerate(unique_rigs):
    # Get the column for the current rig
    column = columns[i % 3]

    with column:
        # Filter data for the current rig
        rig_data = df[df["name"] == rig]

        # Extract the list of GPUs for each entry, combine them ensuring uniqueness
        all_gpus = set()
        for gpus_str in rig_data["gpus"]:
            try:
                # Convert the JSON string representation of the list into an actual list
                gpus_list = json.loads(gpus_str)
                all_gpus.update(gpus_list)
            except Exception as e:
                print(f"Error: {e}, gpus_str: {gpus_str}")

        # Display the GPUs for the current rig in a table
        column.subheader(f"{rig}")
        column.table(pd.DataFrame(list(all_gpus), columns=["GPUs"]))

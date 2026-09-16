from datetime import datetime
from io import StringIO
import os
import pandas as pd
import requests
import folium
from folium.plugins import HeatMap

# 1. Configuration & Security
API_KEY = os.environ.get("NASA_API_KEY")
if not API_KEY:
  raise ValueError("No NASA_API_KEY found in environment variables.")

SOURCE = "VIIRS_SNPP"
AREA_COORDINATES = "75.7,11.4,76.5,12.0"  # Wayanad Bounding Box
DAY_RANGE = 1

url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{API_KEY}/{SOURCE}/{AREA_COORDINATES}/{DAY_RANGE}"

print("Fetching thermal anomaly data for Wayanad from NASA FIRMS...")

try:
  response = requests.get(url)
  response.raise_for_status()
  df = pd.read_csv(StringIO(response.text))

  # 2. Initialize Map over Wayanad
  wayanad_map = folium.Map(location=[11.6854, 76.1320], zoom_start=11)

  folium.TileLayer(
      tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      attr="OpenStreetMap",
      name="Street Map",
  ).add_to(wayanad_map)

  if df.empty:
    print(
        "No thermal anomalies or fire detections found in Wayanad for this"
        " timeframe."
    )
    folium.Marker(
        [11.6854, 76.1320],
        popup="<b>Status:</b> No active anomalies detected in the last 24h.",
        icon=folium.Icon(color="green", icon="info-sign"),
    ).add_to(wayanad_map)
  else:
    print(f"\n[ALERT] Success! Found {len(df)} thermal anomaly point(s).")

    # 3. Build Heat Data Array [latitude, longitude, intensity_weight]
    heat_data = []
    for idx, row in df.iterrows():
      lat = row["latitude"]
      lon = row["longitude"]
      # Use Fire Radiative Power (FRP) as intensity weight; default to 10 if missing
      weight = float(row["frp"]) if pd.notna(row["frp"]) else 10.0
      heat_data.append([lat, lon, weight])

    # Add the HeatMap layer to the folium map
    HeatMap(
        heat_data,
        radius=18,
        blur=12,
        max_zoom=13,
        gradient={0.4: "blue", 0.65: "lime", 0.9: "orange", 1.0: "red"},
    ).add_to(wayanad_map)

  # Save as index.html
  wayanad_map.save("index.html")
  print("Generated fresh thermal heat map: index.html")

except Exception as e:
  print(f"An error occurred: {e}")

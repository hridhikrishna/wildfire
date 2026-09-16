from datetime import datetime
from io import StringIO
import os
import pandas as pd
git
import requests

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

  # 2. Generate Interactive Map using Folium
  # Center map over Wayanad
  wayanad_map = folium.Map(location=[11.6854, 76.1320], zoom_start=11)

  # Add a tile layer for satellite view (optional, makes it look like a real monitoring center)
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
    # Create an empty indicator map
    folium.Marker(
        [11.6854, 76.1320],
        popup="<b>Status:</b> No active anomalies detected in the last 24h.",
        icon=folium.Icon(color="green", icon="info-sign"),
    ).add_to(wayanad_map)
  else:
    print(f"\n[ALERT] Success! Found {len(df)} thermal anomaly point(s).")
    for idx, row in df.iterrows():
      color = "red" if row.get("frp", 0) > 50 else "orange"
      popup_text = f"""
                <b>Thermal Anomaly Detected</b><br>
                <b>Confidence:</b> {str(row['confidence']).upper()}<br>
                <b>FRP (Intensity):</b> {row['frp']} MW<br>
                <b>Time (UTC):</b> {row['acq_date']} {row['acq_time']}<br>
                <b>Coordinates:</b> {row['latitude']}, {row['longitude']}
            """
      folium.CircleMarker(
          location=[row["latitude"], row["longitude"]],
          radius=9,
          popup=folium.Popup(popup_text, max_width=300),
          color=color,
          fill=True,
          fill_color=color,
          fill_opacity=0.7,
      ).add_to(wayanad_map)

  # Save the map as index.html
  wayanad_map.save("index.html")
  print("Generated fresh interactive map: index.html")

except Exception as e:
  print(f"An error occurred: {e}")

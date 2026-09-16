from io import StringIO
import os
import pandas as pd
import requests

# 1. Configuration & Security
API_KEY = os.environ.get("NASA_API_KEY")

if not API_KEY:
  raise ValueError(
      "No NASA_API_KEY found in environment variables. Please set it in your"
      " GitHub repository secrets."
  )

SOURCE = "VIIRS_SNPP"
AREA_COORDINATES = "75.7,11.4,76.5,12.0"
DAY_RANGE = 1

url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{API_KEY}/{SOURCE}/{AREA_COORDINATES}/{DAY_RANGE}"

print("Fetching thermal anomaly data for Wayanad from NASA FIRMS...")

try:
  response = requests.get(url)
  response.raise_for_status()

  df = pd.read_csv(StringIO(response.text))

  if df.empty:
    print(
        "No thermal anomalies or fire detections found in Wayanad for this"
        " timeframe."
    )
  else:
    print(
        f"\n[ALERT] Success! Found {len(df)} thermal anomaly point(s) in"
        " Wayanad."
    )

    print("\nAnomaly Details:")
    print("-" * 65)
    for idx, row in df.iterrows():
      print(f"Latitude: {row['latitude']}, Longitude: {row['longitude']}")
      print(f"  - Confidence: {str(row['confidence']).upper()}")
      print(f"  - Fire Radiative Power (FRP): {row['frp']} MW")
      print(f"  - Timestamp (UTC): {row['acq_date']} {row['acq_time']}")
      print("-" * 65)

except Exception as e:
  print(f"An error occurred: {e}")

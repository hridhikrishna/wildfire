from io import StringIO
import os
import pandas as pd
import requests

# 1. Configuration & Security
# Pulls the NASA API key securely from GitHub Actions Secrets
API_KEY = os.environ.get("NASA_API_KEY")

if not API_KEY:
  raise ValueError(
      "No NASA_API_KEY found in environment variables. Please set it in your"
      " GitHub repository secrets."
  )

# High-resolution 375m thermal sensor
SOURCE = "VIIRS_SNPP"

# 2. Define Bounding Box for Wayanad (west, south, east, north)
# Format: min_longitude, min_latitude, max_longitude, max_latitude
AREA_COORDINATES = "75.7,11.4,76.5,12.0"

# Number of days to look back (1 to 10 days)
DAY_RANGE = 1

# 3. Build the official NASA FIRMS Area API URL
url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{API_KEY}/{SOURCE}/{AREA_COORDINATES}/{DAY_RANGE}"

print(f"Fetching thermal anomaly data for Wayanad from NASA FIRMS...")

try:
  response = requests.get(url)
  response.raise_for_status()

  # Load data into a Pandas DataFrame
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

    # Optional: Save locally (will be saved inside the GitHub runner environment during the job execution)
    df.to_csv("wayanad_thermal_anomalies.csv", index=False)
    print("\nSaved data locally to 'wayanad_thermal_anomalies.csv'.")

except requests.exceptions.HTTPError as err:
  print(f"HTTP Error: {err}")
  print(
      "Double-check that your NASA_API_KEY secret is correctly set in GitHub."
  )
except Exception as e:
  print(f"An error occurred: {e}")
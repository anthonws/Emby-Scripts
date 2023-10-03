import requests
import pandas as pd
import json
import os
from fuzzywuzzy import fuzz
import base64


def search_for_files_by_fuzzy_match_case_insensitive_highest_percentage(string, path="."):

  string = string.lower()
  found_files = []
  for root, dirs, files in os.walk(path):
    for f in files:
      f_lower = f.lower()
      match_percentage = fuzz.ratio(string, f_lower)
      found_files.append((f, os.path.join(root, f), match_percentage))

  found_files.sort(key=lambda x: x[2], reverse=True)

  if found_files:
    best_file = found_files[0][1]
    print(f"Found file with the highest percentage of match: {best_file}")
    return best_file
  else:
    print(f"No files found matching the string '{string}'")
    return ""

# Global variables
EMBY_SERVER_URL = 'http://XXX.XXX.XXX.XXX:8096/emby'
API_KEY = 'YOUR_API_KEY'
path = "C:/YOUR/PATH/TO/CHANNEL/LOGOS"

# Get TV channels
response = requests.get(f'{EMBY_SERVER_URL}/LiveTv/Manage/Channels?api_key={API_KEY}')

# Check response
if response.status_code == 200:
    channels = json.loads(response.content)
else:
    raise Exception(f"Failed to get TV channels: {response.status_code}")

# Create dataframe
df = pd.DataFrame(channels['Items'])

# Iterate over rows in dataframe
for index, row in df.iterrows():
    string = (row['Name'])
    # Search for file with highest percentage of match
    best_file = search_for_files_by_fuzzy_match_case_insensitive_highest_percentage(string, path)
    if best_file:
        with open(best_file, 'rb') as f:
            logo = f.read()
            encoded_logo = base64.b64encode(logo).decode('ascii')
        response = requests.post(f'{EMBY_SERVER_URL}/Items/{row["Id"]}/Images/Primary?api_key={API_KEY}', data=encoded_logo, headers={'Content-Type': 'image/png'})
        if response.status_code == 204:
            print(f"Successfully updated channel logo for '{string}'")
        else:
            raise Exception(f"Failed to update channel logo for '{string}': {response.status_code}")
    else:
        print(f"Failed to find the file for '{string}'")

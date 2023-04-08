import os
import re
import json
import requests
from tqdm import tqdm


# Function to get the table IDs from the given HTML content
def get_table_ids(html):
    table_ids = re.findall(r"\/table\?table=(\d+)", html)
    return table_ids


# Function to save the table data into a file
def save_table_data_to_file(table_data, filename="table_data_backup.json"):
    with open(filename, "w") as f:
        json.dump(table_data, f, indent=2)


# Read the cookie and xrequest from environment variable
cookie_value = os.environ.get("BGA_COOKIE")
x_request_value = os.environ.get("BGA_XREQUEST")

if cookie_value is None or x_request_value is None:
    print("BGA_COOKIE and BGA_XREQUEST not set.")
    print("Look find these in the network inspector tab of a logged in browser session")
    exit()

# Set up headers with the cookie
headers = {"Cookie": cookie_value, "X-Request-Token": x_request_value}

# Initialize an empty dictionary for storing table data
table_data_dict = {}
with open("table_data_backup.json", "r") as f:
    table_data_dict = json.load(f)

unfinished = True
dirty = False
# Get the most recent games data
url1 = f"https://boardgamearena.com/message/board?type=lastresult&id=1531&social=false&per_page=300"
while unfinished:
    response1 = requests.get(url1, headers=headers)
    if response1.status_code == 200:
        games_data = response1.json()
        if len(games_data["data"]) == 0:
            unfinished = False

        # Extract table IDs from the HTML content
        table_ids = set()
        for game in games_data["data"]:
            table_ids.update(get_table_ids(game["html"]))
        last_id = games_data["data"][-1]["id"]
        last_time = games_data["data"][-1]["timestamp"]

        # Get the table data for each table ID
        url2 = "https://boardgamearena.com/table/table/tableinfos.html?id="
        for table_id in tqdm(table_ids):
            if table_id not in table_data_dict:
                response2 = requests.get(url2 + table_id, headers=headers)
                if response2.status_code == 200:
                    table_data = response2.json()
                    table_data_dict[table_id] = table_data
                    dirty = True
                else:
                    print(f"Error getting data for table {table_id}")

                # Save the table data to a file
    else:
        print("Error getting games data.")
        unfinished = False
    if dirty:
        save_table_data_to_file(table_data_dict)
        dirty = False
    url1 = f"https://boardgamearena.com/message/board?type=lastresult&id=1531&social=false&per_page=300&from_id={last_id}&from_time={last_time}"
    print(len(table_data_dict))

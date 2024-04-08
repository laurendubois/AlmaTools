import sys
import requests
from bs4 import BeautifulSoup

# This script writes full XML to output file for one MMS ID 

# Constants for file names
API_KEY_FILE = 'PSB.txt'
HOLDING_IDS_FILE = 'items.txt'
OUTPUT_FILE = 'items_results.txt'
ERROR_FILE = 'items_errors.txt'
BASE_URL = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/"

# Read API key from file
with open(API_KEY_FILE, 'r') as file:
    apikey = file.read().strip()

# Basic request to check connection/API key
headers = {
    "Authorization": "apikey " + apikey,
    "content-type": "application/xml",
    "Accept": "application/xml"
}
sys.stdout.write("Checking API key...")
test_api = requests.get(BASE_URL + "bibs/test", headers=headers)
if test_api.status_code == 400:
    print("\nInvalid API key - please confirm key has r/w permission for /bibs", )
    sys.exit()
elif test_api.status_code != 200:
    print(f"\nError: Failed to connect to API. Status code: {test_api.status_code}")
    sys.exit()
else:
    sys.stdout.write("OK\n")

# Read Holding IDs from file
with open(HOLDING_IDS_FILE, 'r') as file:
    holding_ids = [line.strip() for line in file]


# Function to retrieve barcodes for a given Holding ID
def get_barcodes(holding_id):
    url = f"{BASE_URL}bibs/991000010789705251/holdings/{holding_id}/items/"  # Works if MMS ID hardcoded 991000010789705251
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        item_xml = response.text
        print(item_xml)
        return item_xml
    else:
        print(f"Failed to retrieve items for holding ID: {holding_id}")
        return None


# Function to write item XML to a text file
def write_item_xml(filename, item_xml):
    with open(filename, 'a') as file:
        file.write(item_xml)


# Loop through each Holding ID and retrieve item XML
for holding_id in holding_ids:
    item_xml = get_barcodes(holding_id)
    if item_xml:
        write_item_xml(OUTPUT_FILE, item_xml)
        print(f"Item XML for Holding ID {holding_id} appended to {OUTPUT_FILE}")
    else:
        with open(ERROR_FILE, 'a') as file:
            file.write(f"Failed for Holding ID: {holding_id}\n")
        print(f"Failed: {holding_id}. Written to {ERROR_FILE}")

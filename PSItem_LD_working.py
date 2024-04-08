import sys
import requests
from bs4 import BeautifulSoup

# This script pulls certain item fields from the XML into an output file

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


# Function to item details for a given Holding ID
def get_item_details(holding_id):
    url = f"{BASE_URL}bibs/991000010789705251/holdings/{holding_id}/items/"  # Works if MMS ID hardcoded 991000010789705251
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        item_xml = response.text
        print(item_xml)
        return item_xml
    else:
        print(f"Failed to retrieve items for holding ID: {holding_id}")
        return None


# Function to extract holding details from holdings XML
def extract_item_details(xml_string):
    soup = BeautifulSoup(xml_string, 'xml')
    item_details = []
    for item in soup.find_all('item'):
        holding_num = item.find('holding_id').text.strip()
        pid = item.find('pid').text.strip()
        barcode = item.find('barcode').text.strip()
        base_status = item.find('base_status').get('desc')
        physical_material_type = item.find('physical_material_type').get('desc')
        process_type = item.find('process_type').get('desc') if item.find('process_type') else ""
        item_details.append((holding_num, pid, barcode, base_status, physical_material_type, process_type))
    return item_details


# Function to write xml details to a text file
def write_item_details(filename, item_details):
    with open(filename, 'a') as file:
        for item_detail in item_details:
            holding_num, pid, barcode, base_status, physical_material_type, process_type = item_detail
            file.write(
                f"Holding Num: {holding_num}|Item PID: {pid}|Barcode: {barcode}|Base_Status: {base_status}|"
                f"Physical_Material_Type: {physical_material_type}|Process Type: {process_type}\n")


# Loop through each Holding ID and retrieve item details
for holding_id in holding_ids:
    item_xml = get_item_details(holding_id)
    if item_xml:
        item_details = extract_item_details(item_xml)
        if item_details:
            write_item_details(OUTPUT_FILE, item_details)
            print(f"Item details for {holding_id} appended to {OUTPUT_FILE}")
        else:
            with open(ERROR_FILE, 'a') as file:
                file.write(f"No item details for: {holding_id}\n")
            print(f"No holding record for: {holding_id}. Written to {ERROR_FILE}")
    else:
        with open(ERROR_FILE, 'a') as file:
            file.write(f"Failed for Holding ID: {holding_id}\n")
        print(f"Failed: {holding_id}. Written to {ERROR_FILE}")

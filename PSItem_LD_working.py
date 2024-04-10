import sys
import requests
from bs4 import BeautifulSoup

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
    print("\nInvalid API key - please confirm key has r/w permission for /bibs")
    sys.exit()
elif test_api.status_code != 200:
    print(f"\nError: Failed to connect to API. Status code: {test_api.status_code}")
    sys.exit()
else:
    sys.stdout.write("OK\n")

# Read Holding IDs and MMS IDs from file
with open(HOLDING_IDS_FILE, 'r') as file:
    holding_mms_pairs = [line.strip().split('|') for line in file]


# Function to use API to retrieve item details for an MMS ID and holding pair
def get_item_details(mms_id, holding_id):
    url = f"{BASE_URL}bibs/{mms_id}/holdings/{holding_id}/items/"  # Updated URL
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        item_xml = response.text
        return item_xml
    else:
        print(f"Failed to retrieve items for MMS ID: {mms_id} and holding ID: {holding_id}")
        return None


# Function to extract specific fields from XML
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


# Function to write specific fields to a text file
def write_item_details(filename, item_details):
    with open(filename, 'a') as file:
        for item_detail in item_details:
            holding_num, pid, barcode, base_status, physical_material_type, process_type = item_detail
            file.write(
                f"Holding Num: {holding_num}|Item PID: {pid}|Barcode: {barcode}|Base_Status: {base_status}|"
                f"Physical_Material_Type: {physical_material_type}|Process Type: {process_type}\n")


# Loop through each MMS ID and holding pair and retrieve item details
for mms_id, holding_id in holding_mms_pairs:
    item_xml = get_item_details(mms_id.strip(), holding_id.strip())
    if item_xml:
        item_details = extract_item_details(item_xml)
        if item_details:
            write_item_details(OUTPUT_FILE, item_details)
            print(f"Item details for MMS ID: {mms_id} and holding ID: {holding_id} appended to {OUTPUT_FILE}")
        else:
            with open(ERROR_FILE, 'a') as file:
                file.write(f"No item details for MMS ID: {mms_id} and holding ID: {holding_id}\n")
            print(f"No holding record for MMS ID: {mms_id} and holding ID: {holding_id}. Written to {ERROR_FILE}")
    else:
        with open(ERROR_FILE, 'a') as file:
            file.write(f"Failed for MMS ID: {mms_id} and holding ID: {holding_id}\n")
        print(f"Failed for MMS ID: {mms_id} and holding ID: {holding_id}. Written to {ERROR_FILE}")

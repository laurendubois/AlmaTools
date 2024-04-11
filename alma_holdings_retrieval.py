import sys
import requests
from bs4 import BeautifulSoup

# Uses Alma Sandbox API to pull certain holding details [based on MMS ID] into an output file

# Constants for file names
API_KEY_FILE = 'PSB.txt'
MMS_IDS_FILE = 'bibs.txt'
OUTPUT_FILE = 'bibs_output.txt'
ERROR_FILE = 'bibs_errors.txt'
BASE_URL = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/"

# Read API key from file
with open(API_KEY_FILE, 'r') as file:
    apikey = file.read().strip()

# Check connection/API key
headers = {
    "Authorization": "apikey " + apikey,
    "content-type": "application/xml",
    "Accept": "application/xml"
}
sys.stdout.write("Checking API key...")
test_api = requests.post(BASE_URL + "bibs/test", headers=headers)
if test_api.status_code == 400:
    print("\nInvalid API key - please confirm key has r/w permission for /bibs", )
    sys.exit()
elif test_api.status_code != 200:
    print(f"\nError: Failed to connect to API. Status code: Unknown")
    sys.exit()
else:
    sys.stdout.write("OK\n")

# Read MMS IDs from file
with open(MMS_IDS_FILE, 'r') as file:
    mms_ids = [line.strip() for line in file]


def get_holdings(mms_id):
    """Retrieves holding XML based on MMS ID"""
    url = f"{BASE_URL}bibs/{mms_id}/holdings"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        holdings_xml = response.text
        return holdings_xml
    else:
        print(f"Failed to retrieve holdings for MMS ID: {mms_id}")
        return None


def extract_holding_details(xml_string):
    """Extracts specific fields from the holding XML"""
    soup = BeautifulSoup(xml_string, 'xml')
    holding_details = []
    for holding in soup.find_all('holding'):
        holding_id = holding.find('holding_id').text.strip()
        suppress = holding.find('suppress_from_publishing').text.strip()
        call_number = holding.find('call_number').text.strip() if holding.find('call_number') else ""
        library = holding.find('library').get('desc') if holding.find('library') else ""
        location = holding.find('location').get('desc') if holding.find('location') else ""
        holding_details.append((holding_id, suppress, call_number, library, location))
    return holding_details


def write_mms_and_holding_details(filename, mms_id, holding_details):
    """Writes the extracted field details to a txt"""
    with open(filename, 'a') as file:  # Use 'a' mode to append each line to file
        for holding_detail in holding_details:
            holding_id, suppress, call_number, library, location = holding_detail
            file.write(
                f"MMSID: {mms_id}|HoldingID: {holding_id}|Suppress: {suppress}|Call: {call_number}|Library: {library}|"
                f"Location: {location}\n")


# Then loop through all the MMS IDs listed and write to the same txt
for mms_id in mms_ids:
    holdings_xml = get_holdings(mms_id)
    if holdings_xml:
        holding_details = extract_holding_details(holdings_xml)
        if holding_details:
            write_mms_and_holding_details(OUTPUT_FILE, mms_id, holding_details)
            print(f"Holding details for MMS ID {mms_id} appended to {OUTPUT_FILE}")
        else:
            with open(ERROR_FILE, 'a') as file:
                file.write(f"No holding record found for MMS ID: {mms_id}\n")
            print(f"No holding record found for MMS ID {mms_id}. Written to {ERROR_FILE}")
    else:
        with open(ERROR_FILE, 'a') as file:
            file.write(f"Failed to retrieve holdings for MMS ID: {mms_id}\n")
        print(f"Failed to retrieve holdings for MMS ID:{mms_id}. Written to {ERROR_FILE}")

import sys
import requests
from bs4 import BeautifulSoup

# Constants for file names
api_key_file = 'PSB.txt'
mms_ids_file = 'bibs.txt'
output_file = 'holding_results.txt'
error_file = 'holding_errors.txt'
base_url = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/"

# Read API key from file
with open(api_key_file, 'r') as file:
    apikey = file.read().strip()

# Basic request to check connection/API key
headers = {
    "Authorization": "apikey " + apikey,
    "content-type": "application/xml",
    "Accept": "application/xml"
}
sys.stdout.write("Checking API key...")
test_api = requests.post(base_url + "bibs/test", headers=headers)
if test_api.status_code == 400:
    print("\nInvalid API key - please confirm key has r/w permission for /bibs", )
    sys.exit()
elif test_api.status_code != 200:
    print(f"\nError: Failed to connect to API. Status code: {testapi.status_code}")
    sys.exit()
else:
    sys.stdout.write("OK\n")

# Read MMS IDs from file
with open(mms_ids_file, 'r') as file:
    mms_ids = [line.strip() for line in file]

# Function to retrieve holdings for a given MMS ID
def get_holdings(mms_id):
    url = f"{base_url}bibs/{mms_id}/holdings"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        holdings_xml = response.text
        return holdings_xml
    else:
        print(f"Failed to retrieve holdings for MMS ID: {mms_id}")
        return None

# Function to extract holding details from holdings XML
def extract_holding_details(xml_string):
    soup = BeautifulSoup(xml_string, 'xml')
    holding_details = []
    for holding in soup.find_all('holding'):
        holding_id = holding.find('holding_id').text.strip()
        suppress = holding.find('suppress_from_publishing').text.strip()
        library = holding.find('library').get('desc') if holding.find('library') else ""
        location = holding.find('location').get('desc') if holding.find('location') else ""
        holding_details.append((holding_id, suppress, library, location))
    return holding_details

# Function to write MMS ID and holding details to a text file
def write_mms_and_holding_details(filename, mms_id, holding_details):
    with open(filename, 'a') as file:  # Use 'a' mode to append each line to file
        for holding_detail in holding_details:
            holding_id, suppress, library, location = holding_detail
            file.write(f"MMS ID: {mms_id}, Holding ID: {holding_id}, Suppress From Publishing: {suppress}, Library: {library}, Location: {location}\n")

# Loop through each MMS ID and retrieve holding details
for mms_id in mms_ids:
    holdings_xml = get_holdings(mms_id)
    if holdings_xml:
        holding_details = extract_holding_details(holdings_xml)
        if holding_details:
            write_mms_and_holding_details(output_file, mms_id, holding_details)
            print(f"Holding details for MMS ID {mms_id} appended to {output_file}")
        else:
            with open(error_file, 'a') as file:
                file.write(f"No holding record for MMS ID: {mms_id}\n")
            print(f"No holding record for MMS ID {mms_id}. Written to {error_file}")
    else:
        with open(error_file, 'a') as file:
            file.write(f"Failed to retrieve holdings for MMS ID: {mms_id}\n")
        print(f"Failed MMS ID: {mms_id}. Written to {error_file}")

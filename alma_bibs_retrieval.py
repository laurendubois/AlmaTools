import sys
import requests
from bs4 import BeautifulSoup

# This will get certain XML fields to determine if electronic resource bib or not 

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
    print(f'\nError: Failed to connect to API. Status code: {test_api.status_code}')
    sys.exit()
else:
    sys.stdout.write("OK\n")

# Read MMS IDs from file
with open(MMS_IDS_FILE, 'r') as file:
    mms_ids = [line.strip() for line in file]


def get_bib_details(mms_id):
    """Retrieves XML based on MMS ID"""
    url = f"{BASE_URL}bibs/{mms_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve bib details for MMS ID: {mms_id}")
        return None


# Open the output file in append mode
with open(OUTPUT_FILE, 'a', encoding='utf-8') as output_file:
    # Then loop through all the MMS IDs listed and write to the same txt
    for mms_id in mms_ids:
        bib_xml = get_bib_details(mms_id)
        if bib_xml:
            soup = BeautifulSoup(bib_xml, 'xml')

            # Extracting the required fields
            mms_id = soup.find('mms_id').text
            holdings_link = soup.find('holdings').get('link') if soup.find('holdings') else None
            leader = soup.find('leader').text
            controlfield_006 = soup.find('controlfield', {'tag': '006'}).text[0] if soup.find('controlfield',
                                                                                              {'tag': '006'}) else None
            network_number = soup.find('network_numbers').find('network_number').text
            datafield_856 = soup.find('datafield', {'tag': '856'}).text if soup.find('datafield',
                                                                                     {'tag': '856'}) else None
            suppress_from_publishing = soup.find('suppress_from_publishing').text
            suppress_from_external_search = soup.find('suppress_from_external_search').text

            # Writing the extracted fields to the output file with labels
            output_file.write(
                f"MMS ID: {mms_id}|Holdings Link: {holdings_link if holdings_link else ''}|Leader: {leader}|Controlfield 006: {controlfield_006 if controlfield_006 else ''}|Network Number: {network_number}|Datafield 856: {datafield_856}|Suppressed From Publishing: {suppress_from_publishing}|Suppressed From External Search: {suppress_from_external_search}\n")

            print(f"Details for MMS ID {mms_id} appended to {OUTPUT_FILE}")
        else:
            with open(ERROR_FILE, 'a') as file:
                file.write(f"Failed to retrieve XML record for MMS ID: {mms_id}\n")
            print(f"Failed to retrieve XML record for MMS ID {mms_id}. Written to {ERROR_FILE}")

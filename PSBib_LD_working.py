import requests
from bs4 import BeautifulSoup

# Read API key from file
with open('PSB.txt', 'r') as file:
    key = file.read().strip()

# Base URL and headers
base_url = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/"
headers = {
    "Authorization": "apikey " + key,
    "content-type": "application/xml",
    "Accept": "application/xml"
}

# Read MMS IDs from file
with open('bibs.txt', 'r') as file:
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
    with open(filename, 'a') as file:  # Use 'a' mode to append to the file instead of overwriting
        for holding_detail in holding_details:
            holding_id, suppress, library, location = holding_detail
            file.write(f"MMS ID: {mms_id}, Holding ID: {holding_id}, Suppress From Publishing: {suppress}, Library: {library}, Location: {location}\n")

# Output filenames
output_filename = 'holdingresults.txt'
not_found_filename = 'holdingsresultsnotfound.txt'

# Loop through each MMS ID and retrieve holdings
for mms_id in mms_ids:
    holdings_xml = get_holdings(mms_id)
    if holdings_xml:
        holding_details = extract_holding_details(holdings_xml)
        if holding_details:
            write_mms_and_holding_details(output_filename, mms_id, holding_details)
            print(f"Holding details for MMS ID {mms_id} appended to {output_filename}")
        else:
            with open(not_found_filename, 'a') as file:
                file.write(f"{mms_id}\n")
            print(f"No holding details found for MMS ID {mms_id}. Information written to {not_found_filename}")
    else:
        with open(not_found_filename, 'a') as file:
            file.write(f"Failed to retrieve holdings for MMS ID: {mms_id}\n")
        print(f"Failed to retrieve holdings for MMS ID: {mms_id}. Information written to {not_found_filename}")

import requests
from bs4 import BeautifulSoup

# This script prints holding XML to terminal

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

# Function to prettify XML using BeautifulSoup
def prettify_xml(xml_string):
    soup = BeautifulSoup(xml_string, features="xml")
    return soup.prettify()

# Loop through each MMS ID and retrieve holdings
for mms_id in mms_ids:
    holdings_xml = get_holdings(mms_id)
    if holdings_xml:
        # Process the holdings XML as needed
        pretty_xml = prettify_xml(holdings_xml)
        print(pretty_xml)

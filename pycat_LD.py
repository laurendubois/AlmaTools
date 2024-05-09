import os
import json
import pandas as pd
from io import BytesIO
from pymarc import XmlHandler, parse_xml
import requests

# Define Alma API key and base url
api_key = "YOUR_API_KEY"
base_url = "https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs"

# Input and output directories
input_directory = r"C:\Users\lmd8\PycharmProjects\OCLCTools\MissingHoldings"
output_directory = r"C:\Users\lmd8\PycharmProjects\OCLCTools\MissingHoldings_output"

# Load the Excel file
excel_file_path = os.path.join(input_directory, "MissingHoldings.xlsx")
df = pd.read_excel(excel_file_path)

# Extract MMSIDs from the specified column
column_name = "MMSID"  # Update with the column name containing MMSIDs
mms_ids = df[column_name].tolist()

# Loop through each MMSID and fetch the corresponding Bib record
for index, mms_id in enumerate(mms_ids):
    # Construct the query parameters
    params = {
        "mms_id": mms_id,
        "apikey": api_key,
        "expand": "p_avail"  # Optionally, you can expand inventory information
    }

    # Make the request to Alma API
    response = requests.get(base_url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the XML response
        def parse_xml_record(data):
            handler = XmlHandler()
            parse_xml(data, handler)
            return handler.records[0]

        # Write the Bib record to a separate file
        output_file_path = os.path.join(output_directory, f"bib_record_{index}.json")
        with open(output_file_path, "w") as file:
            json.dump(parse_xml_record(BytesIO(response.content)).as_dict(), file, indent=4)
    else:
        print(f"Error: {response.status_code} - {response.text}")

print("Complete. Check output files.")

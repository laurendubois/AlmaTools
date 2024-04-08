import sys
import requests
import pandas as pd

with open('PSB.txt', 'r') as file:
    key = file.read()

# Establishes URL, Key, df
biburl = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/"
apikey = key

df = pd.read_csv("BibFix.csv", dtype=str)
print(df)
print(len(df))

# Check API key
headers = {
    "Authorization": "apikey " + apikey,
    "content-type": "application/json",
    "Accept": "application/json"}
sys.stdout.write("Checking API key...")
testapi = requests.post(biburl + "test", headers=headers)
if testapi.status_code == 400:
    print("\nInvalid API key - please confirm key has r/w permission for /bibs", )
    sys.exit()
elif testapi.status_code != 200:
    sys.stdout.write("Error\n")
    sys.exit()
else:
    sys.stdout.write("OK\n")

# Reads to Bib level
for i in range(0, len(df)):
    url = biburl + str(df.iloc[i]['MMS'])
    print(url)
    xml = requests.get(url, headers=headers)
    r = xml.text
    modified = r.replace('<subfield code=\"a\">'+df.iloc[i]['OLD Call']+'</subfield>',
                         '<subfield code=\"a\">'+df.iloc[i]['FIX Call A']+'</subfield><subfield code\"b\">'+df.iloc[i]['FIX Call B']+'</subfield>')
    print(modified)
#    rewrite = requests.put(url, headers=headers, data=modified)

# Reads to Holding level
# for i in range(0, len(df)):
#     url = biburl + str(df.iloc[i]['MMSId']) + "/holdings/" + str(df.iloc[i]['HId'])
#     print(url)
#     xml = requests.get(url, headers=headers)
#     r = xml.text
#     print(xml)

# Reads to Item level
# for i in range(0, len(df)):
#     url = biburl + str(df.iloc[i]['MMSId']) + "/holdings/" + str(df.iloc[i]['HId']) + "/items/" + str(df.iloc[i]['PId'])
#     print(url)
#     xml = requests.get(url, headers=headers)
#     r = xml.text
#     print(xml)

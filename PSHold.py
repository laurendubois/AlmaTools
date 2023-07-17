import sys
import requests
from bs4 import BeautifulSoup as bs
import re

# API key as variable
with open('PSB.txt', 'r') as file:
    key = file.read()

# Establishes URL, Key, Bib/Holding dict
biburl = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/"
apikey = key
biblist = [bib for bib in open('bibs.txt', 'r')]
biblist = [bib.strip() for bib in biblist]
holdinglist = [holding for holding in open('holdings.txt', 'r')]
holdinglist = [holding.strip() for holding in holdinglist]
getdict = dict(zip(biblist, holdinglist)).items()
print(getdict)

# Check API key
headers = {
    "Authorization": "apikey " + apikey,
    "content-type": "application/xml",
    "Accept": "application/xml"}
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

# Similar to bib, but gathers holdings
# It's undocumented, but it appears you can just use any integer, hardcoded, instead of a bib MMS
# You can use something like BeautifulSoup to sort through the XML, or spin up a dedicated XML parser.
# Regex can also be helpful for replace statements
for holding in holdinglist:
    url = biburl + "9" + "/holdings/" + holding
    xml = requests.get(url, headers=headers)
    # soup = bs(xml.content, "html.parser")
    # print(soup.prettify())
    # results = soup.find(tag=852)
    # print(results.prettify())
    r = xml.text
    print(r)
    # upload = r.replace()

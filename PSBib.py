import sys
import requests

# API key as variable from another file, security
with open('PSB.txt', 'r') as file:
    key = file.read()

# Establishes base URL, Key (in separate file), Biblist (list of MMS IDs)
# Key could probably just be relabelled above.
biburl = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/"
apikey = key
biblist = [bib for bib in open('bibs.txt', 'r')]
print(biblist)

# Basic request to check connection/API key
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

# Define an added XML field
# This method treats the incoming data as text, probably not the greatest but demo purposes
# Could prep the note ahead or do it all in the replace structure as below.
# addnote = '</subfield></datafield><datafield ind1="1" ind2=" " tag="590"><subfield code="a">Example public note.</subfield></datafield>'

for bib in biblist:
    bib = bib.strip()
    url = biburl + bib
    xml = requests.get(url, headers=headers)
    r = xml.text
    print(r)
    modified = r.replace(">text</subfield>", ">tactile text</subfield>")
    print(modified)
    rewrite = requests.put(url, headers=headers, data=modified)
    print(rewrite)

import requests
from bs4 import BeautifulSoup

url = "https://reports-public-sandbox.ieso.ca/public/Demand/"
response = requests.get(url,verify=False)
soup = BeautifulSoup(response.content, "html.parser")

for link in soup.find_all("a", href=True):
    if "Demand" in link.text and ".csv" in link['href']:
        print("Found:", link['href'])
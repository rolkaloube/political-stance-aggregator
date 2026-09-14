import requests
from bs4 import BeautifulSoup

url = "https://example.com"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

# Extract links and text
for link in soup.find_all("a"):
    text = link.get_text(strip=True)
    href = link.get("href")

    if text and href:
        print(f"{text} -> {href}")

import requests
from bs4 import BeautifulSoup

# Retrieve the web page content
url = "https://portal-v1.as3.no/tools/professional-competences"
response = requests.get(url)
html_content = response.text

soup = BeautifulSoup(html_content, 'html.parser')

items = soup.select('ul.nofield-listcontent li')
#items = soup.select('div.listContent li')

# Find all div elements with the specified class
divs = soup.find_all('div', class_='listItem')

# Extract and print the text content from each div
for div in divs:
    print(div.get_text(strip=True))
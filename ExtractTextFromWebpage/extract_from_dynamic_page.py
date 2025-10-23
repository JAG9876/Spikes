from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Setup Chrome driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Retrieve the web page content
url = "https://portal-v1.as3.no/tools/professional-competences"
driver.get(url)


username_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "username"))
    # lambda d: d.find_element(By.ID, "username")
)

password_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "password"))
)

# Set a breakpoint here, start debugging, manually log in and navigate to the desired page, then continue execution.
soup = BeautifulSoup(driver.page_source, 'html.parser')

items = soup.select('ul.nofield-listcontent li div.listItem div.input-text__outer')

# Extract and print the text content from each div
for item in items:
    print(item.get_text(strip=True))

driver.quit()
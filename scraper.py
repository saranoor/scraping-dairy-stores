from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import StaleElementReferenceException

def get_text_or_blank(driver, selector, retries=3):
    for _ in range(retries):
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, selector)
            return elems[0].text.strip() if elems else ""
        except StaleElementReferenceException:
            print("stale so we are gonna retry")
            continue
    return ""


options = Options()
options.add_argument(" - headless") # Run browser in the background
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(), options=options)
driver.get("https://www.google.com/maps")
# driver.quit()

try:
    accept_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='Accept all']")
    accept_button.click()
except NoSuchElementException:
    print("No GDPR requirements detected")

search_box = WebDriverWait(driver, 5).until(
EC.presence_of_element_located((By.CSS_SELECTOR, "#searchboxinput"))
)
TARGET_PIN = "380001"
search_box.send_keys(f"dairy zip code {TARGET_PIN}")
search_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Search']")
search_button.click()

business_items = WebDriverWait(driver, 10).until(
EC.presence_of_all_elements_located((By.XPATH, '//div[@role="feed"]//div[contains(@jsaction, "mouseover:pane")]'))
)
wait = WebDriverWait(driver, 10)

cards_xpath = '//div[@role="feed"]//div[contains(@jsaction, "mouseover:pane")]'
wait.until(EC.presence_of_all_elements_located((By.XPATH, cards_xpath)))


for idx in range(len(driver.find_elements(By.XPATH, cards_xpath))):
    cards = driver.find_elements(By.XPATH, cards_xpath)
    card = cards[idx]

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
    card.click()

    # Wait until business panel loads
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf")))

    name = get_text_or_blank(driver, "h1.DUwDvf")
    address = get_text_or_blank(driver, 'button[data-item-id^="address"]')
    if TARGET_PIN not in address:
        continue
    phone = get_text_or_blank(driver, 'button[data-item-id^="phone"]')
    reviews = get_text_or_blank(driver, 'button[jsaction*="pane.rating"] span')
    link = get_text_or_blank(driver, 'a[data-item-id="authority"]')

    print(f"Business: {name}, Address: {address}, Phone: {phone}, Reviews: {reviews}, Link: {link}")

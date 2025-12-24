import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
# from exceptions import TimeoutException
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
wait = WebDriverWait(driver, 10)


try:
    accept_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='Accept all']")
    accept_button.click()
except NoSuchElementException:
    print("No GDPR requirements detected")

# --- search complete --- 
search_box = WebDriverWait(driver, 5).until(
EC.presence_of_element_located((By.CSS_SELECTOR, "#searchboxinput"))
)
TARGET_PIN = "380001"
search_box.send_keys(f"dairy zip code {TARGET_PIN}")
search_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Search']")
search_button.click()

# load all results
cards_xpath = '//div[@role="feed"]//div[contains(@jsaction, "mouseover:pane")]'
feed = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))

seen = 0

no_change_count = 0
MAX_NO_CHANGE = 15

while True:
    cards = driver.find_elements(By.XPATH, cards_xpath)

    if len(cards) == seen:
        no_change_count += 1
        if no_change_count >= MAX_NO_CHANGE:
            print("No more new cards. Done scrolling.")
            break
    else:
        no_change_count = 0
        seen = len(cards)

    driver.execute_script(
        "arguments[0].scrollTop = arguments[0].scrollHeight",
        feed
    )
    time.sleep(1.2)

print(f"total length of cards:{len(cards)}")
def wait_for_panel_change(driver, old_name, timeout=6):
    print(f"name before: {old_name}")
    WebDriverWait(driver, timeout).until(
        lambda d: get_text_or_blank(d, "h1.DUwDvf") != old_name
    )

for card in cards:
    print(f"card: {card}")
    try:
        name_before = get_text_or_blank(driver, "h1.DUwDvf")

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
        # driver.execute_script("arguments[0].click();", card)
        click_target = card.find_element(By.XPATH, ".//a | .//button")
        driver.execute_script("arguments[0].click();", click_target)

        try:
            wait_for_panel_change(driver, name_before)
        except TimeoutException:
            print("did not open anything moving on")
            continue  # click didn't open anything → skip safely
        name = get_text_or_blank(driver, "h1.DUwDvf")
        address = get_text_or_blank(driver, 'button[data-item-id^="address"] .Io6YTe')

        if TARGET_PIN not in address:
            continue

        phone = get_text_or_blank(driver, 'button[data-item-id^="phone"] .Io6YTe')
        reviews = get_text_or_blank(driver, 'button[jsaction*="pane.rating"] span')
        link = get_text_or_blank(driver, 'a[data-item-id="authority"]')

        print(f"{name} | {address} | {phone} | {reviews} | {link}")

    except StaleElementReferenceException:
        continue
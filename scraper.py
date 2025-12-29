import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re

# from exceptions import TimeoutException
def get_text_or_blank(driver, selector, retries=3):
    for _ in range(retries):
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, selector)
            return elems[0].text.strip() if elems else ""
        except StaleElsementReferenceException:
            # print("stale so we are gonna retry")
            continue
    return ""

def create_driver(proxy=None):
    opts = Options()
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--ignore-ssl-errors")
    if proxy:
        opts.add_argument(f"--proxy-server={proxy}")
    # opts.add_argument("--headless")  # enable if you want headless
    opts.add_experimental_option("detach", True)
    drv = webdriver.Chrome(service=Service(), options=opts)
    return drv

def search_box_send_keys(driver,zip_code):
    search_box = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#searchboxinput"))
    )
    TARGET_PIN = "380001"
    search_box.send_keys(f"dairy zip code {zip_code}, Ahmedabad, Gujrat")

    try:
        search_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Search']")
        search_button.click()
    except NoSuchElementException:
        search_box.send_keys(Keys.ENTER)

def load_all_cards(driver):
    cards_xpath = '//div[@role="feed"]//div[contains(@jsaction, "mouseover:pane")]'
    wait = WebDriverWait(driver, 10)
    feed = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))

    driver.execute_script("arguments[0].click();", feed)
    driver.execute_script("arguments[0].style.border='5px solid red'", feed)
    driver.maximize_window()
    driver.switch_to.window(driver.current_window_handle) # Brings tab to front
    actions = ActionChains(driver)
    actions.move_to_element(feed).click().perform()

    seen = 0
    no_change_count = 0
    MAX_NO_CHANGE = 15

    cards = driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"] > div > div[jsaction]')
    start_load = time.perf_counter()

    while True:
        cards = driver.find_elements(By.XPATH, cards_xpath)
        
        if len(cards) > seen:
            seen = len(cards)
            no_change_count = 0
            print(f"Total cards loaded: {seen}")
        else:
            no_change_count += 1
            print("giving chance")
            if no_change_count >= MAX_NO_CHANGE:
                break

        if cards:
            time.sleep(0.5)
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)

        time.sleep(0.5) 
    print(f"total length of cards:{len(cards)}")
    load_duration = time.perf_counter() - start_load
    print(f"Time taken to load all cards: {load_duration:.2f} seconds")
    return cards

def parse_cards(driver, cards, zip_code):
    last_name = ""
    rows =[]
    wait = WebDriverWait(driver, 10)

    for card in cards:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
            old_title = driver.find_elements(By.CSS_SELECTOR, "h1.DUwDvf")
            old_title = old_title[0] if old_title else None
            click_target = card.find_element(By.XPATH, ".//a | .//button")  
            driver.execute_script("arguments[0].click();", click_target)   

            try:
                if old_title:
                    wait.until(EC.staleness_of(old_title))
                    wait.until(lambda d: (
                        (title := d.find_elements(By.CSS_SELECTOR, "h1.DUwDvf"))
                        and title[0].text.strip()
                        and title[0].text.strip() != last_name
                    ))
            except TimeoutException as e:
                print(f"stale wait did not work moving on and the error is: {e}")  
                print("\n")
                continue

            name = get_text_or_blank(driver, "h1.DUwDvf")
            address = get_text_or_blank(driver, 'button[data-item-id^="address"] .Io6YTe')   

            if zip_code not in address:
                addr = "gulbahar mil taskkant road, 380012, Ahmedabad Gujarat"
                match = re.search(r"\b\d{6}\b", addr)
                postal_code = match.group(0)
            else:
                postal_code = zip_code
            phone = get_text_or_blank(driver, 'button[data-item-id^="phone"] .Io6YTe')
            rating = get_text_or_blank(driver, 'div.F7nice span[aria-hidden="true"]')

            last_name = name
            rows.append({
                    "Name": name,
                    "Address": address,
                    "Phone": phone,
                    "review_count": rating,
                    "zip_code": postal_code

                })
        except (StaleElementReferenceException) as e:
            print("did not open anything moving on:", e)
            continue
    return rows

def get_zip_code_dairy(zip_code, proxy):    
    driver = create_driver(proxy)
    driver.get("https://www.google.com/maps")
    search_box_send_keys(driver, zip_code)
    cards = load_all_cards(driver)
    rows = parse_cards(driver, cards,zip_code)

    df = pd.DataFrame(rows)
    df.to_excel(f"dairy_{zip_code}.xlsx", index=False)
    print(f"Saved to dairy_{zip_code}.xlsx")

    time.sleep(60)
    driver.quit()

# get_zip_code_dairy("380004",None)

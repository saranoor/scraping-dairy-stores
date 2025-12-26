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

def get_zip_code_dairy(zip_code, proxy):
    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument(f"--proxy-server={proxy}")
    options.add_argument(" - headless") # Run browser in the background
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(), options=options)
    driver.get("https://httpbin.io/ip")
    time.sleep(5)
    driver.get("https://www.google.com/maps")
    # driver.quit()
    actions = ActionChains(driver)
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
    search_box.send_keys(f"dairy zip code {zip_code}, Ahmedabad, Gujrat")

    try:
        search_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Search']")
        search_button.click()
    except NoSuchElementException:
        search_box.send_keys(Keys.ENTER)

    # load all results
    cards_xpath = '//div[@role="feed"]//div[contains(@jsaction, "mouseover:pane")]'
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

        # THE FIX: Scroll to the last card specifically
        if cards:
            # Move mouse to the card and click (focuses the tab context)
            # actions = ActionChains(driver)
            # actions.move_to_element(cards[-1]).click().perform()
            
            # Small wait for the click to register
            time.sleep(0.5)
            
            # Scroll the feed container
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)

        time.sleep(2.5) # Crucial: Google Maps throttles rapid requests
    print(f"total length of cards:{len(cards)}")
    def wait_for_panel_change(driver, old_name, timeout=15):
        print(f"name before: {old_name}")
        WebDriverWait(driver, timeout).until(
            lambda d: get_text_or_blank(d, "h1.DUwDvf") != old_name
        )
    
    def wait_for_selection(card, timeout=10):
        WebDriverWait(driver, timeout).until(
            lambda d: (
                card.get_attribute("aria-selected") == "true"
                or "bfdHYd" in (card.get_attribute("class") or "")
            )
        )

    last_name = ""
    rows =[]



    for card in cards:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
            old_title = driver.find_elements(By.CSS_SELECTOR, "h1.DUwDvf")
            old_title = old_title[0] if old_title else None
            click_target = card.find_element(By.XPATH, ".//a | .//button")  
            driver.execute_script("arguments[0].click();", click_target)   
            # 🔴 WAIT until the place name changes
            try:
                wait.until(lambda d: card.get_attribute("aria-selected") == "true")
            except TimeoutException:
                print("card did not get selected moving on")
            try:
                wait.until(lambda d: (
                    d.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text.strip() != "" and
                    d.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text.strip() != last_name
                ))
            except TimeoutException:
                print("place name did not change moving on")

            try:
                if old_title:
                    print("wait for panel refresh")
                    wait.until(EC.staleness_of(old_title))
                    print("wait for the panel content to load")
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf")))
            except TimeoutException as e:
                print(f"stale wait did not work moving on and the error is: {e}")  
                print("\n")
                continue

            name = get_text_or_blank(driver, "h1.DUwDvf")
            address = get_text_or_blank(driver, 'button[data-item-id^="address"] .Io6YTe')   
            if zip_code not in address:
                print(f"Skipping {name} as it does not match the zip code {zip_code} in address: {address}")
                continue

            phone = get_text_or_blank(driver, 'button[data-item-id^="phone"] .Io6YTe')
            rating = get_text_or_blank(driver, 'div.F7nice span[aria-hidden="true"]')
            link = get_text_or_blank(driver, 'a[data-item-id="authority"]') 
            print(f"{name} | {address}") 
            print("\n")
            last_name = name
            rows.append({
                    "Name": name,
                    "Address": address,
                    "Phone": phone,
                    "review_count": rating

                })
        except (StaleElementReferenceException) as e:
            print("did not open anything moving on:", e)
            continue

    df = pd.DataFrame(rows)
    df.to_excel(f"dairy_{zip_code}.xlsx", index=False)
    print(f"Saved to dairy_{zip_code}.xlsx")

    driver.quit()

# get_zip_code_dairy("380001",None)
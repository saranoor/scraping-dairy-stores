import queue
from threading import Thread
import requests
from bs4 import BeautifulSoup
import time
from scraper import get_zip_code_dairy
from urllib3.exceptions import ReadTimeoutError

class FreeProxy:
    def __init__(self):
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }


    def get_proxies(self):
        self.proxies = queue.Queue()
        
        url = "https://free-proxy-list.net"
        r = requests.get(url, headers=self.headers)

        soup = BeautifulSoup(r.text, "html.parser")
        table_rows = soup.find("section", attrs={"id": "list"}).find("tbody").find_all("tr")

        for row in table_rows:
            ip_address = row.find_all("td")[0].text.strip()
            port = row.find_all("td")[1].text.strip()

            if row.find_all("td")[6].text.strip() == "yes":
                self.proxies.put(f"{ip_address}:{port}")

        # print(f"Total proxies fetched: {self.proxies.qsize()}")
        # print(f"Print proxies queue: {self.proxies.queue}")


    def check_proxies(self):
        self.valid_proxies = []

        while not self.proxies.empty():
            proxy = self.proxies.get()

            try:
                r = requests.get("https://www.google.com/maps", headers=self.headers, proxies={"http": proxy, "https": proxy}, timeout=5)
                # print(f"Proxy {proxy} is valid")
                # print(f'r.status_code: {r.status_code}')

            except:
                # print(f"Proxy {proxy} failed")
                continue

            if r.status_code == 200:
                self.valid_proxies.append(proxy)


    def get_proxy_list(self):
        while True:
            try:
                self.get_proxies()

                threads = [Thread(target=self.check_proxies) for _ in range(32)]

                [t.start() for t in threads]
                [t.join() for t in threads]

                assert len(self.valid_proxies) > 0
            
                return self.valid_proxies
            except:
                # print("Retrying to fetch proxies...")
                continue
    

if __name__ == "__main__":
    free_proxy = FreeProxy()
    proxy_list = free_proxy.get_proxy_list()
    print(proxy_list)

    # from selenium import webdriver

    # from selenium.webdriver.chrome.service import Service

    # from webdriver_manager.chrome import ChromeDriverManager

    # from selenium.webdriver.chrome.options import Options

    # from selenium.webdriver.common.by import By



    # define the proxy address and port

    # proxy = proxy_list[0] #"20.235.159.154:80"
    # get_zip_code_dairy("380001", proxy=proxy) 

    while True: 
        proxy = proxy_list.pop()
        try:
            get_zip_code_dairy("380003", proxy=proxy)  
            print("Success with proxy:", proxy, "for zip code 380002. Now breaking out of loop.")
            break
        except ReadTimeoutError as e:
            print(f"Proxy {proxy} failed: {e}. Trying next proxy...")
            continue
        except Exception as e:
            print(f"Proxy {proxy} failed: {e}. Trying next proxy...")
            continue

    # # set Chrome options to run in headless mode using a proxy

    # options = Options()

    # # options.add_argument("--headless=new")

    # options.add_argument(f"--proxy-server={proxy}")
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument('--ignore-ssl-errors')



    # # initialize Chrome driver

    # driver = webdriver.Chrome(

    #     service=Service(ChromeDriverManager().install()),

    #     options=options

    # )
    # driver.get("https://www.google.com/maps")
    # time.sleep(120)
    # driver.quit()


    # # navigate to the target webpage
    # while (len(proxy_list) > 0):
    #     try:
    #         # driver.get("https://httpbin.io/ip")
    #         # time.sleep(5)
    #         # driver.get("https://www.whatismyip.com/")
    #         # time.sleep(5)
    #         # driver.get("https://www.google.com/maps")
    #         # time.sleep(5)



    #         # print the body content of the target webpage

    #         # print(driver.find_element(By.TAG_NAME, "body").text)



    #         # release the resources and close the browser

    #         # driver.quit()
    #         get_zip_code_dairy("380001", proxy=proxy)   
    #         break
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    #         # driver.quit()
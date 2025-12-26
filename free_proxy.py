import queue
from threading import Thread
import requests
from bs4 import BeautifulSoup
import time

class FreeProxy:
    def __init__(self):
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }


    def get_proxies(self):
        print("Fetching proxies from free-proxy-list.net...")
        self.proxies = queue.Queue()
        print("Feted proxies from free-proxy-list.net...")
        url = "https://free-proxy-list.net"
        r = requests.get(url, headers=self.headers)

        soup = BeautifulSoup(r.text, "html.parser")
        table_rows = soup.find("section", attrs={"id": "list"}).find("tbody").find_all("tr")

        for row in table_rows:
            ip_address = row.find_all("td")[0].text.strip()
            port = row.find_all("td")[1].text.strip()

            if row.find_all("td")[6].text.strip() == "yes":
                self.proxies.put(f"{ip_address}:{port}")

        print(f"Total proxies fetched: {self.proxies.qsize()}")
        print(f"Print proxies queue: {self.proxies.queue}")


    def check_proxies(self):
        self.valid_proxies = []

        while not self.proxies.empty():
            proxy = self.proxies.get()

            try:
                r = requests.get("https://www.google.com/maps", headers=self.headers, proxies={"http": proxy, "https": proxy}, timeout=5)
                print(f"Proxy {proxy} is valid")
                print(f'r.status_code: {r.status_code}')

            except:
                print(f"Proxy {proxy} failed")
                continue

            if r.status_code == 200:
                self.valid_proxies.append(proxy)


    def get_proxy_list(self):
        while True:
            try:
                self.get_proxies()
                print("Checking proxies...")
                threads = [Thread(target=self.check_proxies) for _ in range(32)]
                print("Starting proxy validation threads...")
                [t.start() for t in threads]
                [t.join() for t in threads]
                print("Proxy validation completed.")    
                assert len(self.valid_proxies) > 0
            
                return self.valid_proxies
            except:
                print("Retrying to fetch proxies...")
                continue
    
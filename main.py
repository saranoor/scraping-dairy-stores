from scraper import get_zip_code_dairy
from urllib3.exceptions import ReadTimeoutError
from free_proxy import FreeProxy

if __name__ == "__main__":
    free_proxy = FreeProxy()
    print("Fetching proxy list...")
    proxy_list = free_proxy.get_proxy_list()
    print(f"Valid proxies: {proxy_list}")

    while True: 
        proxy = proxy_list.pop()
        try:
            get_zip_code_dairy("380004", proxy=proxy)  
            print("Success with proxy:", proxy, "for zip code 380004. Now breaking out of loop.")
            break
        except ReadTimeoutError as e:
            print(f"Proxy {proxy} failed: {e}. Trying next proxy...")
            continue
        except Exception as e:
            print(f"Proxy {proxy} failed: {e}. Trying next proxy...")
            continue


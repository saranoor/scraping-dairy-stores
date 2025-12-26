# Scraping Google Maps (Dairy Listings)

## Problem
Extract dairy business details (name, address, phone, rating) from Google Maps for a given ZIP code. Google throttles/block-lists repeated requests, so the scraper needs proxy rotation and resilient DOM handling.

## How It’s Solved
- Fetch free HTTPS proxies, filter for ones that can reach Google, and pick a working proxy.
- Launch Selenium with Chrome, optionally via the chosen proxy.
- Load Google Maps, accept consent, search for “dairy zip code <ZIP>”.
- Scroll the results feed until all cards load.
- Click each card, wait for the detail pane to refresh, and scrape fields.
- Save results to an Excel file `dairy_<zip>.xlsx`.

## Key Components
- `free_proxy.py`: Scrapes `free-proxy-list.net`, checks proxies against Google Maps, returns a validated proxy list.
- `scraper.py`: Core Selenium scraper; `get_zip_code_dairy(zip, proxy)` loads Maps, scrolls results, clicks cards, and extracts name/address/phone/rating.
- `main.py`: Orchestrates proxy selection and runs the scraper for a target zip (e.g., `380004`).
- Outputs: `dairy_<zip>.xlsx` files with scraped rows.

## Tech Stack
- Python 3
- Selenium (Chrome/Chromedriver)
- Requests + BeautifulSoup (proxy discovery)
- pandas (Excel export)

## Usage
1. Install dependencies (in your venv):
    .\.venv\Scripts\Activate.ps1
    deactivate
    pip install -r requirements.txt

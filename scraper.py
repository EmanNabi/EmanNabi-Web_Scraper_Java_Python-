# python scraper
import os
import re
import requests
import threading
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Constants for base URL, output directory, timeout, and threading parameters
BASE_URL = "https://papers.nips.cc"
OUTPUT_DIR = "D:/Data Science/Scraped_Data-Using_Python/"
TIMEOUT = 30  # Timeout in seconds for HTTP requests
THREAD_COUNT = 10  # Number of threads to use for concurrent scraping
START_YEAR = 2020  # Starting year for scraping papers
END_YEAR = 2024  # Ending year for scraping papers

# Fetches the HTML content from a given URL
def fetch_url(url):
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return None

# Extracts the year from a string
def extract_year(text):
    match = re.search(r"(\d{4})", text)
    return int(match.group(1)) if match else None

# Processes the year page to extract paper links and submits them for further processing
def process_year(year_url, year):
    html = fetch_url(year_url)
    if not html:
        return
    
    soup = BeautifulSoup(html, 'html.parser')
    paper_links = soup.select("ul.paper-list li a[href$='Abstract-Conference.html']")
    
    if not paper_links:
        return

    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        for paper_link in paper_links:
            paper_url = BASE_URL + paper_link['href']
            executor.submit(process_paper, paper_url, year)

# Processes each paper page to find and download the PDF link
def process_paper(paper_url, year):
    html = fetch_url(paper_url)
    if not html:
        return
    
    soup = BeautifulSoup(html, 'html.parser')
    pdf_link = soup.select_one("a[href$='Paper-Conference.pdf']")
    if pdf_link:
        pdf_url = BASE_URL + pdf_link['href']
        download_pdf(pdf_url, year)

# Downloads the PDF from the given URL and saves it in the appropriate year folder
def download_pdf(pdf_url, year):
    file_name = pdf_url.split('/')[-1]
    year_dir = os.path.join(OUTPUT_DIR, str(year))
    os.makedirs(year_dir, exist_ok=True)
    file_path = os.path.join(year_dir, file_name)
    
    try:
        response = requests.get(pdf_url, stream=True, timeout=TIMEOUT)
        response.raise_for_status()
        
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(8192):
                file.write(chunk)
        print(f"Successfully downloaded: {file_name}")
    except requests.RequestException as e:
        print(f"Failed to download {pdf_url}: {e}")

# Main entry point: fetches the main page, extracts year links, and triggers further processing
def main():
    html = fetch_url(BASE_URL)
    if not html:
        print("Failed to fetch the main page. Exiting...")
        return
    
    soup = BeautifulSoup(html, 'html.parser')
    year_links = soup.select("a[href*='/paper/']")
    
    if not year_links:
        print("No year links found!")
        return
    
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        for year_link in year_links:
            year_text = year_link.text.strip()
            year = extract_year(year_text)
            if year and START_YEAR <= year <= END_YEAR:
                year_url = BASE_URL + year_link['href']
                executor.submit(process_year, year_url, year)

if __name__ == "__main__":
    main()
import requests
from bs4 import BeautifulSoup
import json
import argparse
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime
import re
import logging
import sys
import uuid
import time
import random
import traceback

# ============================================================
# Global run identifiers and logging configuration
# ============================================================
session_id = uuid.uuid4().hex[:12]

today = datetime.today()
date_save = today.strftime("%Y-%m-%d")
logging.basicConfig(filename='boerseLog.log',level=logging.INFO,
                    encoding='utf-8',
                    format='%(asctime)s : %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')


# ============================================================
# Command-line arguments
# ============================================================
parser = argparse.ArgumentParser(description="Forum Scraper")


parser.add_argument("--mode", choices=["normal", "deep"], required=True)
parser.add_argument("--proxy", choices=["true", "false"], default="false")
parser.add_argument("--username", type=str, required=False)
parser.add_argument("--password", type=str, required=False)
parser.add_argument("--keyword", type=str, required=True, help="Keyword to search for in the forum")

args = parser.parse_args()


print("=" * 72)
print("BOERSE.CX FORUM SCRAPER")
print("=" * 72)
print(f"Mode        : {args.mode}")
print(f"Proxy       : {args.proxy}")
print(f"Username    : {args.username}")
print(f"Password    : {args.password}")
print(f"Keyword     : {args.keyword}")
print(f"Run Session : {session_id}")
print("=" * 72)



# ============================================================
# Main scraper class
# ============================================================
class BoerseScraper:

    mode = args.mode
    proxy = args.proxy  
    username = args.username
    password = args.password
    keyword = args.keyword
    cookies_file = "cookies.json"
    save = []


    # Only links from these file-hosting domains are saved.
    ALLOWED_HOSTERS = {
        "ddownload.com",
        "uploadrar.com",
        "mega4upload.net",
        "rapidgator.net",
        "katfile.com",
        "turbobit.net",
        "nitroflare.com",
    }


    # Browser-like request headers used by the requests session.
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://boerse.cx',
        'priority': 'u=0, i',
        'referer': 'https://boerse.cx/',
        'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Microsoft Edge";v="150"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0',
    }

    # --------------------------------------------------------
    # Initialization
    # --------------------------------------------------------
    def __init__(self):
        print("[INIT] Preparing output directory...")
        folder = Path.cwd() / "savefiles"
        folder.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Output directory ready: {folder}")


    # --------------------------------------------------------
    # Session and optional proxy setup
    # --------------------------------------------------------
    def create_session(self):
        self.ses = requests.Session()
        self.ses.headers.update(self.headers)

        if self.proxy == "true":
            proxy_username = (
                "brd-customer-hl_92acb0c1"
                "-zone-pool_arnaldo_abrasaldo_rotatin"
                "-country-de"
                f"-session-{session_id}"
            )

            proxy_password = "Brigth data password"

            proxy_url = (
                f"http://{proxy_username}:{proxy_password}"
                "@brd.superproxy.io:44445"
            )

            self.ses.proxies.update({
                "http": proxy_url,
                "https": proxy_url,
            })

            print("=" * 70)
            print("[PROXY] Bright Data proxy enabled")
            print(f"[PROXY] Country: Germany")
            print(f"[PROXY] Sticky session: {session_id}")
            print("=" * 70)

        else:
            print("=" * 70)
            print("[PROXY] Proxy disabled")
            print("[PROXY] Using the machine's direct IP")
            print("=" * 70)

    # --------------------------------------------------------
    # Login and cookie handling
    # --------------------------------------------------------
    def login(self):
        print("[LOGIN] Opening forum home page...")
        response = self.ses.get('https://boerse.cx/',timeout=100)
        csrf = response.text.split('data-csrf="')[1].split('"')[0]

        data = {
            'login': self.username,
            'password': self.password,
            'remember': '1',
            '_xfRedirect': 'https://boerse.cx/',
            '_xfToken': csrf
        }

        response = self.ses.post('https://boerse.cx/login/login', data=data)
        print(f"[LOGIN] Response status: {response.status_code}")
        if response.status_code != 200:
            print('Failed to log in !')
            print('Check username / password if valid')
            self.exit()

        cookies = requests.utils.dict_from_cookiejar(self.ses.cookies)

        with open("cookies.json", "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=4)

        print("[OK] Cookies saved to cookies.json")
        with open('boerseLog.log', 'w'):
            pass


    def check_login(self):
        print("[LOGIN] Checking whether credentials were supplied...")

        if self.username is not None and self.password is not None:
            self.login()


    def check_cookies(self):
        try:
            with open(self.cookies_file, "r", encoding="utf-8") as f:
                cookies = json.load(f)
                self.ses.cookies.update(requests.utils.cookiejar_from_dict(cookies))
                print("[OK] Cookies loaded into session.")

            return True
        except FileNotFoundError:
            print("[ERROR] Cookies file not found. Please log in first.")
            input("Press Enter to exit...")
            return False


    def check_session(self):
        print("[SESSION] Validating saved forum session...")

        url = 'https://boerse.cx/thema/der-spiegel-geschichte-06-2024.249711/'
        response = self.ses.get(url,timeout=100)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.select_one(".p-title-value").get_text(strip=True)
            print(f"[SESSION] Validation page: {title}")
            print("[OK] Session is valid.")
            return True
        
        else:
            print("[ERROR] Session is invalid. Please log in again.")
            return False

    # --------------------------------------------------------
    # Search initialization
    # --------------------------------------------------------
    def get_search_id(self):
        print(f"[SEARCH] Starting search for: {self.keyword}")
        response = self.ses.get('https://boerse.cx/')
        csrf = response.text.split('data-csrf="')[1].split('"')[0]
        
        data = {
            'keywords': self.keyword,
            'c[title_only]': '1',
            'c[users]': '',
            'c[word_count][lower]': '',
            '_xfToken': csrf,
        }

        response = self.ses.post('https://boerse.cx/search/search', data=data)
        print(f"[SEARCH] POST status: {response.status_code}")
        print(f"[SEARCH] Search URL: {response.url}")
        self.id_url = response.url

    # Exit helper for terminal use.
    def exit(self):
        input("Press Enter to exit...")
        sys.exit(1)

    # --------------------------------------------------------
    # Thread-page scraping
    # --------------------------------------------------------
    def scrape_page(self, link, pagenum):
        print(f"[THREAD] Requesting listing page {pagenum}: {link}")
        xx = 0
        while True:
            if xx == 10:
                logging.error('Error! navigating to page url -- ' + link)
                self.exit()
            try:
                response = self.ses.get(link,timeout=100)
                if response.status_code == 200:
                    break
            except Exception as e:
                print(e)
                xx += 1


        if response.status_code != 200:
            logging.info("-" * 113)
            logging.error(
                f"HTTP {response.status_code} while requesting {link}"
            )
            logging.info("-" * 113)
            self.exit()

        soup = BeautifulSoup(response.text, "html.parser")

        # Session expired
        if "/login" in response.url or soup.select_one('input[name="login"]'):
            logging.info("-" * 113)
            logging.error("Session expired. Login page detected.")
            logging.error(f"URL: {link}")
            logging.info("-" * 113)

            # Optional: re-login and retry
            # self.login()
            # return self.scrape_page(link, pagenum)
            self.exit()


        soup = BeautifulSoup(response.text, "html.parser")

        try:
            title = soup.select_one(".p-title-value").get_text(strip=True)
        except:
            title = "N/A"

        try:
            post_date = soup.select_one(".message-cell.message-cell--main time")["datetime"]
        except:
            post_date = None

        # Determine page number

        downloads = []

        for a in soup.select("div.bbWrapper a[href]"):
            url = a["href"].strip()

            # Skip invalid links
            if not url.startswith(("http://", "https://")):
                continue

            domain = urlparse(url).netloc.lower().removeprefix("www.")

            # Allow subdomains (e.g. files.ddownload.com)
            if any(
                domain == host or domain.endswith("." + host)
                for host in self.ALLOWED_HOSTERS
            ):
                downloads.append(url)

        for download in downloads:
            self.save.append({
                "thread_url": link,
                "thread_title": title,
                "post_date": post_date,
                "page_numer":pagenum,
                "download_link": download,
                "hoster_domain": urlparse(download).netloc,
                "search_term": self.keyword,
            })
            print(
                "[FOUND] page {} | title({}) | link({})".format(
                    str(pagenum),
                    title,
                    download,
                )
            )

        logtitle = ' completed - ' + title + ' | url - ' + link
        logging.info(logtitle)

        delay = random.uniform(2.0, 4.7)
        print(f'[DELAY] Waiting {delay:.2f} seconds before the next request...')
        time.sleep(delay)


    # Read the most recently saved listing page for resume support.
    def get_last_page(self):

        path = Path('savefiles') / f"{self.safe_filename(self.keyword)}.json"

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        last_page = data[-1]["page_numer"]
        return last_page

    # --------------------------------------------------------
    # Search-result listing pagination
    # --------------------------------------------------------
    def scrape_listing(self):

        try:
            num = self.get_last_page() 
            num = int(num) + 1
        except Exception as e:
            num = 1

        if self.mode == 'normal':
            num = 1
                
        print('=' * 72)
        print(f'[LISTING] Starting on search-result page: {num}')
        print(f'[LISTING] Mode: {self.mode}')
        print('=' * 72)
        for i in range(num, 1000):  # Scrape first 2 pages for demonstration

            xx = 0
            while True:
                if xx == 10:
                    logging.error('Error! looping to pages ..')
                    self.exit()
                try:
                    response = self.ses.get(f"{self.id_url}&page={i}",timeout=100)
                    print(f"[LISTING] Page {i} status: {response.status_code}")

                    if response.status_code == 200:
                        break
                    else:
                        print(f"[RETRY] Error fetching listing page {i}. Retrying...")
                except requests.exceptions.RequestException as e:
                    print(f"[RETRY] Request failed: {e}. Retrying...")
                    xx += 1
                except Exception as e:
                    print(e)
                    xx += 1


            print(f"[LISTING] Page {i} final status: {response.status_code}")
            urlpage = response.url.split('page=')[1]
            urlpage = int(urlpage)
            if i > urlpage:
                print('[DONE] Reached the final listing page.')
                logging.info('Finish!')
                break

            soup = BeautifulSoup(response.text, "html.parser")

            cards = soup.select('.contentRow-title')

            if cards == []:
                print('[DONE] No result cards found on this page.')
                break

            for href in cards:
                link = 'https://boerse.cx' + href.find('a')['href']
                self.scrape_page(link,str(i))

            if self.mode == 'normal':
                break

    # Convert the keyword into a Windows/Linux-safe filename.
    def safe_filename(self,text: str) -> str:
        # Remove invalid filename characters
        text = re.sub(r'[<>:"/\\|?*]', '', text)

        # Replace whitespace with underscores
        text = re.sub(r'\s+', '_', text.strip())

        return text

    # --------------------------------------------------------
    # JSON saving and deduplication
    # --------------------------------------------------------
    def save_file(self):
        print("[SAVE] Preparing JSON output...")
        folder = Path("savefiles")
        folder.mkdir(parents=True, exist_ok=True)

        path = folder / f"{self.safe_filename(self.keyword)}.json"

        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []

        data.extend(self.save)

        # Remove duplicates by download_link
        unique = {}
        for item in data:
            unique[item["download_link"]] = item

        data = list(unique.values())

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"[OK] Saved {len(data)} unique download links.")
        print(f"[OK] Output file: {path.resolve()}")

    # --------------------------------------------------------
    # Main execution flow
    # --------------------------------------------------------
    def crawler(self):

        print("[START] Initializing scraper workflow...")
        self.create_session()
        self.check_login()

        if not self.check_cookies():
            return

        if not self.check_session():
            print("Please log in again to refresh cookies.")
            input("Press Enter to exit...")
            return

        logging.info('Initialize ... (boerse.cx) forum scraper....')
        logging.info('keyword = ' + self.keyword)
        logging.info('---------------------------------------------------->')
        logging.info('')

        self.get_search_id()
        self.scrape_listing()
        self.save_file()

        print("=" * 72)
        print("SCRAPING COMPLETED")
        print(f"New records collected this run: {len(self.save)}")
        print("=" * 72)

    def main(self):
        try:
            self.crawler()
        except Exception as e:
            error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            logging.info("-" * 113)
            logging.error(f"An error occurred: forum_scraper.py \n%s", error_message)
            logging.error("-" * 113)


if __name__ == "__main__":
    boerse_scraper = BoerseScraper()
    boerse_scraper.main()


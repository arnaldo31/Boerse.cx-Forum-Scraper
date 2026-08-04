# Boerse.cx Forum Scraper (Python + Requests + BeautifulSoup)

A Python scraper for the **Boerse.cx** forum that searches using a specified keyword and supports both **Normal** and **Deep** scraping modes. The `--keyword` and `--mode` command-line arguments are **required**. The scraper automatically reuses saved login cookies, optionally logs in using a username and password when `cookies.json` is missing or the session has expired, supports optional proxy usage, extracts download links only from supported file-hosting websites, skips all unsupported hosts, removes duplicate download links, and exports the extracted results as structured JSON files.

The scraper supports:

- Normal Mode
- Deep Mode
- Cookie Login
- Optional Proxy
- Automatic Duplicate Removal
- Resume Support
- JSON Output
- Supported Hoster Filtering

---

## Supported Download Hosts

The scraper only saves download links from the following supported file-hosting websites:

- ddownload.com
- uploadrar.com
- mega4upload.net
- rapidgator.net
- katfile.com
- turbobit.net
- nitroflare.com

Any download links from websites **not included in this list are automatically skipped and will not be saved**.
# INSTALLATION

## 1. Install Python

Download Python 3.10 or newer:

https://www.python.org/downloads/

**IMPORTANT**

✔ Check **Add Python to PATH**

Verify installation:

```bash
python --version
pip --version
```

---

## 2. Open Command Prompt (CMD)

- Press **Windows + R**
- Type:

```text
cmd
```

- Press **Enter**

Run all commands inside CMD.

---

## 3. Install Libraries

Install one by one:

```bash
pip install requests
pip install beautifulsoup4
```

Or install everything at once:

```bash
pip install requests beautifulsoup4
```

---

# PROJECT STRUCTURE

```text
boerse-scraper/
├── forum_scraper.py
├── cookies.json
├── boerseLog.log
├── savefiles/
└── README.md
```

---

# HOW TO RUN

## Normal Mode

```bash
python forum_scraper.py --mode normal --keyword "DER SPIEGEL"
```

---

## Deep Mode

```bash
python forum_scraper.py --mode deep --keyword "DER SPIEGEL"
```

---

## Using Proxy

```bash
python forum_scraper.py --mode deep --proxy true --keyword "DER SPIEGEL"
```

Proxy is disabled by default.

---

## Login (Only Required When Needed)

If **cookies.json** does not exist, or your login session has expired, run:

```bash
python forum_scraper.py --mode normal --keyword "DER SPIEGEL" --username YOUR_USERNAME --password YOUR_PASSWORD
```

After a successful login, the scraper automatically creates:

```text
cookies.json
```

Future runs **do not require** the username and password while the cookies remain valid.

---

# COMMAND LINE OPTIONS

| Argument | Required | Description |
|----------|----------|-------------|
| --mode | Yes | Scraping mode (`normal` or `deep`) |
| --keyword | Yes | Keyword to search |
| --proxy | No | Enable proxy (`true` or `false`) |
| --username | Only if login is required | Forum username |
| --password | Only if login is required | Forum password |

---

# OUTPUT

All scraped data is saved inside:

```text
savefiles/
```

Example:

```text
savefiles/DER_SPIEGEL.json
```

The filename is automatically generated from the search keyword.

---

# SCRAPED DATA SCHEMA

| Field | Type | Description |
|--------|------|-------------|
| thread_url | String | URL of the forum thread |
| thread_title | String | Thread title |
| post_date | String / Null | Date the post was created |
| page_numer | String | Search result page number |
| download_link | String | Download URL extracted from the thread |
| hoster_domain | String | Download host domain |
| search_term | String | Search keyword used |

---

# SAMPLE JSON

```json
[
    {
        "thread_url": "https://boerse.cx/thema/example-thread.12345/",
        "thread_title": "Example Thread",
        "post_date": "2026-08-04T09:35:00+00:00",
        "page_numer": "1",
        "download_link": "https://rapidgator.net/file/example",
        "hoster_domain": "rapidgator.net",
        "search_term": "DER SPIEGEL"
    }
]
```

---

# SUPPORTED DOWNLOAD HOSTS

The scraper only saves download links from the following hosts:

- ddownload.com
- uploadrar.com
- mega4upload.net
- rapidgator.net
- katfile.com
- turbobit.net
- nitroflare.com

---

# FEATURES

✔ Keyword Search

✔ Normal & Deep Mode

✔ Cookie Session Support

✔ Automatic Login (when needed)

✔ Optional Bright Data Proxy

✔ Automatic Duplicate Removal

✔ Resume Support

✔ Random Human-like Delay

✔ JSON Output

✔ Logging

---

# IMPORTANT NOTES

- Username and password are **only required** if **cookies.json** does not exist or the session has expired.
- Keywords containing spaces **must be enclosed in quotes**.

Example:

```bash
--keyword "DER SPIEGEL"
```

- Output files are automatically deduplicated using the `download_link` field.
- Logs are saved to:

```text
boerseLog.log
```

- Scraped JSON files are saved inside:

```text
savefiles/
```

---

# AUTHOR

Built using:

- Python
- Requests
- BeautifulSoup

# 📊 SEC EDGAR Filing Alert Bot

A Scrapy spider that queries the SEC EDGAR full-text search API across 500+ small-cap tickers and curated keywords, monitors 8-K/6-K/10-Q and 13F filings, parses filing index pages for metadata, and sends real-time Telegram alerts with filing details and direct document links.

---

## Features

- Monitors **500+ small-cap tickers** across two search strategies:
  - **Keyword + Ticker** — searches 8-K and 6-K filings using curated phrases (e.g. `"licensing agreement"`, `"FDA granted"`, `"Private Placement"`)
  - **Ticker-only** — searches broader form types (10-Q, 13F-HR, 424B4, etc.) for all tracked tickers
- Queries the **SEC EDGAR full-text search API** (`efts.sec.gov`)
- Parses filing index pages for:
  - Filing date & time (formatted as UTC)
  - Form type
  - Ticker symbol
  - Company name
  - Direct filing document URL
- Sends **real-time Telegram alerts** via bot on every new match
- Configurable date ranges for both search modes

---

## Requirements

- Python 3.8+
- Scrapy
- Requests

```bash
pip install scrapy requests
```

---

## Project Structure

```
secgov/
├── spiders/
│   └── sec.py           # Main EDGAR spider
├── pipelines.py         # Telegram alert pipeline
├── middlewares.py       # Scrapy middlewares
├── settings.py          # Scrapy settings
└── __init__.py
scrapy.cfg
```

---

## Configuration

### 1. Telegram Bot (`pipelines.py`)

Replace the placeholders with your bot credentials:

```python
BOT_TOKEN = "Enter YOUR TOKEN"
CHAT_ID   = "ENTER CHAT ID"
```

To get these:
- Create a bot via [@BotFather](https://t.me/BotFather) to get your `BOT_TOKEN`
- Use the [Chat ID Bot](https://github.com/) utility to retrieve your `CHAT_ID`

### 2. Search Parameters (`sec.py`)

| Setting | Description |
|---|---|
| `KEYWORDS` | Phrases to search in 8-K/6-K filings |
| `TICKERS` | List of stock tickers to monitor |
| `FORMS_K` | Forms used with keyword search (`6-K`, `8-K`) |
| `FORMS_Q` | Forms used with ticker-only search (`10-Q`, `13F-HR`, etc.) |
| `startdt` / `enddt` | Date range for each search mode |

### 3. Cookies & Headers

The spider includes browser-like cookies and headers to avoid bot detection. Update the `cookies` dict in `sec.py` if requests start getting blocked.

---

## Usage

Enable the Telegram pipeline in `settings.py`:

```python
ITEM_PIPELINES = {
    'secgov.pipelines.TelegramAlertPipeline': 300,
}
```

Then run the spider:

```bash
scrapy crawl edgar
```

Or export to CSV alongside Telegram alerts:

```bash
scrapy crawl edgar -o filings.csv
```

---

## Output

### Telegram Alert Format

```
📢 New EDGAR Filing Alert

Filing Date: Oct 28, 2024, 06:31:25 UTC
Form Type:   8-K
Ticker:      AAPL
Company Name: Example Corp
View Filing: https://www.sec.gov/Archives/edgar/data/...
```

### CSV / JSON Fields

| Field | Description |
|---|---|
| `Filing_date` | Formatted filing timestamp (UTC) |
| `Form_type` | SEC form type (8-K, 10-Q, etc.) |
| `Ticker` | Stock ticker symbol |
| `Company_Name` | Company name (cleaned) |
| `View Fillings` | Direct URL to the filing document |

---

## How It Works

1. **Search Phase** — Generates API requests combining keywords × tickers for 8-K/6-K, then ticker-only requests for 10-Q/13F forms
2. **Parse Phase** — Extracts filing metadata from the JSON API response and builds SEC index page URLs
3. **Index Phase** — Visits each filing index page to extract the formatted filing date and document URL
4. **Alert Phase** — The Telegram pipeline sends a formatted message to your configured chat for every item yielded

---

## Notes

- Session cookies in the spider may expire — update them from your browser if requests start failing
- `download_delay = 0.2` is set to be polite to SEC servers
- Duplicate URLs are filtered by Scrapy's built-in deduplication (where `dont_filter=False`)
- Keep your `BOT_TOKEN` private — never commit it to version control

---

## License

For educational and personal use only. Ensure compliance with SEC's data usage policies and `robots.txt`.

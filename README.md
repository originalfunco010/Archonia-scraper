# Archonia Scraper

Python web scraper for [Archonia](https://www.archonia.com) Funko POP! items.  
Automatically sends alerts to Discord via webhooks when new items are found.

## Features

- Scrapes the latest Funko POP! products from Archonia.
- Maintains a local cache (`Archonia_cache.json`) to avoid duplicate alerts.
- Sends messages to Discord via webhooks.
- Webhooks stored securely in a `.env` file.
- Supports test and production webhooks via a toggle (`USE_TEST_WEBHOOK`).

## Setup

### Clone the repository:
- Open an terminal and execute:

```git clone git@github.com:originalfunco010/Archonia-scraper.git```  
```cd Archonia-scraper```

### Install dependencies:

- In the same terminal, execute:

```pip install beautifulsoup4 requests python-dotenv```

### Create a .env file
Create a .env file in the project folder:

```text
DISCORD_WEBHOOK_PROD=your_production_webhook  
DISCORD_WEBHOOK_TEST=your_test_webhook
```
Replace the placeholders with your actual Discord webhook URLs.  
.env is ignored by GitHub to keep secrets safe.

## Usage

- Open a terminal in the project folder (VS Code or other).
- Toggle between test or production in WebscraperArchonia.py:

```USE_TEST_WEBHOOK = True  # True = test, False = production```

- Run the scraper:

```python WebscrapeArchonia.py```

- New items will be sent to Discord.
- The cache (collectibles.json) is automatically updated.

## Folder Structure
```text
Archonias-scraper/
├─ Images/                       # Temporary images folder
├─ WebscraperArchonia.py         # scraper script
├─ Archonia_cache.json           # cache of found items
├─ .env                          # Discord webhooks (not on GitHub)
├─ .gitignore                    # ignores .env
├─ remove_png_files.sh           # Script to remove png and other image-files
└─ README.md                     # this file
```
## Testing

Set ```USE_TEST_WEBHOOK = True``` to send messages to a test Discord channel.  
Set ```USE_TEST_WEBHOOK = False``` to send messages to production.

## Notes

- All sensitive information (webhooks) should remain in .env.
- You can add multiple bots to the same repo by creating separate folders.
- Cache files can be committed to GitHub or kept local, depending on your preference.
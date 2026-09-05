# BelarusTripBot 🇧🇾

A Telegram bot that helps you plan a sightseeing trip around Belarus. Pick a region, browse attractions pulled live from **Wikipedia** with photos and descriptions, save the ones you like, and get a ready-to-open **Google Maps** route through them.

## Features

- **Region picker** — choose one of six Belarusian regions (Minsk, Grodno, Brest, Vitebsk, Mogilev, Gomel) from a keyboard menu
- **Attraction browser** — scroll through attractions for the chosen region one at a time with `<` / `>`, each shown with a photo and a short description
- **Live data from Wikipedia** — attraction lists, descriptions, and images are fetched on the fly via the Wikipedia Search and Page API, with a fallback search if the first query comes up empty
- **Route builder** — press `+` to add the current attraction to your personal route
- **Google Maps export** — `create route` turns your saved attractions into a multi-stop driving route link you can open straight in Google Maps

## Tech Stack

- Python
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) (`telebot`) for the Telegram bot interface
- `requests` for HTTP calls to the Wikipedia API
- [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page) (`action=query`, search + pageimages/extracts) for attraction data, descriptions, and images
- `urllib.parse.quote` to build Google Maps directions URLs

## Requirements

- Python 3.9+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

## Getting Started

1. Clone the repo:

   ```
   git clone https://github.com/dran1k-default/belarus-trip-bot.git
   cd belarus-trip-bot
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Add your bot token in `storage.py`:

   ```python
   token = "YOUR_TELEGRAM_BOT_TOKEN"
   ```

   > ⚠️ Don't commit your real token — consider moving it to an environment variable and adding `storage.py` (or a `.env` file) to `.gitignore` once your token is in place.

4. Run the bot:

   ```
   python main.py
   ```

5. Open a chat with your bot on Telegram and send `/start`.

## Project Structure

```
belarus-trip-bot/
├── main.py             # Bot entry point — handlers for /start, region picker, browsing, route building
├── data_fetcher.py      # Wikipedia API integration — attraction search, descriptions, image download
├── storage.py            # Bot token and in-memory per-chat state (region, places, route)
└── requirements.txt      # Python dependencies
```

## How It Works

1. `/start` greets the user and offers to create a new trip.
2. Choosing a region saves it and fetches a list of attractions for that region from Wikipedia (`get_attractions`).
3. `show_place` displays the current attraction with an image (`get_place_image` + `download_image_bytes`) and description, falling back to text-only if no image is available.
4. `<` / `>` cycle through attractions; `+` adds the current one to the route.
5. `create route` builds a Google Maps directions URL from all saved attractions and sends it to the user.




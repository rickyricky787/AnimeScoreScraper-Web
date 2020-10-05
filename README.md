# Anime Score Scraper (Web)
Scrapes anime scores from MyAnimeList, Anime Planet, and AniList using BeautifulSoup.
This is the web demo version of a previous project of the same name: https://github.com/rickyricky787/AnimeScoreScraper

## How to Use
Simply visit https://anime-scores.herokuapp.com/ , enter the anime, and view your results. Since web app uses Google Custom Search API, so it is limited to around 30 queries per day.

If you would like to clone and test locally using your own Google API keys:
- Install any missing modules
- Create a .env file with API_KEY = (your Custom Search API key) and SEARCH_ENGINE_ID = (your Search Engine Key)
- Remove . from imports

If you would like to clone and test locally without using Google API keys (not recommended):
- Install any missing modules
- Replace any instance of googleThis() with scrapeGoogle().
- Remove . from imports
- NOTE: Google might set up a captcha after multiple queries, causing the scraper to fail.

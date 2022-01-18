import requests
from .settings import *


# Finds the link of the anime webpage using Google Custom Search API
def googleThis(name, keyword, website):
    API_KEY, SEARCH_ENGINE_ID = getKeys()
    # Query will look like something like "One Piece AniList"
    query = name + " " + keyword
    return googleThisHelper(query, website, API_KEY, SEARCH_ENGINE_ID)

def googleThisHelper(query, website, API_KEY, SEARCH_ENGINE_ID):
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start=1"
    data = requests.get(url).json()
    results = data.get("items")

    if results != None:
        # We will first check if there is suggested query that Google provides
        # If there is, we redo this function again with said query
        if data.get("spelling") != None:
            corrected_query = data.get("spelling").get("correctedQuery")
            return googleThisHelper(corrected_query, website, API_KEY, SEARCH_ENGINE_ID)
        else:
            # We will (hopefully) find the correct link from the links within the first Google search page
            # The first link the right website (ex. myanimelist.com/anime) will be returned
            for items in results:
                link = items.get("link")
                if website in link:
                    return link

    return "None"

# Finds the link of the anime webpage by scraping Google's search results
def scrapeGoogle(name, keyword, website):

    # Function will "google" the anime name, followed by the keyword (ex. Pokemon + MyAnimeList).
    search = name + " " + keyword
    page = requests.get("https://www.google.com/search?q={}&num={}".format(search, 5))
    soup = BeautifulSoup(page.content, "html5lib")
    links = soup.findAll("a")
 
    # We will (hopefully) return the correct link within those 5 first searches
    for link in links :
        link_href = link.get("href")
        # If not an image (imgurl) or a snippet (?sa=X), add link to array
        if website in link_href and not "imgurl" in link_href and not "?sa=X" in link_href:
            return link.get("href").split("?q=")[1].split("&sa=U")[0]

    return "None"
# Anime Ranking Search using BeautifulSoup
# Author: Ricky Rodriguez

import requests
from bs4 import BeautifulSoup
import re
import time
from .settings import *

# A class that will contain all the data we are looking for; used by functions
class Data:
    def __init__(self, webpage="None"):
        self.title = "None"
        self.score = "0.0"
        self.conv_score = "0.0"
        self.votes = "0.0"
        self.link = webpage
        self.image = "None"

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


# Function that turns all numbers within data class to a string 
def numToString(anime):
    anime.score = str(anime.score)
    anime.conv_score = str(anime.conv_score)
    anime.votes = str(anime.votes)

# Returns the MyAnimeList link of the anime queried
def MyAnimeListLink(name):
    link = googleThis(name, "MyAnimeList", "myanimelist.net/anime")
    return link

# Retrieves data scraped from MyAnimeList
def MyAnimeListData(link):
    results = Data(link)
    # If no link was returned from googleThis(), then anime webpage not found
    if results.link != "None":
        page = requests.get(results.link)
        soup = BeautifulSoup(page.content, "html5lib")

        # If there is no "fl-l.score", then link is incorrect / anime webpage not found
        element_check = soup.select_one("div.fl-l.score")
        if element_check is not None:
            container = element_check
            results.score = container.get_text()
            results.score = results.score.strip()

            # An upcoming anime has an "N/A" rating
            if results.score != "N/A":
                results.score = float(results.score)
                results.conv_score = float('%.2f'%(results.score * 10))
            else:
                results.score = "N/A"
                results.conv_score = "N/A"

            container = soup.find("span", {"itemprop":"ratingCount"})
            if container is not None:
                results.votes = container.get_text()
                results.votes = str(results.votes)
            else:
                results.votes = "N/A"

            results.title = soup.find("h1", {"class":"title-name"})
            results.title = (results.title).get_text()
            
            results.image = soup.find("img", {"itemprop":"image"})
            results.image = str(results.image)
            results.image = results.image.split('data-src="')[1].split('" ')[0]

    numToString(results)
    time.sleep(1)
    return results

# Returns the AnimePlanet link of the anime queried
def AnimePlanetLink(name):
    link = googleThis(name, "Anime Planet", "anime-planet.com/anime")
    return link

# Retrieves the data scraped from AnimePlanet
def AnimePlanetData(link):
    results = Data(link)
    
    if results.link != "None":
        # If link has /videos on them, just remove it
        results.link = (results.link).replace("/videos", "")

        page = requests.get(results.link)
        soup = BeautifulSoup(page.content, "html5lib")
        element_check = soup.select_one("div.avgRating")
        if element_check is not None:
            container = element_check
            results.score = container.get_text()

            # Upcoming anime
            if "needed to calculate" in results.score:
                results.score = "N/A"
                results.conv_score = "N/A"
            else:
                results.score = results.score.split(' out')[0]
                results.conv_score = str('%.2f'%(100 * (float(results.score) / 5)))
            
            container = soup.select_one("div.avgRating")
            if container is not None:
                container = container.get_text()
                if not "needed to calculate" in container:
                    container = container.split('from ')[1].split(' votes')[0]
                    results.votes = container.replace(',', '')
                # Upcoming anime
                else:
                    results.votes = "N/A"

            results.title = soup.find("h1", {"itemprop":"name"})
            results.title = results.title.get_text()
            results.image = soup.find("img", {"class":"screenshots"})
            results.image = str(results.image)
            results.image = results.image.split('src="')[1].split('?t=')[0]
            results.image = "https://www.anime-planet.com" + results.image

    numToString(results)
    time.sleep(1)
    return results

# Returns the AniList link of the anime queried
def AniListLink(name):
    link = googleThis(name, "AniList", "anilist.co/anime")
    return link

# Retrieves the data scraped from AniList
def AniListData(link):
    results = Data(link)
    if results.link != "None":
        page = requests.get(results.link)
        soup = BeautifulSoup(page.content, "html5lib")
        element_check = soup.find("script", {"type":"application/ld+json"})
        if element_check is not None:
            container = str(element_check)
            if "ratingValue" in container and "ratingCount" in container:
                results.score = container.split('ratingValue":')[1].split(',')[0]
                results.conv_score = results.score
                results.votes = container.split('ratingCount":')[1].split(',')[0]
            else:
                # If "ratingValue" and "ratingCount" not found, then it could be a upcoming anime
                results.score = "N/A"
                results.conv_score = "N/A"
                results.votes = "N/A"

            results.title = soup.find("title", {"data-vue-meta":"true"})
            results.title = results.title.get_text()
            results.title = results.title.split(" · AniList")[0]
            results.image = soup.find("img", {"class":"cover"})
            results.image = str(results.image)
            results.image = results.image.split('src="')[1].split('"/>')[0]

    numToString(results)
    time.sleep(1)
    return results
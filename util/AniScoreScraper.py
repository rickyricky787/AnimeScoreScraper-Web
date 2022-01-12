# Anime Ranking Search using BeautifulSoup
# Author: Ricky Rodriguez

import requests
from bs4 import BeautifulSoup
import re
import time
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

# A class that will contain all the data we are looking for; used by functions
class AnimeData:
    def __init__(self, webpage="None"):
        self.title = "None"
        self.score = "0.0"
        self.conv_score = "0.0"
        self.votes = "0.0"
        self.link = webpage
        self.image = "None"

class MyAnimeListData(AnimeData):
    def __init__(self, anime_name):
        link = googleThis(anime_name, "MyAnimeList", "myanimelist.net/anime")
        super().__init__(link)
        self.site_name = "MyAnimeList"
    
    def scrape_data(self):
        # If no link was returned from googleThis(), then anime webpage not found
        if self.link != "None":
            page = requests.get(self.link)
            soup = BeautifulSoup(page.content, "html5lib")

            # If there is no "fl-l.score", then link is incorrect / anime webpage not found
            element_check = soup.select_one("div.fl-l.score")
            if element_check is not None:
                container = element_check
                self.score = container.get_text()
                self.score = self.score.strip()

                # An upcoming anime has an "N/A" rating
                if self.score != "N/A":
                    self.score = float(self.score)
                    self.conv_score = float('%.2f'%(self.score * 10))
                else:
                    self.score = "N/A"
                    self.conv_score = "N/A"

                container = soup.find("span", {"itemprop":"ratingCount"})
                if container is not None:
                    self.votes = container.get_text()
                    self.votes = str(self.votes)
                else:
                    self.votes = "N/A"

                self.title = soup.find("h1", {"class":"title-name"})
                self.title = (self.title).get_text()
                
                self.image = soup.find("img", {"itemprop":"image"})
                self.image = str(self.image)
                self.image = self.image.split('data-src="')[1].split('" ')[0]

        # Converting numbers to strings
        self.score = str(self.score)
        self.conv_score = str(self.conv_score)
        self.votes = str(self.votes)

        time.sleep(1)

class AnimePlanetData(AnimeData):
    def __init__(self, anime_name):
        link = googleThis(anime_name, "Anime Planet", "anime-planet.com/anime")
        super().__init__(link)
        self.site_name = "Anime Planet"
    
    def scrape_data(self):
        if self.link != "None":
            # If link has /videos on them, just remove it
            self.link = (self.link).replace("/videos", "")

            page = requests.get(self.link)
            soup = BeautifulSoup(page.content, "html5lib")
            element_check = soup.select_one("div.avgRating")
            if element_check is not None:
                container = element_check
                self.score = container.get_text()

                # Upcoming anime
                if "needed to calculate" in self.score:
                    self.score = "N/A"
                    self.conv_score = "N/A"
                else:
                    self.score = self.score.split(' out')[0]
                    self.conv_score = str('%.2f'%(100 * (float(self.score) / 5)))
                
                container = soup.select_one("div.avgRating")
                if container is not None:
                    container = container.get_text()
                    if not "needed to calculate" in container:
                        container = container.split('from ')[1].split(' votes')[0]
                        self.votes = container.replace(',', '')
                    # Upcoming anime
                    else:
                        self.votes = "N/A"

                self.title = soup.find("h1", {"itemprop":"name"})
                self.title = self.title.get_text()
                self.image = soup.find("img", {"class":"screenshots"})
                self.image = str(self.image)
                self.image = self.image.split('src="')[1].split('?t=')[0]
                self.image = "https://www.anime-planet.com" + self.image

        # Converting numbers to strings
        self.score = str(self.score)
        self.conv_score = str(self.conv_score)
        self.votes = str(self.votes)

        time.sleep(1)

class AniListData(AnimeData):
    def __init__(self, anime_name):
        link = googleThis(anime_name, "AniList", "anilist.co/anime")
        super().__init__(link)
        self.site_name = "AniList"
    
    def scrape_data(self):
        if self.link != "None":
            page = requests.get(self.link)
            soup = BeautifulSoup(page.content, "html5lib")
            element_check = soup.find("script", {"type":"application/ld+json"})
            if element_check is not None:
                container = str(element_check)
                if "ratingValue" in container and "ratingCount" in container:
                    self.score = container.split('ratingValue":')[1].split(',')[0]
                    self.conv_score = self.score
                    self.votes = container.split('ratingCount":')[1].split(',')[0]
                else:
                    # If "ratingValue" and "ratingCount" not found, then it could be a upcoming anime
                    self.score = "N/A"
                    self.conv_score = "N/A"
                    self.votes = "N/A"

                self.title = soup.find("title", {"data-vue-meta":"true"})
                self.title = self.title.get_text()
                self.title = self.title.split(" · AniList")[0]
                self.image = soup.find("img", {"class":"cover"})
                self.image = str(self.image)
                self.image = self.image.split('src="')[1].split('"/>')[0]

        # Converting numbers to strings
        self.score = str(self.score)
        self.conv_score = str(self.conv_score)
        self.votes = str(self.votes)

        time.sleep(1)



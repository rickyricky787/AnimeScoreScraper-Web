# Anime Ranking Search using BeautifulSoup
# Author: Ricky Rodriguez

import requests
from bs4 import BeautifulSoup
import re
import time

# A class that will contain all the data we are looking for; used by functions
class Data:
    def __int__(self):
        self.title = "None"
        self.score = "0.0"
        self.conv_score = "0.0"
        self.votes = "0.0"
        self.link = "None"
        self.image = "None"


# Def: Finds the link of the anime webpage in a website (MyAnimeList, Anime Planet, Anilist)
# Input: User inputed "name", "keyword" and "website" of the webpage we plan on scraping
# Output: The link of the anime webpage (if found), "None" (if not found)

def findLink(name, keyword, website):

    # Function will "google" the anime name, followed by the keyword (ex. Pokemon + MyAnimeList).
    search = name + " " + keyword
    page = requests.get("https://www.google.com/search?q={}&num={}".format(search, 5))
    soup = BeautifulSoup(page.content, "html5lib")
    links = soup.findAll("a")
 
    # "links" has first 5 websites found from Google
    # "search_results" will (hopefully) have the link we want
    search_results = "None"

    for link in links :
        link_href = link.get("href")
        # If not an image (imgurl) or a snippet (?sa=X), add link to array
        if website in link_href and not "imgurl" in link_href and not "?sa=X" in link_href:
            search_results = link.get("href").split("?q=")[1].split("&sa=U")[0]
            break

    time.sleep(1)
    return search_results


# Function that turns all numbers within data class to a string 
def numToString(anime):
    anime.score = str(anime.score)
    anime.conv_score = str(anime.conv_score)
    anime.votes = str(anime.votes)

# To get data from MyAnimeList
def MyAnimeList(name):
    results = Data()
    results.link = findLink(name, "MyAnimeList", "myanimelist.net/anime")

    # If no link was returned from findLink(), then anime webpage not found
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

            results.title = soup.find("span", {"itemprop":"name"})

            # To remove alternate title (just return the main one)
            title_string = str(results.title)
            if "<br/>" in title_string:
                results.title = title_string.split('itemprop="name">')[1].split('<br/>')[0]
            else:
                results.title = results.title.get_text()

            results.image = soup.find("img", {"itemprop":"image"})
            results.image = str(results.image)
            results.image = results.image.split('data-src="')[1].split('" ')[0]

    numToString(results)
    time.sleep(1)
    return results

# To get data from AnimePlanet
def AnimePlanet(name):
    results = Data()
    results.link = findLink(name, "Anime Planet", "anime-planet.com/anime")

    # If link has /videos on them, just remove it
    results.link = (results.link).replace("/videos", "")
    
    if results.link != "None":
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
                results.conv_score = container.span["style"]
                results.conv_score = results.conv_score[7:-1]
            
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

#To get data from AniList
def AniList(name):
    results = Data()
    results.link = findLink(name, "AniList", "anilist.co/anime")
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
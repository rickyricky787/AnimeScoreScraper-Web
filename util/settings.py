import os
from dotenv import load_dotenv, find_dotenv

# To get keys from .env files
def getKeys():
    load_dotenv(find_dotenv())

    API_KEY = os.environ.get("API_KEY")
    SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

    return API_KEY, SEARCH_ENGINE_ID
from flask import Flask, redirect, url_for, render_template, request
from util.AniScoreScraper import MyAnimeListData, AnimePlanetData, AniListData


app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/results", methods=["POST"])
def results():
    anime_name = request.form["anime_query"]
    if anime_name != "":
        site1_data = MyAnimeListData(anime_name)
        site2_data = AnimePlanetData(anime_name)
        site3_data = AniListData(anime_name)

        site_data = [site1_data, site2_data, site3_data]

        for site in site_data:
            site.scrape_data()

        return render_template(
            "results.html",
            site_data=site_data
            )
    else:
        render_template("index.html")

if __name__ == "__main__":
    app.run()
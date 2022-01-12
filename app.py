from flask import Flask, redirect, url_for, render_template, request
from flask_caching import Cache
from util.AniScoreScraper import MyAnimeListData, AnimePlanetData, AniListData

cache = Cache()

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
cache.init_app(app)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        query = request.form["nm"]
        return redirect(url_for("results", anime_name=query))
    else:
        return render_template("index.html")

@app.route("/<anime_name>", methods=["GET", "POST"])
@cache.cached(timeout=120)
def results(anime_name):
    site1_data = MyAnimeListData(anime_name)
    site2_data = AnimePlanetData(anime_name)
    site3_data = AniListData(anime_name)

    site_data = [site1_data, site2_data, site3_data]

    for site in site_data:
        site.scrape_data()

    if request.method == "POST":
        query = request.form["nm"]
        return redirect(url_for("results", anime_name=query))
    else:
        return render_template(
            "results.html", 
            title=anime_name, 
            site_data=site_data
            )

if __name__ == "__main__":
    app.run()
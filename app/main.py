from flask import Flask, redirect, url_for, render_template, request
from animescorescraper import MyAnimeList, AnimePlanet, AniList

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        query = request.form["nm"]
        return redirect(url_for("results", qry=query))
    else:
        return render_template("home.html")

@app.route("/<qry>")
def results(qry):
    search1 = MyAnimeList(qry)
    search2 = AnimePlanet(qry)
    search3 = AniList(qry)
    if request.method == "POST":
        query = request.form["nm"]
        return redirect(url_for("results", qry=query))
    else:
        return render_template("results.html", title=qry, anime1=search1, anime2=search2, anime3=search3)
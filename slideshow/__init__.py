import os
from flask import Flask, render_template, jsonify
from .database import database, Post

app = Flask(__name__)
app.config["DATABASE"] = os.getenv("SLIDESHOW_DB", "slideshow.sqlite")


@app.before_first_request
def init_db():
    database.init(app.config["DATABASE"])
    database.create_tables([Post], safe=True)


@app.route("/")
def client():
    return render_template("index.html")


@app.route("/beamer")
def beamer():
    return render_template("beamer.html")


@app.route("/posts", methods=["POST"])
def add_post():
    return "OK"


@app.route("/posts", methods=["GET"])
def get_posts():
    posts = list(Post.select().dicts())
    return jsonify(posts=posts)

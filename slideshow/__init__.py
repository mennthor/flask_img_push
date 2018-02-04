import os
from flask import Flask, render_template, jsonify, request
from .database import database, Post
from datetime import datetime

app = Flask(__name__)
app.config["DATABASE"] = os.getenv("SLIDESHOW_DB", "slideshow.sqlite")
app.config["IMG_DIR"] = os.getenv(
    "SLIDESHOW_IMG_DIR", os.path.join(os.getenv("HOME"), "Pictures", "wedding")
)


@app.before_first_request
def init_db():
    os.makedirs(app.config["IMG_DIR"], exist_ok=True)
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
    post = Post()
    post.timestamp = datetime.utcnow()
    post.comment = request.form["comment"]
    ext = os.path.splitext(request.files["image"].filename)[1]
    filename = post.timestamp.isoformat() + ext

    filename = filename.replace(":", "_")
    request.files["image"].save(os.path.join(app.config["IMG_DIR"], filename))
    post.name = filename
    post.save()
    return jsonify(status="OK")


@app.route("/posts", methods=["GET"])
def get_posts():
    posts = list(Post.select().dicts())
    return jsonify(posts=posts)

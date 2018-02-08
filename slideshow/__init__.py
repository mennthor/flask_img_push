import os
from flask import Flask, render_template, jsonify, request, send_from_directory
from datetime import datetime

from .database import database, Post
from .image import resize

app = Flask(__name__)
app.config["DATABASE"] = os.getenv("SLIDESHOW_DB", "slideshow.sqlite")
app.config["IMG_DIR"] = os.getenv(
    "SLIDESHOW_IMG_DIR", os.path.join(os.getenv("HOME"), "Pictures", "wedding")
)


@app.before_first_request
def init_db():
    os.makedirs(app.config["IMG_DIR"], exist_ok=True)
    os.makedirs(os.path.join(app.config["IMG_DIR"], 'original'), exist_ok=True)
    os.makedirs(os.path.join(app.config["IMG_DIR"], 'small'), exist_ok=True)

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
    filename = post.timestamp.isoformat().replace(":", "_") + ext

    original_path = os.path.join(app.config["IMG_DIR"], 'original', filename)
    small_path = os.path.join(app.config["IMG_DIR"], 'small', filename)

    request.files["image"].save(original_path)
    resize(original_path, small_path)

    post.name = filename
    post.save()
    return jsonify(status="OK")


@app.route("/posts", methods=["GET"])
def get_posts():
    posts = list(Post.select().dicts())
    return jsonify(posts=posts)


@app.route('/images/small/<name>')
def small(name):
    return send_from_directory(
        os.path.join(app.config['IMG_DIR'], 'small'), name
    )


@app.route('/images/original/<name>')
def original(name):
    return send_from_directory(
        os.path.join(app.config['IMG_DIR'], 'original'), name
    )


import os
from flask import Flask, render_template, jsonify, request, send_from_directory
from datetime import datetime

from .database import database, Post
from .image import resize


# Get config from env vars
app = Flask(__name__)
app.config["DATABASE"] = os.getenv("SLIDESHOW_DB", "slideshow.sqlite")
app.config["IMG_DIR"] = os.getenv(
    "SLIDESHOW_IMG_DIR", os.path.join(os.getenv("HOME"), "Pictures", "wedding")
)


# Init on launch
@app.before_first_request
def init_app():
    # Images are saved as posted and cropped with fixed ratios later
    os.makedirs(os.path.join(app.config["IMG_DIR"], 'original'), exist_ok=True)
    os.makedirs(os.path.join(app.config["IMG_DIR"], 'small'), exist_ok=True)
    os.makedirs(os.path.join(app.config["IMG_DIR"], 'large'), exist_ok=True)
    # Setup database
    database.init(app.config["DATABASE"])
    database.create_tables([Post], safe=True)


# These are the public interfaces sites
@app.route("/")
def client():
    """ Client site, for sending pictures and comments """
    return render_template("client.html")


@app.route("/gallery")
def gallery():
    """ Gallery site, for displaying sent pictures and comments """
    return render_template("gallery.html")


# Receiver site to post new images and comments to and get DB info from
@app.route("/posts", methods=["POST"])
def add_post():
    # Fill post db entry
    post = Post()
    post.timestamp = datetime.utcnow()
    post.comment = request.form["comment"]

    # Get image from form, resize and save
    img_file = request.files["image"]
    img_resized = resize(img_file)

    ext = os.path.splitext(request.files["image"].filename)[1]
    filename = post.timestamp.isoformat().replace(":", "_") + ext
    img_path = os.path.join(app.config["IMG_DIR"], filename)
    img_resized.save(img_path)

    # Save image filename in post db and finalize
    post.name = filename
    post.save()
    return jsonify(status="OK")


@app.route("/posts", methods=["GET"])
def get_posts():
    posts = list(Post.select().dicts())
    return jsonify(posts=posts)


# Hosted images from database, acces by full filename
@app.route('/images/<name>')
def img_host(name):
    return send_from_directory(app.config['IMG_DIR'], name)

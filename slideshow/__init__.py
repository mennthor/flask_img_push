# coding: utf-8

from __future__ import print_function
import os
import sys
from flask import (Flask, render_template, jsonify, request,
                   send_from_directory, redirect, url_for, flash)
from datetime import datetime
import numpy as np

from .database import database, Post
from .image import fix_orientation


# #######################################################################
# TODO:
# 1. Use flask socket-io to push new pictures to gallery instead of reload
# 2. Backup files on DB clear
# #######################################################################


# Get config from env vars
app = Flask(__name__)
app.secret_key = "DONTTELLANYONETHESECRETKEY"
app.config["DATABASE"] = os.getenv("SLIDESHOW_DB", "slideshow.sqlite")
app.config["IMG_DIR"] = os.getenv(
    "SLIDESHOW_IMG_DIR", os.path.join(os.getenv("HOME"), "Pictures", "wedding")
)


def get_max_id():
    """ Get max id from database """
    try:
        max_id = np.amax([msi.id for msi in Post.select()])
    except Exception:
        max_id = None
    return max_id


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
    return render_template("client.html", error=request.args.get("error"))


@app.route("/gallery")
def gallery():
    """ Gallery site, for displaying sent pictures and comments """
    # Fetch 5 images from database
    URL = "http://127.0.0.1:5000/images/"
    max_id = get_max_id()

    if max_id is not None:
        if max_id < 5:
            # Need to show with replacement because too few images
            ids = np.random.choice(np.arange(1, max_id + 1),
                                   replace=True, size=5)
            # These are returned unique so we have to rebroadcast them again
            filenames = [msi.name for msi in
                         Post.select().where(Post.id << ids.tolist())]
            # Build a mapping from ids to [0, 1, 2, ...]
            n_ids = len(filenames)
            assert n_ids == len(np.unique(ids))
            id_map = {i: _id for i, _id in zip(np.unique(ids),
                                               np.arange(n_ids))}
            _ids = np.array([id_map[i] for i in ids])
            filenames = np.array(filenames)[_ids]
        else:
            ids = np.random.choice(np.arange(1, max_id + 1),
                                   replace=False, size=5).tolist()
            # Fetch names from db and pass to template
            filenames = [msi.name for msi in
                         Post.select().where(Post.id << ids)]

        # Prepend URL to use in img tab in template
        filenames = {i: URL + s for i, s
                     in enumerate(filenames)}
    else:
        # No imgs added yet or eror, only show placeholder
        filenames = 5 * [URL + "_placeholder_.jpg"]

    return render_template("gallery.html", filenames=filenames)


# Receiver site to post new images and comments to and get DB info from
@app.route("/posts", methods=["POST"])
def add_post():
    # Fill post db entry
    try:
        post = Post()
        post.timestamp = datetime.utcnow()
        post.comment = request.form["comment"]

        # Get image from form, resize and save
        img_file = request.files["image"]
        # img_resized = resize(img_file)
        img_resized = fix_orientation(img_file)

        ext = os.path.splitext(request.files["image"].filename)[1]
        filename = post.timestamp.isoformat().replace(":", "_") + ext
        img_path = os.path.join(app.config["IMG_DIR"], filename)
        img_resized.save(img_path)

        # Save image filename in post db and finalize
        post.name = filename
        post.save()
        msg = "Successfully sent image :)"
    except Exception as e:
        msg = e

    flash(msg)
    return redirect(url_for("client"))


@app.route("/posts", methods=["GET"])
def get_posts():
    posts = list(Post.select().dicts())
    return jsonify(posts=posts)


# Hosted images from database, access by full filename
@app.route("/images/<name>")
def img_host(name):
    return send_from_directory(app.config['IMG_DIR'], name)


# Clear database site
@app.route("/database_clear")
def db_clear():
    max_id = get_max_id()
    if max_id is not None:
        del_query = (Post.delete()
                     .where(Post.id << np.arange(1, max_id + 1).tolist()))
        try:
            rows_del = del_query.execute()
            msg = "Deleted {} rows. DB is now empty.".format(rows_del)
            success = True
        except Exception as e:
            msg = e
            success = False
    else:
        msg = "DB was already empty, did nothing."
        success = True

    return render_template("clear_db.html", success=success, msg=msg)


# Show database content
@app.route("/database_show")
def db_show():
    query = Post.select()
    s = "<h1> Database dump: </h1>"
    for item in query:
        s += "{}: {}".format(item.id, item.name) + "<br>"

    return s

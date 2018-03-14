# coding: utf-8

from __future__ import print_function
import os
import sys
import threading
from flask import (Flask, render_template, jsonify, request,
                   send_from_directory, redirect, url_for, flash)
from flask_socketio import SocketIO
from datetime import datetime
import numpy as np

from .database import database, Post, get_rnd_db_entries, get_max_id
from .image import fix_orientation


app = Flask(__name__)
app.secret_key = "DONTTELLANYONETHESECRETKEY"
app.config["DATABASE"] = os.getenv("SLIDESHOW_DB", "slideshow.sqlite")
app.config["IMG_DIR"] = os.getenv("SLIDESHOW_IMG_DIR",
                                  os.path.join(os.getenv("HOME"),
                                               "Pictures", "wedding"))


# Init app before launch
@app.before_first_request
def init_app():
    # Images are saved as posted and cropped with fixed ratios later
    os.makedirs(os.path.join(app.config["IMG_DIR"], 'original'), exist_ok=True)
    os.makedirs(os.path.join(app.config["IMG_DIR"], 'small'), exist_ok=True)
    os.makedirs(os.path.join(app.config["IMG_DIR"], 'large'), exist_ok=True)
    # Setup database
    database.init(app.config["DATABASE"])
    database.create_tables([Post], safe=True)
    # Set the timer to push new random content to gallery
    start_gallery_updater()


def start_gallery_updater():
    """ A self starting thread to update the gallery each T seconds. """
    t = threading.Timer(15.0, start_gallery_updater)
    t.daemon = True
    t.start()
    print("Updated gallery", file=sys.stderr)
    filenames, _ = get_rnd_db_entries(N=4)
    URL = "http://127.0.0.1:5000/images/"
    filenames = {i: URL + s for i, s in enumerate(filenames)}
    socket.emit("update", {"img_tl": filenames[0],
                           "img_bl": filenames[1],
                           "img_tr": filenames[2],
                           "img_br": filenames[3],
                           })


# Init flask SocketIO
socket = SocketIO()
socket.init_app(app)


# Client mobile page
@app.route("/")
def client():
    """ Client site, for sending pictures and comments """
    return render_template("client.html", error=request.args.get("error"))


# Passive image gallery
@app.route("/gallery")
def gallery():
    """ Gallery site, for displaying sent pictures and comments """
    # Fetch 5 images from database
    filenames, comments = get_rnd_db_entries(N=5)
    URL = "http://127.0.0.1:5000/images/"
    filenames = {i: URL + s for i, s in enumerate(filenames)}
    return render_template("gallery.html", filenames=filenames,
                           comment=comments[2])


# Receiver site to post new images and comments to and get DB info from
@app.route("/posts", methods=["POST"])
def add_post():
    # Fill post db entry
    URL = "http://127.0.0.1:5000/images/"
    try:
        post = Post()
        post.timestamp = datetime.utcnow()
        comment = request.form["comment"]
        post.comment = comment

        # Get image from form, resize and save
        img_file = request.files["image"]
        img_resized = fix_orientation(img_file)

        ext = os.path.splitext(request.files["image"].filename)[1]
        filename = post.timestamp.isoformat().replace(":", "_") + ext
        img_path = os.path.join(app.config["IMG_DIR"], filename)
        img_resized.save(img_path)

        # Save image filename in post db and finalize
        post.name = filename
        post.save()
        msg = "Successfully sent image :)"

        socket.emit("new_image", {"filename": URL + filename,
                                  "comment": comment})
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


# DEBUG: Clear database site
@app.route("/database_clear")
def db_clear():
    max_id = get_max_id()
    if max_id is not None:
        del_query = (Post.delete()
                     # .where(Post.id == max_id))
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


# DEBUG: Show database content
@app.route("/database_show")
def db_show():
    query = Post.select()
    s = "<h1> Database dump: </h1>"
    for item in query:
        s += "{}: {}".format(item.id, item.name) + "<br>"

    return s


# DEBUG to test socket io
# @app.route("/sender", methods=["GET", "POST"])
# def sender():
#     if request.method == "POST":
#         txt = request.form["msg"]
#         socket.emit("to_receiver", {"parameter": txt})
#         return redirect(url_for("sender"))

#     msg = request.args.get("message", "no msg yet...")
#     return render_template("sender.html", message=msg)


# @app.route("/receiver", methods=["GET"])
# def receiver():
#     return render_template("receiver.html")


# Start the server wrapper
def start_server():
    socket.run(app, host="0.0.0.0", debug=True)

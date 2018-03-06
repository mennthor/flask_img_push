# from .routes import start_server


import os
from flask import Flask
from flask_socketio import SocketIO

from .routes import main as main_blueprint
from .database import database, Post

app = Flask(__name__)
app.secret_key = "DONTTELLANYONETHESECRETKEY"
app.config["DATABASE"] = os.getenv("SLIDESHOW_DB", "slideshow.sqlite")
app.config["IMG_DIR"] = os.getenv("SLIDESHOW_IMG_DIR",
                                  os.path.join(os.getenv("HOME"),
                                               "Pictures", "wedding"))

app.register_blueprint(main_blueprint)


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


# Init flask SocketIO
socketio = SocketIO()
socketio.init_app(app)


# Start the server wrapper
def start_server():
    socketio.run(app, host="0.0.0.0", debug=True)

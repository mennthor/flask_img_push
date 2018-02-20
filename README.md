# flask_img_push

Flask app which enables users to push images from their phones to a single gallery page running on a beamer.

1. Create a new python 3 virtual environment and `pip install -r requirements.txt`.
2. `chmod +x start_flask.sh` and `./start_flask.sh` to start the debug server at `localhost:5000`.
3. `localhost:5000` is the client page where you can push a photo to the gallery page.
4. `localhist:5000/gallery` is the gallery page where the pushed images are shown, supposed to be running only once on a beamer with a fixed page size.

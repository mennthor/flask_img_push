# flask_img_push

Flask app which enables users to push images from their phones to a single gallery page running on a beamer.  
Thanks to @bixel and @MaxNoe.

1. Create a new python 3 virtual environment and `pip install -r requirements.txt`.
2. `python start.py` to start the debug server at `localhost:5000`.
3. `localhost:5000` is the client page where you can push a photo to the gallery page.
4. `localhost:5000/gallery` is the gallery page where the pushed images are shown, supposed to be running only once on a beamer with a fixed page size.
5. Put a placeholder picture in `~/Pictures/wedding/_placeholder.jpg`, for an empty database.
6. Posted pictures are saved at `~/Pictures/wedding/` with a timestamp and at full resolution.
7. Center image container show the last posted image with its comment, if available. 4 surrounding image container show randomly picked images from the database - updated every 15 secs.
8. Posting images available if devices are in the same WiFi and directing to the server IP adress with port `5000`, also working without internet connection.
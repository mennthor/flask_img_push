"""
Helper method to handle images.
"""

from PIL import Image, ExifTags
import sys


def resize(in_file, long_edge=3000):
    """ Resize an uploaded image ``in_file`` and return a smaller version. """
    img = Image.open(in_file)

    if long_edge > max(img.width, img.height):
        return img

    # Find long edge and rescale
    ratio = img.width / img.height
    if ratio > 1:
        new_width = long_edge
        new_height = long_edge / ratio
    else:
        new_width = long_edge * ratio
        new_height = long_edge
    # Shrink using LANCZOS filter
    return img.resize((int(new_width), int(new_height)), Image.LANCZOS)


def crop_and_resize(in_file, ratio=None, long_edge=800):
    """
    Crop and resize image to desired ratio and long_edge len.
    We want to save a version that fits in a fixed width html container.
    If the ratio is almost identical to the target, then we crop a little to
    make it match to the grid. Otherwise (eg. portrait) is only resized so that
    the long_edge mathes the container height or width and the image is centered
    in the HTML template later.
    """
    return in_file


def fix_orientation(img_file):
    """
    iPhones capture landscape and write EXIF to rotate
    http://sylvana.net/jpegcrop/exif_orientation.html
    https://stackoverflow.com/questions/26697230/incorrect-image-rotation-in-img-tag
    """
    img = Image.open(img_file)
    exif = get_exif(img)
    if (exif is None) or ("Orientation" not in exif.keys()):
        """ Picture is probably OK by measuring the real pixels """
        return img
    else:
        orientation = int(exif["Orientation"])
        """ Cases 3, 6, 8 are rotated cases """
        if orientation == 3:
            img = img.rotate(180, expand=True)
        elif orientation == 6:
            img = img.rotate(-90, expand=True)
        elif orientation == 8:
            img = img.rotate(+90, expand=True)

    return img


def get_exif(img):
    """
    Returns an EXIF dict with string keys where possible.
    From: https://stackoverflow.com/questions/4764932/in-python-how-do-i-read-the-exif-data-for-an-image
    """
    exif = img._getexif()
    if isinstance(exif, dict):
        exif = {
            ExifTags.TAGS[k]: v
            for k, v in exif.items()
            if k in ExifTags.TAGS
            }
    else:
        exif = None
    return exif

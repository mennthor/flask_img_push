"""
Helper method to handle images.
"""

from PIL import Image


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

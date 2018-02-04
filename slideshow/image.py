from PIL import Image


def resize(input_path, output_path, long_edge=2000, enlarge=False):
    img = Image.open(input_path)

    if long_edge > max(img.width, img.height):
        return

    ratio = img.width / img.height

    if ratio > 1:
        new_width = long_edge
        new_height = long_edge / ratio
    else:
        new_width = long_edge * ratio
        new_height = long_edge

    small = img.resize((int(new_width), int(new_height)), Image.LANCZOS)

    small.save(output_path)

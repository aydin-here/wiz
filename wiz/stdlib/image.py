try:
    from PIL import Image

    PIL_AVAILABLE = True
except Exception:
    Image = None
    PIL_AVAILABLE = False

from errors import WizError


class ImageModule:

    def __init__(self):

        if not PIL_AVAILABLE:
            return

        self.functions = {
            "open": self.open,
            "create": self.create,
            "save": self.save,
            "resize": self.resize,
            "thumbnail": self.thumbnail,
            "crop": self.crop,
            "rotate": self.rotate,
            "flip": self.flip,
            "grayscale": self.grayscale,
            "invert": self.invert,
            "blur": self.blur,
            "size": self.size,
            "width": self.width,
            "height": self.height,
            "mode": self.mode,
            "format": self.format,
            "pixel": self.pixel,
            "paste": self.paste,
            "copy": self.copy,
            "to_list": self.to_list,
        }

    def _check(self):
        if not PIL_AVAILABLE or Image is None:
            raise WizError("The 'image' module requires Pillow.")

    def open(self, filename):
        self._check()
        return Image.open(filename)

    def create(self, width, height, color="white"):
        self._check()
        return Image.new("RGB", (int(width), int(height)), str(color))

    def save(self, image, filename):
        image.save(filename)
        return True

    def resize(self, image, width, height):
        return image.resize((int(width), int(height)))

    def thumbnail(self, image, width, height):
        copy = image.copy()
        copy.thumbnail((int(width), int(height)))
        return copy

    def crop(self, image, x1, y1, x2, y2):
        return image.crop((int(x1), int(y1), int(x2), int(y2)))

    def rotate(self, image, degrees):
        return image.rotate(int(degrees))

    def flip(self, image, direction="horizontal"):
        if str(direction) in ("horizontal", "x"):
            return image.transpose(Image.FLIP_LEFT_RIGHT)
        return image.transpose(Image.FLIP_TOP_BOTTOM)

    def grayscale(self, image):
        return image.convert("L")

    def invert(self, image):
        from PIL import ImageOps
        return ImageOps.invert(image.convert("RGB"))

    def blur(self, image, radius=2):
        from PIL import ImageFilter
        return image.filter(ImageFilter.GaussianBlur(int(radius)))

    def size(self, image):
        return {
            "width": image.width,
            "height": image.height,
        }

    def width(self, image):
        return image.width

    def height(self, image):
        return image.height

    def mode(self, image):
        return image.mode

    def format(self, image):
        return image.format

    def pixel(self, image, x, y):
        if "RGB" in image.mode:
            return list(image.getpixel((int(x), int(y))))
        return image.getpixel((int(x), int(y)))

    def paste(self, base, overlay, x=0, y=0):
        base.paste(overlay, (int(x), int(y)))
        return True

    def copy(self, image):
        return image.copy()

    def to_list(self, image):
        self._check()
        return list(image.convert("RGB").getdata())
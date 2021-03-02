import sys, os
from PIL import Image

for path in sys.argv[1:]:
    im = Image.open(path)
    output = ".".join(path.split(".")[:-1]) + ".jpg"
    im.convert('RGB').save(output, 'JPEG', quality=100)

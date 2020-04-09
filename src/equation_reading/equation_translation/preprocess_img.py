from PIL import Image  # pillow
import numpy as np
import png             # pypng
import sys


def reformat(fn, fn_out):
    grey = np.array(Image.open(fn).convert('L'))
    grey[grey>175] = 255
    grey_pil = Image.fromarray(grey)
    img = grey_pil.point(lambda x: int(x/17))
    #(w, h) = img.size
    png.fromarray(np.asarray(img, np.uint8),'L;4').save(fn_out)


if __name__ == "__main__":
    args = sys.argv
    reformat(args[1], args[2])

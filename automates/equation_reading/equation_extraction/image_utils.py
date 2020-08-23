import cv2
import numpy as np

def resize(imgs1, imgs2, num_channels):
    WHITE = [255 * num_channels]
    # Get the max heigh, width
    max_height = 0
    max_width = 0
    for i in range(len(imgs1)):
        height, width = imgs1[i].shape[:2]
        max_height = max(max_height, height)
        max_width = max(max_width, width)

        height, width = imgs2[i].shape[:2]
        max_height = max(max_height, height)
        max_width = max(max_width, width)
    # resize
    final1 = []
    final2 = []
    for i, img in enumerate(imgs1):
        height, width = img.shape[:2]
        h_diff_per_side = int((max_height - height) / 2)
        w_diff_per_side = int((max_width - width) / 2)
        img = cv2.copyMakeBorder(img, h_diff_per_side, h_diff_per_side, w_diff_per_side, w_diff_per_side,
                                 cv2.BORDER_CONSTANT, value=WHITE)
        # img = cv2.copyMakeBorder(img, 0, max_height - height, 0, max_width - width, cv2.BORDER_CONSTANT,
        #                           value=WHITE)
        final1.append(img)

        img2 = imgs2[i]
        height, width = img2.shape[:2]
        h_diff_per_side = int((max_height - height) / 2)
        w_diff_per_side = int((max_width - width) / 2)
        # img2 = cv2.copyMakeBorder(img2, 0, max_height - height, 0, max_width - width, cv2.BORDER_CONSTANT,
        #                           value=WHITE)
        img2 = cv2.copyMakeBorder(img2, h_diff_per_side, h_diff_per_side, w_diff_per_side, w_diff_per_side, cv2.BORDER_CONSTANT,
                                  value=WHITE)
        final2.append(img2)

    # return imgs1, imgs2, max_height, max_width
    return final1, final2, max_height, max_width

def pixel_is_white(pixel, threshold=255):
    for channel in pixel:
        if channel < threshold:
            return False
    return True

# Returns a 4-channel image, 4th channel is transparency
def remove_background(image, color):
    colors = {'blue':2, 'red':0}
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
    thresh = 254
    for row in image:
        for p in row:
            if pixel_is_white(p):
                p[3] = 0
            else: # change the color TODO: why does this work?
                p[0] = 0
                p[1] = 0
                p[2] = 0
                p[colors[color]] = 255
    return image

from skimage import io, morphology, util
from skimage.color import gray2rgb, rgb2gray
from skimage.filters import threshold_otsu
import argparse
import imgaug as ia
from imgaug import augmenters as iaa
import cv2
from PIL import Image
import numpy as np
# we expect to be given a grayscale image

def func_images_skeletonize(images, random_state, parents, hooks):
    results = []
    for img in images:
        # make it a binary image
        img = np.squeeze(img)
        thresh = threshold_otsu(img)
        inv_binary = img < thresh # inverts, because normally called with `>`
        inv_skeleton = morphology.skeletonize(inv_binary)
        # formatting
        skeleton = util.invert(inv_skeleton) * 255
        skeleton = np.expand_dims(skeleton, axis=2)
        skeleton = skeleton.astype(np.uint8)
        results.append(skeleton)
    return results


def func_images_closing(images, random_state, parents, hooks):
    results = []
    for img in images:
        inv = util.invert(img)
        inv_closed = morphology.closing(inv)
        closed = util.invert(inv_closed) #* 255
        results.append(closed)
    return results


def downsample_func(rescale_factor):
    def func_images_downsample(images, random_state, parents, hooks):
        results = []
        for img in images:
            img = np.squeeze(img)
            height, width = img.shape[:2]
            new_img = Image.fromarray(img)
            height = int(height * rescale_factor)
            width = int(width * rescale_factor)
            downsampled = new_img.resize((width, height), Image.LANCZOS)
            downsampled = np.array(downsampled)
            downsampled = np.expand_dims(downsampled, axis=2)
            results.append(downsampled)
        return results
    return func_images_downsample



def blur(img):
    mean = np.random.uniform(0, 0.1)
    std = np.random.uniform(0.05, 0.2)
    blur = iaa.GaussianBlur(sigma=(mean, std))
    mean_str = "{0:.2f}".format(mean)
    std_str = "{0:.3f}".format(std)
    return blur.augment_image(img), "blur{0}-{1}".format(mean_str, std_str)

def downsample(img):
    ratio = np.random.uniform(0.25, 0.75)
    downsample_aug = iaa.Lambda(func_images=downsample_func(ratio))
    ratio_str = "{0:.3f}".format(ratio)
    return downsample_aug.augment_image(img), "downsamp{0}".format(ratio_str)

def closing(img):
    closing_aug = iaa.Lambda(func_images=func_images_closing)
    return closing_aug.augment_image(img), "close"

def skeletonize(img):
    skeleton_aug = iaa.Lambda(func_images=func_images_skeletonize)
    return skeleton_aug.augment_image(img), "skel"

augmenters = [blur, downsample, closing, skeletonize]

def select_random_augmentation(img):
    f = np.random.choice(augmenters)
    return f(img)

if __name__ == '__main__':

    # TODO parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('image', help='image name')
    parser.add_argument('--pad-size', default=10)
    args = parser.parse_args()

    images = []
    original_img = io.imread(args.image)
    padded_img = util.pad(original_img, args.pad_size, 'constant', constant_values=255)
    images.append(padded_img)

    # iaa.GaussianBlur
    blur = iaa.GaussianBlur(sigma=(0, 1.0))
    blur_img = blur.augment_image(padded_img)
    images.append(blur_img)

    # downsample (PIL) LANCZOS
    downsample_aug = iaa.Lambda(func_images=downsample_func(0.5))
    downsampled = downsample_aug.augment_image(padded_img)
    images.append(downsampled)

    # downsample + stretch ???
    
    # morphology.closing ???
    closing_aug = iaa.Lambda(func_images=func_images_closing)
    closed = closing_aug.augment_image(padded_img)
    images.append(closed)

    # morphology.skeletonize
    skeleton_aug = iaa.Lambda(func_images=func_images_skeletonize)
    skeleton = skeleton_aug.augment_image(padded_img)
    images.append(skeleton)

    # display results
    images = [gray2rgb(img) for img in images]
    grid = ia.draw_grid(images, 4)
    ia.imshow(grid)

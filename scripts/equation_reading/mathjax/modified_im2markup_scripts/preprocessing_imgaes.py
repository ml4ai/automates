import sys, os, json, glob
import numpy as np
from PIL import Image

def main_parallel(l):
    filename, postfix, output_filename, crop_blank_default_size, pad_size, buckets, downsample_ratio = l
    postfix_length = len(postfix)
    status = crop_image(filename, output_filename, crop_blank_default_size)
    if not status:
        print('%s is blank, crop a white image of default size!'%filename)
    status = pad_group_image(output_filename, output_filename, pad_size, buckets)
    if not status:
        print('%s (after cropping and padding) is larger than the largest provided bucket size, left unchanged!'%filename)
    status = downsample_image(output_filename, output_filename, downsample_ratio)

def crop_image(img, output_path, default_size=None):
    old_im = Image.open(img).convert('L')
    img_data = np.asarray(old_im, dtype=np.uint8) # height, width
    nnz_inds = np.where(img_data!=255)
    if len(nnz_inds[0]) == 0:
        if not default_size:
            old_im.save(output_path)
            return False
        else:
            assert len(default_size) == 2, default_size
            x_min,y_min,x_max,y_max = 0,0,default_size[0],default_size[1]
            old_im = old_im.crop((x_min, y_min, x_max+1, y_max+1))
            old_im.save(output_path)
            return False
    y_min = np.min(nnz_inds[0])
    y_max = np.max(nnz_inds[0])
    x_min = np.min(nnz_inds[1])
    x_max = np.max(nnz_inds[1])
    old_im = old_im.crop((x_min, y_min, x_max+1, y_max+1))
    old_im.save(output_path)
    return True

def pad_group_image(img, output_path, pad_size, buckets):
    PAD_TOP, PAD_LEFT, PAD_BOTTOM, PAD_RIGHT = pad_size
    old_im = Image.open(img)
    old_size = (old_im.size[0]+PAD_LEFT+PAD_RIGHT, old_im.size[1]+PAD_TOP+PAD_BOTTOM)
    j = -1
    for i in range(len(buckets)):
        if old_size[0]<=buckets[i][0] and old_size[1]<=buckets[i][1]:
            j = i
            break
    if j < 0:
        new_size = old_size
        new_im = Image.new("RGB", new_size, (255,255,255))
        new_im.paste(old_im, (PAD_LEFT,PAD_TOP))
        new_im.save(output_path)
        return False
    new_size = buckets[j]
    new_im = Image.new("RGB", new_size, (255,255,255))
    new_im.paste(old_im, (PAD_LEFT,PAD_TOP))
    new_im.save(output_path)
    return True

def downsample_image(img, output_path, ratio):
    assert ratio>=1, ratio
    if ratio == 1:
        return True
    old_im = Image.open(img)
    old_size = old_im.size
    new_size = (int(old_size[0]/ratio), int(old_size[1]/ratio))

    new_im = old_im.resize(new_size, PIL.Image.LANCZOS)
    new_im.save(output_path)
    return True


def main(args):

    output_dir = '/home/gauravs/Automates/temp/Learn_git/cropped_eqn69.png'
    input_dir = '/projects/temporary/automates/er/gaurav/2014/1401/latex_images/1401.3339/Large_eqns/eqn69.png0001-1.png'
    postfix = '.png'
    crop_blank_default_size = '[600,60]'
    pad_size = '[8,8,8,8]'
    buckets = '[[240, 100], [320, 80], [400, 80], [400, 100], [480, 80], [480, 100], [560, 80], [560, 100], [640, 80], [640, 100], [720, 80], [720, 100], [720, 120], [720, 200], [800, 100], [800, 320], [1000, 200], [1000, 400], [1200, 200], [1600, 200], [1600, 1600]]'
    downsample_ratio = 2.
    filenames = input_dir
    main_parallel(filename, postfix, output_dir, crop_blank_default_size, pad_size, buckets, downsample_ratio)

if __name__ == '__main__':
    main(sys.argv[1:])
    print(' ')
    print('completed!')

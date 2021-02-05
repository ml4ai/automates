#!/usr/bin/env python
# Preprocess images for ease of training
import sys, os, argparse, json, glob, logging, PIL, multiprocessing
import numpy as np

from datetime import datetime
from PIL import Image
sys.path.insert(0, '%s'%os.path.join(os.path.dirname(__file__), '../utils/'))
from image_utils import *
from multiprocessing import Pool, Lock

# Printing starting time
print(' ')
start_time = datetime.now()
print('Starting at:  ', start_time)

# defining lock
lock = Lock()

# defining root
root = '/projects/temporary/automates/er/gaurav'

# defining ArgumentParser -- arguments
def process_args(args):
    parser = argparse.ArgumentParser(description='Process images for ease of training. Crop images to get rid of the background. For a cropped image of size (w,h), we pad it with PAD_TOP, PAD_BOTTOM, PAD_LEFT, PAD_RIGHT, and the result is of size (w+PAD_LEFT+PAD_RIGHT, h+PAD_TOP+PAD_BOTTOM. Then we see which bucket it falls into and pad them with whitespace to match the smallest bucket that can hold it. Finally, downsample images.')

    parser.add_argument('-yr', '--year',
                        type=int, metavar='', required=True,
                        help=('years to run'
                        ))
    parser.add_argument('-dir', '--directories', nargs="+",type=int, metavar='',
                        required=True,
                        help=('directories to run seperated by space'
                        ))
    parser.add_argument('--crop-blank-default-size', dest='crop_blank_default_size',
                        type=str, default='[600,60]',
                        help=('If an image is blank, this is the size of the cropped image, should be a Json string. Default=(600,60).'
                        ))
    parser.add_argument('--pad-size', dest='pad_size',
                        type=str, default='[8,8,8,8]',
                        help=('We pad the cropped image to the top, left, bottom, right with whitespace of size PAD_TOP, PAD_LEFT, PAD_BOTTOM, PAD_RIGHT, should be a Json string. Default=(8,8,8,8).'
                        ))
    parser.add_argument('--buckets', dest='buckets',
                        type=str, default='[[240, 100], [320, 80], [400, 80], [400, 100], [480, 80], [480, 100], [560, 80], [560, 100], [640, 80], [640, 100], [720, 80], [720, 100], [720, 120], [720, 200], [800, 100], [800, 320], [1000, 200], [1000, 400], [1200, 200], [1600, 200], [1600, 1600]]',
                        help=('Bucket sizes used for grouping. Should be a Json string. Note that this denotes the bucket size after padding and before downsampling.'
                        ))
    parser.add_argument('--downsample-ratio', dest='downsample_ratio',
                        type=float, default=2.,
                        help=('The ratio of downsampling, default=2.0.'
                        ))
    parameters = parser.parse_args(args)
    return parameters

def main_parallel(l):
    filename, output_filename, crop_blank_default_size, pad_size, buckets, downsample_ratio = l
    print(filename)
    status = crop_image(filename, output_filename, crop_blank_default_size)
    if not status:
        logging.info('%s is blank, crop a white image of default size!'%filename)
    status = pad_group_image(output_filename, output_filename, pad_size, buckets)
    if not status:
        logging.info('%s (after cropping and padding) is larger than the largest provided bucket size, left unchanged!'%filename)
    status = downsample_image(output_filename, output_filename, downsample_ratio)

def main(args):

    global root

    parameters = process_args(args)
    print(parameters)
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
        filemode='w',
        filename=os.path.join(root, f'{str(parameters.year)}/im2markup_Logs/{parameters.directories[0]}_{parameters.directories[-1]}_cropped_images.log'))

    logger = logging.getLogger()

    crop_blank_default_size = json.loads(parameters.crop_blank_default_size)
    pad_size = json.loads(parameters.pad_size)
    buckets = json.loads(parameters.buckets)
    downsample_ratio = parameters.downsample_ratio

    for DIR in parameters.directories:
        print('Currently running:  ', DIR)
        input_dir = os.path.join(root, f'{str(parameters.year)}/{DIR}/latex_images')
        im2markup_dir = os.path.join(root, f'{str(parameters.year)}/{DIR}/im2markup')
        if not os.path.exists(im2markup_dir):
            os.makedirs(im2markup_dir)
        output_dir = os.path.join(root, f'{str(parameters.year)}/{DIR}/im2markup/cropped_images')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        temp = []
        for folder in os.listdir(input_dir):
            for tyf in os.listdir(os.path.join(input_dir, folder)):
                output_folder = os.path.join(output_dir, folder)
                output_tyf = os.path.join(output_folder, tyf)
                for F in [output_folder, output_tyf]:
                    if not os.path.exists(F):
                        os.makedirs(F)
                filenames = glob.glob(os.path.join(os.path.join(input_dir, f'{folder}/{tyf}'), '*'+'.png'))
                for filename in filenames:
                    temp.append([filename, os.path.join(output_tyf, os.path.basename(filename)), crop_blank_default_size, pad_size, buckets, downsample_ratio]) 
        
        print('temp DONE!')
        with Pool(multiprocessing.cpu_count()-10) as pool:
            results = pool.map(main_parallel, temp)

if __name__ == '__main__':
    main(sys.argv[1:])

    # Printing stoping time
    print(' ')
    stop_time = datetime.now()
    print('Stoping at:  ', stop_time)
    

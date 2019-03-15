#!/usr/bin/env python

from __future__ import print_function
import csv
import errno
import json
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
from pdf2image import convert_from_path
from PIL import Image

import sys
#sys.path.append('/home/jkadowaki/im2markup/utils')
sys.path.append('/home/jkadowaki/im2markup/scripts/preprocessing')
import preprocess_images, preprocess_formulas, preprocess_filter

sys.path.append('/home/jkadowaki/im2markup/scripts/evaluation')
try:
    import evaluate_image
except ImportError:
    import subprocess
    subprocess.call([sys.executable, "-m", "pip", "install", "distance"])
    subprocess.call([sys.executable, "-m", "pip", "install", "python-Levenshtein"])
    import evaluate_image

################################################################################

"""
OBJECTIVE:

    docker container:
    `./docker.sh python -u <file_you're_running.py> <args.....>`

"""

################################################################################

def create_directory(path):
    
    """
    Creates a new directory if one does not exist.
        
    Args:
        path (str) - Name of directory
        
    """
    
    # Tries to Create a New Directory
    try:
        os.makedirs(path)
    
    # Raises an Exception if Directory Already Exists
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


################################################################################

def get_data(directory, extension=".pdf", prefix=None):
    
    """
    Walks through specified directory to find all files with specified extension.
    
    Args:
        directory (str) - Name of Directory to Search
        extension (str) - Extension of File to Search
    
    Returns:
    An iterator of file names satisfying extension criteria.
    """

    for root, dirs, files in os.walk(directory):
        for file in files:
            if all([file.endswith(extension),
                    (prefix is None or file.startswith(prefix)) ]):

                # Creates an Iterator of File Names
                yield os.path.join(root, file)


################################################################################

def main(directory='./data_20190315',
         rawdata_directory='/projects/automates/arxiv/output',
         a4=True):
    
    """
    Renders all images
    
    Args:
        directory (str): Name of directory
        rawdata_directory (str): Name of directory
    
    Returns:
        Blah.
    """

    # File Names
    gold_prefix = "equation_im2markup"
    gold_im_ext = ".pdf"
    gold_latex  = "tokens.json"
    formulas    = "formulas.lst"
    norm        = "formulas.norm.lst"
    test        = "test.lst"
    filter      = "test_filter.lst"

    # Directories
    img_dir    = "images"
    proc_dir   = "images_processed"
    plot_dir   = "plots"
    results    = "results"

    # Images
    dpi     = 250   # Scale Factor; Controls Eqn Sinze Relative to Final Image Size
    width   = 1654  # Final Width
    height  = 2339  # Final Height
    voffset = 400   # Vertical Offset from Top
    color   = (255, 255, 255, 0)  # Transparent


    # Create Directories
    create_directory(os.path.join(directory, img_dir))

    # Retrieves a List of Gold Images
    gold_img_iter = get_data(rawdata_directory,
                             prefix=gold_prefix,
                             extension=gold_im_ext)

    # Creates a Formula List & Test List
    tex_list  = open(os.path.join(directory, formulas), "w")
    test_list = open(os.path.join(directory, test), "w")

    # Equation Counter
    idx = 0
    
    
    while True:
        
        # Checks Whether  Equation Exists
        try:
            img_file = next(gold_img_iter)
        except StopIteration:
            break
        else:
            # Corresponding Gold LaTeX File
            tex_file = img_file.replace(gold_prefix + gold_im_ext, gold_latex)
            print(tex_file)
            #
            # Store Contents of Text File
            with open(tex_file) as f:     # Opens File
                data = json.load(f)       # Loads Data from JSON File
                #
                # Extract LaTeX Tokens from Tex File & Write to LST File
                tex = "".join([d.get("value") for d in data])
                tex_list.write(tex + "\n")
                print(tex)
            #
            # Convert PDF Image to PNG File
            # Note: Do NOT use 'transparent=True' parameter in convert_from_path!
            #       RGB-values set to Black (0,0,0) when transparency is set to 0.
            image = convert_from_path(img_file, dpi=dpi, fmt='png')[0].convert('RGBA')
            new_data = []
            for item in image.getdata():
                if item[0] == 255 and item[1] == 255 and item[2] == 255:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            image.putdata(new_data)
            #
            # File Name Convension to Save PNG Image
            ppr = os.path.basename(os.path.dirname(os.path.dirname(img_file)))
            eqn = os.path.basename(os.path.dirname(img_file))
            img = ppr + "_" + eqn + ".png"
            #
            if a4:
                image.save(os.path.join(directory, img_dir, img), "PNG", quality=100)
            else:
                # Creates a Transparent Image of Desired Size
                blank = Image.new('RGBA', (width, height), color)
                #
                # Compute Image Offset for Centering onto Transparent Image
                img_width, img_height = image.size
                offset = ((width - img_width) // 2, voffset - img_height//2)
                #
                # Paste Image onto Full-Sized Transparent Blank Images
                blank.paste(image, offset)
                blank.save(os.path.join(directory, img_dir, img), "PNG", quality=100)
                #
            # Write Test List
            test_list.write(" ".join([str(idx), os.path.splitext(img)[0], "basic\n"]))
            idx += 1

    # Closes File
    tex_list.close()
    test_list.close()


    # PREPROCESSING
    # Preprocess Images: Crops Formula & Group Similar Sized Images for Batching
    preprocess_images.main(["--input-dir",  os.path.join(directory,  img_dir),
                            "--output-dir", os.path.join(directory, proc_dir)])
                            
    # Preprocess Formulas: Tokenize & Normalize LaTeX Formulas
    # Doesn't work in container: no node.js
    # Must be run in python2!!!
    preprocess_formulas.main(["--mode",        "normalize",
                              "--input-file",  os.path.join(directory, formulas),
                              "--output-file", os.path.join(directory, norm)])
                              
    # Preprocess Test Set: Ignore Formulas with Many Tokens or Grammar Errors
    preprocess_filter.main(["--no-filter",
                            "--image-dir",   os.path.join(directory, proc_dir),
                            "--label-path",  os.path.join(directory, norm),
                            "--data-path",   os.path.join(directory, test),
                            "--output-path", os.path.join(directory, filter) ])


################################################################################

if __name__ == '__main__':
    #main(directory='./data/img_eqn_pairs')
    main(directory='/home/jkadowaki/automates',
         rawdata_directory='/projects/automates/arxiv/output')


#!/usr/bin/env python

from __future__ import print_function
import argparse
import csv
import errno
import json
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import multiprocessing as mp
import numpy as np
import os
from PIL import Image
import subprocess

import sys
sys.path.append('/home/jkadowaki/im2markup/scripts/preprocessing')
import preprocess_images, preprocess_formulas, preprocess_filter

sys.path.append('/home/jkadowaki/im2markup/scripts/evaluation')
try:
    import evaluate_image
except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", "distance"])
    subprocess.call([sys.executable, "-m", "pip", "install", "python-Levenshtein"])
    import evaluate_image

################################################################################

"""
OBJECTIVE:

    This program retrieves the output of the equation extraction program and
    converts the full-page PDF renders of LaTeX equations into the accepted
    full-page PNG format for the im2markup model.
    
    This code MUST be run in the 'im2markup' directory, as the im2markup image
    preprocessing scripts calls files from the 'scripts' subdirectory.

"""

################################################################################

def parse_args():
    
    """
    Parses aruments.
    """
    
    # Creates an Arugment Parser
    parser = argparse.ArgumentParser()
    
    # Adds Required Arguments
    parser.add_argument("list_directory")
    parser.add_argument("rawdata_directory")
    parser.add_argument("processed_directory")
    
    # Adds Optional Arguments
    parser.add_argument("--a4",      default='True')
    parser.add_argument("--clobber", default='True')
    parser.add_argument("--verbose", default='False')
    
    # Parses Arguments
    args = parser.parse_args()
    
    return args


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

def remove_file(path):
    
    """
    Removes a file if it exists.
        
    Args:
        path (str) - Name of filename
        
    """
    
    # Tries to Remove a File
    try:
        os.remove(path)
    
    
    # Raises an Exception if File Does Not Exist
    except OSError as exception:
        if exception.errno != errno.ENOENT:
            raise


################################################################################

def get_data(directory, extension=".pdf", prefix=None):
    
    """
    Walks through specified directory to find all files with specified extension.
    
    Args:
        directory (str) - Name of Directory to Search
        extension (str) - Extension of File to Search
        prefix (str) - Start of Filename to Search.
    
    Returns:
        An iterator of filenames in directory satisfying prefix/extension.
    """
    
    # Traverses Directory Tree via Depth-First Search
    for root, dirs, files in os.walk(directory):
        for file in files:
            
            # Checks Whether Filename Matches Requested Prefix/Extension
            if all([file.endswith(extension),
                    (prefix is None or file.startswith(prefix)) ]):
                
                # Creates an Iterator of File Names
                yield os.path.join(root, file)


################################################################################

def get_tokens(img_file,
               processed_directory='/projects/automates/arxiv', img_dir="images",
               gold_prefix="equation_im2markup", gold_ext=".pdf", gold_latex="tokens.json",
               a4=True, width=1654, height=2339, voffset=400, color=(255, 255, 255, 0),
               verbose=False):


    """
    Converts PDF image to PNG Image & Writes Out LaTeX Tokens
    
    Args:
    directory (str) - Name of Directory to Search
    extension (str) - Extension of File to Search
    prefix (str) - Start of Filename to Search.
    
    Returns:
    An iterator of filenames in directory satisfying prefix/extension.
    """


    # Corresponding Gold LaTeX File
    tex_file = img_file.replace(gold_prefix + gold_ext, gold_latex)
    
    if verbose:
        print(tex_file)

    # Store Contents of Text File
    with open(tex_file) as f:     # Opens File
        data = json.load(f)       # Loads Data from JSON File
        
        # Extract LaTeX Tokens from Tex File & Write to LST File
        tex = "".join([d.get("value") for d in data])
        ##tex_list.write(tex + "\n")
        
        if verbose:
            print(tex)

    # File Name Convension to Save PNG Image
    ppr = os.path.basename(os.path.dirname(os.path.dirname(img_file)))
    eqn = os.path.basename(os.path.dirname(img_file))
    img = ppr + "_" + eqn + ".png"
    png_img = os.path.join(processed_directory, img_dir, img)

    # Convert PDF Image to PNG File
    subprocess.call(["convert", "-density", "200", img_file,
                     "-quality", "100", png_img])

    # Convert PNG to Full-page Image if its Cropped
    if not a4:
        image = Image.open(png_img)

        # Creates a Transparent Image of Desired Size
        blank = Image.new('RGBA', (width, height), color)

        # Compute Image Offset for Centering onto Transparent Image
        img_width, img_height = image.size
        offset = ((width - img_width)//2, voffset - img_height//2)

        # Paste Image onto Full-Sized Transparent Blank Images
        blank.paste(image, offset)
        blank.save(png_img, "PNG", quality=100)

    # Write Test List
    ##test_list.write(" ".join([str(idx), os.path.splitext(img)[0], "basic\n"]))
    ##idx += 1

    return tex, img


################################################################################

def single_process(list_directory='./data_1802',
                   rawdata_directory='/projects/automates/arxiv/output/1802',
                   processed_directory='/projects/automates/arxiv',
                   a4=True, clobber=True, verbose=False):

    """
    Converts all rendered PDFs of gold tokens to full page PNGs & preprocesses
    the full page PNGs into usable format for the im2markup model.
    
    Args:
        list_directory (str) - Directory to save .lst files
        rawdata_directory (str) - Directory with rendered images of gold tokens
        processed_directory (str) - Path to save 'images' and 'image_processed'
                                    directories for training/validation/testing
        a4 (bool) - Flag specifying whether rendered images are full pages
        clobber (bool) - Flag specifying whether to overwrite .lst files
                         (DISCLAIMER: NOT READY TO OVERWRITE IMAGES.)
        verbose (bool) - Flag specifying whether to print file names of converted
                         images and their respective gold tokens.
    """

    # File Names
    gold_prefix = "equation_im2markup"
    gold_ext    = ".pdf"
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
    width   = 1654  # Final Width
    height  = 2339  # Final Height
    voffset = 400   # Vertical Offset from Top
    color   = (255, 255, 255, 0)  # Transparent


    # Create Directories
    create_directory(os.path.join(processed_directory, img_dir))

    # Retrieves a List of Gold Images
    gold_img_iter = get_data(rawdata_directory,
                             prefix=gold_prefix,
                             extension=gold_ext)

    # Deletes Existing File
    if clobber:
        remove_file(os.path.join(list_directory, formulas))
        remove_file(os.path.join(list_directory, test))
    
    # Creates/Appends a Formula List & Test List
    tex_list  = open(os.path.join(list_directory, formulas), "a+")
    test_list = open(os.path.join(list_directory, test), "a+")

    # Equation Counter
    idx = 0
    
    
    while True:
        
        # Checks Whether Equation Exists
        try:
            img_file = next(gold_img_iter)
        
        # Exits Loop if Equation Does Not Exist
        except StopIteration:
            break
        
        # Converts PDF image to PNG Image If Equation Exists
        else:
            
            tex, img = get_tokens(img_file, img_dir=img_dir, verbose=verbose,
                                  processed_directory=processed_directory,
                                  gold_prefix=gold_prefix, gold_ext=gold_ext,
                                  gold_latex=gold_latex, a4=True, width=width,
                                  height=height, voffset=voffset, color=color)
            
            # Write to LST File
            tex_list.write(tex + "\n")
                
            # Write Test List
            test_list.write(" ".join([str(idx), os.path.splitext(img)[0], "basic\n"]))
            idx += 1

    # Closes File
    tex_list.close()
    test_list.close()


    # PREPROCESSING
    # Preprocess Images: Crops Formula & Group Similar Sized Images for Batching
    preprocess_images.main(["--input-dir",  os.path.join(processed_directory, img_dir),
                            "--output-dir", os.path.join(processed_directory, proc_dir)])
                            
    # Preprocess Formulas: Tokenize & Normalize LaTeX Formulas
    # Doesn't work in container: no node.js
    # Must be run in python2!!!
    preprocess_formulas.main(["--mode",        "normalize",
                              "--input-file",  os.path.join(list_directory, formulas),
                              "--output-file", os.path.join(list_directory, norm)])
                              
    # Preprocess Test Set: Ignore Formulas with Many Tokens or Grammar Errors
    preprocess_filter.main(["--no-filter",
                            "--image-dir",   os.path.join(processed_directory, proc_dir),
                            "--label-path",  os.path.join(list_directory, norm),
                            "--data-path",   os.path.join(list_directory, test),
                            "--output-path", os.path.join(list_directory, filter) ])

################################################################################

def multiprocess(list_directory='./data_1802',
                 rawdata_directory='/projects/automates/arxiv/output/1802',
                 processed_directory='/projects/automates/arxiv',
                 a4=True, clobber=True, verbose=False):

    # File Names
    gold_prefix = "equation_im2markup"
    gold_ext    = ".pdf"
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
    width   = 1654  # Final Width
    height  = 2339  # Final Height
    voffset = 400   # Vertical Offset from Top
    color   = (255, 255, 255, 0)  # Transparent
    
    
    # Create Directories
    create_directory(os.path.join(processed_directory, img_dir))
    
    # Retrieves a List of Gold Images
    gold_img_iter = get_data(rawdata_directory,
                             prefix=gold_prefix,
                             extension=gold_ext)
        
    # Deletes Existing File
    if clobber:
        remove_file(os.path.join(list_directory, formulas))
        remove_file(os.path.join(list_directory, test))

    # Creates/Appends a Formula List & Test List
    tex_list  = open(os.path.join(list_directory, formulas), "a+")
    test_list = open(os.path.join(list_directory, test), "a+")
    
    # Equation Counter
    idx = 0
    
    
    p = mp.Pool(32)
    for tex, img in p.imap(get_tokens, gold_img_iter):
        
        # Write to LST File
        tex_list.write(tex + "\n")

        # Write Test List
        test_list.write(" ".join([str(idx), os.path.splitext(img)[0], "basic\n"]))
        idx += 1

    # Closes File
    tex_list.close()
    test_list.close()
    
    
    # PREPROCESSING
    # Preprocess Images: Crops Formula & Group Similar Sized Images for Batching
    preprocess_images.main(["--input-dir",  os.path.join(processed_directory, img_dir),
                            "--output-dir", os.path.join(processed_directory, proc_dir)])

    # Preprocess Formulas: Tokenize & Normalize LaTeX Formulas
    # Doesn't work in container: no node.js
    # Must be run in python2!!!
    preprocess_formulas.main(["--mode",        "normalize",
                              "--input-file",  os.path.join(list_directory, formulas),
                              "--output-file", os.path.join(list_directory, norm)])
    
    # Preprocess Test Set: Ignore Formulas with Many Tokens or Grammar Errors
    preprocess_filter.main(["--no-filter",
                            "--image-dir",   os.path.join(processed_directory, proc_dir),
                            "--label-path",  os.path.join(list_directory, norm),
                            "--data-path",   os.path.join(list_directory, test),
                            "--output-path", os.path.join(list_directory, filter) ])



###########################################################################pypp#####

if __name__ == '__main__':

    """
    single_process(list_directory='/home/jkadowaki/automates/data_1802',
                   rawdata_directory='/projects/automates/arxiv/output/1802',
                   processed_directory='/projects/automates/arxiv',
                   a4=True,
                   clobber=True,
                   verbose=False)
    """

    multiprocess(list_directory='/home/jkadowaki/automates/data_1802',
                 rawdata_directory='/projects/automates/arxiv/output/1802',
                 processed_directory='/projects/automates/arxiv',
                 a4=True,
                 clobber=True,
                 verbose=False)

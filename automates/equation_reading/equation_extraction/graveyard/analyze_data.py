#!/usr/bin/env python

from __future__ import print_function

import csv
import errno
import logging

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image

import sys
sys.path.append('/home/jkadowaki/im2markup/code/equation_extraction')

sys.path.append('/home/jkadowaki/im2markup/scripts/evaluation')
sys.path.append('/home/jkadowaki/im2markup/utils')
import render_latex

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
    Make (toy first, then using the full test set) a tsv with the columns:
        image_name \t gold_tokens \t generated_tokens \t compiled_yesno
    
    docker container:
    `./docker.sh python -u <file_you're_running.py> <args.....>`
    
"""

################################################################################

def create_directory(path):
    
    """
    Creates a new directory if one does not exist.
    
    Args:
        path (str): Name of directory
    
    """
    #
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


################################################################################

def get_data(directory, extension=".pdf"):
    
    """
    Walks through specified directory to find all files with specified extension.
    
    Args:
        directory (str) - Name of Directory to Search
        extension (str) - Extension of File to Search
        
    Returns:
        A list of file names satisfying extension criteria.
    """
    
    file_results = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                file_results.append(os.path.join(root, file))
    #
    return file_results


################################################################################

def panel_plot(gold_im_directory, pred_im_directory, extension=".png",
               plot_name="panel-plot.pdf", plot_directory="plots"):
    
    """
    Plots a side-by-side comparison of the rendered gold & predicted images.
    
    Args:
        gold_im_directory (str): Name of directory containing rendered gold images.
        pred_im_directory (str): Name of directory containing predicted images.
        extension (str): File type extension of rendered images.
        plot_name (str): File name of plot to save.
        plot_directory (str): Name of directory to save plot.
    
    """
    # Retrieve List of Gold Images
    gold_im_list = get_data(gold_im_directory, extension='.png')
    #
    # Create Side-by-Side Plots
    f, axarr = plt.subplots(len(pred_im_list), 2,
                            figsize=(0.5*len(gold_im_list), 2*len(gold_im_list)) )
    #
    # Axes Labels
    for ax, col in zip(axarr[0], ["Gold Image", "Predicted Image"]):
        ax.set_title(col, size=72)
    for ax, row in zip(axarr[:,0], [os.path.basename(i) for i in gold_im_list]):
        ax.set_ylabel(row, rotation=90, fontsize=12)
    #
    # Plotting Gold & Predicted Images
    for idx, fname in enumerate(gold_im_list):
        axarr[idx,0].imshow(Image.open(fname).convert('RGBA'))
        pred = fname.replace(gold_im_directory, pred_im_directory)
        axarr[idx,0].set_xticks([])
        axarr[idx,0].set_yticks([])
        axarr[idx,1].set_xticks([])
        axarr[idx,1].set_yticks([])
        #
        try:
            axarr[idx,1].imshow(Image.open(pred).convert('RGBA'))
        except:
            print(pred, "does not exist!")
    #
    # Save Plot
    create_directory(plot_directory)
    plt.savefig(os.path.join(plot_directory, plot_name), bbox_inches='tight')
    plt.show()
    plt.close()


################################################################################

def compare_plot(gold_im_directory, pred_im_directory, extension=".png",
                 plot_name="comparison-plot.pdf", plot_directory="plots"):
    
    """
    Plots a comparison of the rendered gold & predicted images into a single RGB
        image with the gold image as the blue channel and predicted as red.
        
    Args:
        gold_im_directory (str): Name of directory containing rendered gold images.
        pred_im_directory (str): Name of directory containing predicted images.
        extension (str): File type extension of rendered images.
        plot_name (str): File name of plot to save.
        plot_directory (str): Name of directory to save plot.
    """
    
    gold_im_list = get_data(gold_im_directory, extension='.png')
    
    f, axarr = plt.subplots(len(gold_im_list), 2)
    
    # CHANGE FROM HERE!!!
    """
    for idx, fname in enumerate(gold_im_list):
        axarr[idx,0].imshow(Image.open(fname))
        axarr[idx,1].imshow(Image.open(fname.replace(gold_im_directory,
                                                     pred_im_directory)))
    """
    # Save Plot
    create_directory(plot_directory)
    plt.savefig(os.path.join(plot_directory, plot_name))
    plt.show()
    plt.close()


################################################################################

def main(list_directory='./im2markup/data/sample',
         processed_directory='./im2markup/data/sample'):
    
    """
    Renders all images
    
    Args:
        directory (str): Name of directory
        
    Returns:
        Blah.
    """
    
    process_dir  = 'images_processed'      # Preprocessed Image Directory
    render_dir   = 'images_rendered'       # Rendered Image Directory
    gold_im_dir  = 'images_gold'           # Rendered Gold Image Directory
    pred_im_dir  = 'images_pred'           # Rendered Predicted Image Directory
    plot_dir     = 'plots'                 # Plot Directory
    results_file = 'results/results.txt'   # Result File
    render_file  = 'results/rendered.tsv'  # Rendered Results File
    gold_list    = 'formulas.lst'          # List of Gold Tokens
    test_list    = 'test_filter.lst'       # List of Images in Test Set
    plot_name    = 'panel-plot.pdf'


    #images    = get_data(os.path.join(directory, img_path), extension='.png')
    processed = get_data(os.path.join(processed_directory, process_dir), extension='.png')

    # Load Results File. Format:
    # <img_name1>\t<label_gold1>\t<label_pred1>\t<score_pred1>\t<score_gold1>
    results = np.genfromtxt(os.path.join(list_directory, results_file),
                            delimiter='\t', dtype=None, comments=None)

    # Render Gold & Predicted LaTeX Equations
    render_latex.main(["--result-path", os.path.join(list_directory, results_file),
                       "--data-path",   os.path.join(list_directory, test_list),
                       "--label-path",  os.path.join(list_directory, gold_list),
                       "--output-dir",  os.path.join(processed_directory, render_dir),
                       "--no-replace"])
    logging.info('Jobs finished')

    # Create Side-by-Side Plots of Rendered Gold & Predicted Equations
    panel_plot(os.path.join(processed_directory, render_dir, gold_im_dir),
               os.path.join(processed_directory, render_dir, pred_im_dir),
               extension=".png",
               plot_name=plot_name,
               plot_directory=os.path.join(list_directory, plot_dir))

    # Print Evaluation Metrics
    evaluate_image.main(["--images-dir", os.path.join(processed_directory, render_dir)])

    # Write Rendered Results File
    with open(os.path.join(list_directory, render_file), 'wt') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        for idx, obj in enumerate(results):
            pred = os.path.join(processed_directory, render_dir, pred_im_dir, results[idx][0])
            tsv_writer.writerow([obj[0], obj[1], obj[2], os.path.isfile(pred)])


################################################################################

if __name__ == '__main__':
    main(list_directory='/home/jkadowaki/automates/data_1802',
         processed_directory='/projects/automates/arxiv')


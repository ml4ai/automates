#!/usr/bin/env python

from __future__ import print_function
import argparse
from collections import Counter
import csv
import errno
import json
import logging
import matplotlib.pyplot as plt
plt.rc('text', usetex=True)
import multiprocessing as mp
import numpy as np
import os
from PIL import Image
import re
import shutil
import glob as g

try:
    # Python 3
    from collections import ChainMap
except ImportError:
    # Python 2
    from chainmap import ChainMap

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

def create_directory(path, mode=0o755):
    
    """
    Creates a new directory if one does not exist.
        
    Args:
        path (str) - Name of directory
        
    """
    
    # Tries to Create a New Directory
    try:
        original_umask = os.umask(000)
        os.makedirs(path, mode=mode)
        os.umask(original_umask)
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
    #
    """
    Walks through specified directory to find all files with specified extension.
    
    Args:
        directory (str) - Name of Directory to Search
        extension (str) - Extension of File to Search
        prefix (str) - Start of Filename to Search.
    
    Returns:
        An iterator of filenames in directory satisfying prefix/extension.
    """
    #
    # Traverses Directory Tree via Depth-First Search
    for root, dirs, files in os.walk(directory):
        for file in files:
            #
            # Checks Whether Filename Matches Requested Prefix/Extension
            if all([file.endswith(extension),
                    (prefix is None or file.startswith(prefix)) ]):
                #
                # Creates an Iterator of File Names
                yield os.path.join(root, file)


################################################################################

def get_tokens_length(json_file):
    #
    """
    Converts PDF image to PNG Image & Writes Out LaTeX Tokens
    #
    Args:
        directory (str) - Name of Directory to Search
        extension (str) - Extension of File to Search
        prefix (str) - Start of Filename to Search.
        #
    Returns:
        An iterator of filenames in directory satisfying prefix/extension.
    """
    #
    # Store Contents of Text File
    with open(json_file) as f:     # Opens File
        data = json.load(f)        # Loads Data from JSON File
    
    begin_idx = []
    end_idx = []
    
    # All the various ways to create an equation environment!
    # https://en.wikibooks.org/wiki/LaTeX/Advanced_Mathematics
    begin_markers = ['\\begin {equation}', '\\begin {equation*}',
                     '\\begin {align}',    '\\begin {align*}',
                     '\\begin {eqnarray}', '\\begin {eqnarray*}',
                     '\\begin {gather}',   '\\begin {gather*}',
                     '\\begin {multline}', '\\begin {multline*}',
                     '\\begin {flalign}',  '\\begin {flalign*}',
                     '\\begin {alignat}',  '\\begin {alignat*}',  '\[']
    end_markers   = ['\\end {equation}',   '\\end {equation*}',
                     '\\end {align}',      '\\end {align*}',
                     '\\end {eqnarray}',   '\\end {eqnarray*}',
                     '\\end {gather}',     '\\end {gather*}',
                     '\\end {multline}',   '\\end {multline*}',
                     '\\end {flalign}',    '\\end {flalign*}',
                     '\\end {alignat}',   '\\end {alignat*}',    '\]']
                     #
    toggle = True
    ambiguous_marker = "$$"
    #
    context_length = len(data)
    #
    window_sizes = [8,9,11,12]
    #
    for window_length in window_sizes:
        for idx, token in enumerate(data[:-window_length+1]):
            if token == {'type': "EscapeSequence", 'value': "\\begin "}:
                window_str = ''.join([t.get('value') for t in data[idx:idx+window_length]])
                if window_str in begin_markers:
                    begin_idx.append(idx)
            #
            elif token == {'type': "EscapeSequence", 'value': "\\end "}:
                window_str = ''.join([t.get('value') for t in data[idx:idx+window_length]])
                if window_str in end_markers:
                    end_idx.append(idx)
            #
            elif token == {'type': "MathShift", 'value': "$"}:
                if ''.join([t.get('value') for t in data[idx:idx+2]]) in ambiguous_marker:
                    if toggle:
                        begin_idx.append(idx)
                        toggle = False
                    else:
                        end_idx.append(idx)
                        toggle = True
    #
    if len(begin_idx) == len(end_idx):
        avg = np.mean([ end_idx[idx]-begin_idx[idx] for idx in range(len(begin_idx)) ])
        return avg

################################################################################

def get_metadata(json_file, id_match, verbose=False):
    #
    """
    Converts PDF image to PNG Image & Writes Out LaTeX Tokens
    #
    Args:
        directory (str) - Name of Directory to Search
        extension (str) - Extension of File to Search
        prefix (str) - Start of Filename to Search.
    #
    Returns:
        An iterator of filenames in directory satisfying prefix/extension.
    """
    #
    id2spec_dict = {}
    #
    # Store Contents of Text File
    for line in open(json_file, 'r'):
        paper = json.loads(line)
        id    = paper.get('metadata').get('id')
        spec  = paper.get('header').get('setSpec')
        #
        if id_match in id:
            id2spec_dict[id] = spec
            if verbose:
                print("{0}: {1}".format(id, spec))
    #
    return id2spec_dict


################################################################################

def spec_stats(id2spec_dict, plot_name='spec_hist.pdf', verbose=False):
    #
    spec_freq = Counter(id2spec_dict.values())
    if verbose:
        print("Represented Subjects:", spec_freq)
    #
    if plot_name:
        fig = plt.figure(figsize=(10,10))
        val = np.array(list(spec_freq.values()))+1
        plt.pie(spec_freq.values(),
                labels=spec_freq.keys(),
                explode=max(val)/sum(val) - val/sum(val) + 0.1,
                pctdistance=0.75,
                autopct='%1.1f%%')
        #
        if verbose:
            print(plot_name)
        plt.savefig(plot_name, bbox_inches='tight')
        plt.close()
    #
    return spec_freq

################################################################################

def get_paper_id(id2spec_dict, spec):
    return [k for k,v in id2spec_dict.items() if v==spec]

################################################################################

def read_txt(fname, add_lines=True, remove_misc=True):
    with open(fname, 'r') as f:
        data = f.read()
    return data


################################################################################

# Plot Context Length Distribution for Each Subject
def plot_feature(feature, bins, xlabel, ylabel, title,
                 spec_all, eqn_stats, plot_name):
    #
    ncols = 5
    nrows = int(np.ceil(len(spec_all.keys())/ncols))
    box_length = 4
    #
    # Creates a Multi-Panel Histogram for Specified Feature -- One Histogram for Each Subject
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, sharex=False,
                             figsize=(ncols*box_length, nrows*box_length))
    ax = axes.flatten()
    plt.tick_params(labelsize=12)
    #
    # Create 1 Big Overall Plot to Anchor X- & Y-Labels and Title
    axbig = fig.add_subplot(111, frameon=False)
    axbig.set_xticks([])
    axbig.set_yticks([])
    axbig.set_xlabel(xlabel, fontsize=24, labelpad=24)
    axbig.set_ylabel(ylabel, fontsize=24, labelpad=36)
    axbig.set_title(title, fontsize=30)
    #
    # Iterates through All ArXiV Subjects
    for idx, spec in enumerate(spec_all.keys()):
        if feature == "char_eqn":
            try:
                values = [np.mean(eqn.get(feature)) for eqn in eqn_stats if eqn.get('spec')==spec]
            except:
                #print(feature, idx, spec, "failed.")
                continue
        elif feature == "num_ppr_eqn":
            values = list({eqn.get('paper'):eqn.get(feature) for eqn in eqn_stats if eqn.get('spec')==spec}.values())
        else:
            values = [eqn.get(feature) for eqn in eqn_stats if eqn.get('spec')==spec]
        #
        # Plots Histogram
        if values:
            try:
                ax[idx].hist(values, bins, label=spec, histtype='step', stacked=True, fill=True)
                ax[idx].legend(loc='best')
            except:
                pass
    #
    #print(plot_name)
    fig.savefig(plot_name, bbox_inches='tight')
    plt.close()

################################################################################

def write_dictlist(dictlist, fname):
    try:
        with open(fname, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=dictlist[0].keys())
            writer.writeheader()
            for dict in dictlist:
                writer.writerow(dict)
    except IOError:
        print("I/O error")

################################################################################

def strList_to_list(strList):
    slist = strList.replace('[','').replace(']','').split(',')
    return [int(val) if val else 0 for val in slist]

def read_dictlist(csv_file):
    """
    Helpful in interactive mode if and when creating plots crash the code.
    Imports eqn_stats.csv into eqn_stats dict_list format.
    """
    dictlist = []
    with open(csv_file) as f:
        for row in csv.DictReader(f, skipinitialspace=True):
            line_dict = {}
            for k, v in row.items():
                if k in ['paper', 'spec', 'eqn_dir']:
                    val = v
                elif k in ['num_ppr_eqn', 'context_length', 'num_intext_eqn', 'num_eqn']:
                    val = int(v) if v else 0
                elif k in ['frac_intext_eqn', 'frac_eqn', 'num_tokens']:
                    val = float(v) if v else 0
                elif k in ['char_intext_eqn', 'char_eqn']:
                    val = strList_to_list(v) if v else [0]
                else:
                    print(k, "not a keyword. Value:", v)
                line_dict[k] = val
            dictlist.append(line_dict)
    return dictlist

################################################################################

def filter( eqn_stats,
            excluded_fields=['math'],
            min_eqn_context=1,
            max_eqn_ppr=5,
            max_eqn_context=1,
            max_eqn_intext=50,
            max_eqn_token=200,
            src_dir='annotation',
            dst_dir='final'):
    #
    """
    Filters to Apply:
    1. Number of equations in whole paper < N
       Perhaps N=5?
       (Check equation density or Number of pages.)
    2. Number of equations < 1 in context (only target equation)
    3. Number of in-text math ($$ pairs in context) < 50
    4. Equation length < 200 tokens
    """
    #
    if dst_dir:
        create_directory(dst_dir)
    #
    eqn_filter_stats = []
    for eqn in eqn_stats:
        try:
            if eqn.get("spec") not in excluded_fields and \
               eqn.get("num_ppr_eqn") <= max_eqn_ppr  and \
               eqn.get("num_eqn") >= min_eqn_context  and \
               eqn.get("num_eqn") <= max_eqn_context  and \
               eqn.get("num_intext_eqn") <= max_eqn_intext and \
               np.mean(eqn.get("avg_num_tokens")) <= max_eqn_token:
                    eqn_filter_stats.append(eqn)
                    if dst_dir:
                        shutil.copy2(os.path.join(src_dir, eqn.get('paper'), eqn.get('eqn_dir'), 'context_k3.txt'),
                                     os.path.join(dst_dir, eqn.get('paper') + "_" + eqn.get('eqn_dir') + ".txt"))
                        shutil.copy2(os.path.join(src_dir, eqn.get('paper'), eqn.get('eqn_dir'), 'aabb.png'),
                                     os.path.join(dst_dir, eqn.get('paper') + "_" + eqn.get('eqn_dir') + ".png"))
        except:
            print(eqn.get("spec"),
                  eqn.get("num_ppr_eqn"),
                  eqn.get("num_eqn"),
                  eqn.get("num_intext_eqn"),
                  np.mean(eqn.get("avg_num_tokens")))
    #
    write_dictlist(eqn_filter_stats, 'eqn_filter_stats.csv')
    #
    return eqn_filter_stats


################################################################################

def main(arxiv_id        = '1801',
         annot_dir       = 'annotation',
         pdf_dir         = 'output',
         paper_prefix    = '',
         plot_dir        = 'plots',
         brat_dir        = 'final',
         meta_data       = 'harvest_arxiv.json',
         max_eqn_ppr     = 5,
         max_eqn_context = 1,
         max_eqn_intext  = 50,
         max_eqn_token   = 200,
         max_eqn_chars   = 500,
         excluded_fields = ['math']):

    """
    ARGS:
        arxiv_id (str): Directory name demarking the year & month (i.e., 'YYMM')
        plot_dir (str): Directory to save plots
                        If empty string, script will not generate plots
    RETURNS:

    """

    create_directory(os.path.join(plot_dir, arxiv_id))
    begin_eqnmarkers = ['begin{equation}', 'begin{equation*}', 
                        'begin{align}',    'begin{align*}', 
                        'begin{eqnarray}', 'begin{eqnarray*}'
                        'begin{gather}',   'begin{gather*}',
                        'begin{multline}', 'begin{multline*}',
                        'begin{flalign}',  'begin{flalign*}',
                        'begin{alignat}',  'begin{alignat*}',  '\[' ]

    end_eqnmarkers   = ['end{equation}',   'end{equation*}',
                        'end{align}',      'end{align*}',
                        'end{eqnarray}',   'end{eqnarray*}'
                        'end{gather}',     'end{gather*}',
                        'end{multline}',   'end{multline*}',
                        'end{flalign}',    'end{flalign*}',
                        'end{alignat}',    'end{alignat*}',  '\]' ]
    
    id2spec_all = get_metadata(meta_data, paper_prefix)
    spec_all    = spec_stats(id2spec_all,
                             plot_name=os.path.join(plot_dir, arxiv_id, 'spec_all.pdf')
                                       if plot_dir else '')

    annot_iter      = os.walk(os.path.join(annot_dir, arxiv_id))
    proc_paper_list = annot_iter.__next__()[1]
    id2spec_proc    = dict(ChainMap(*[{paper:id2spec_all.get(paper)} for paper in proc_paper_list]))
    spec_proc       = spec_stats(id2spec_proc,
                                 plot_name=os.path.join(plot_dir, arxiv_id, 'spec_proc.pdf')
                                           if plot_dir else '')

    if plot_dir:
        recovery_rate = dict(ChainMap(*[{spec:spec_proc.get(spec)/spec_all.get(spec)}
                                        if spec_proc.get(spec)
                                        else {spec:0} for spec in spec_all.keys()]))
        fig, ax = plt.subplots(figsize=(8,5))
        rects = ax.barh(range(len(spec_all.keys())), [recovery_rate.get(spec) for spec in spec_all.keys()],
                        align='center',
                        height=0.5,
                        tick_label=list(spec_all.keys()))
        plt.savefig(os.path.join(plot_dir, arxiv_id, 'recovery_rate.pdf'), bbox_inches='tight')
        plt.close()


    annot_iter      = os.walk(os.path.join(annot_dir, arxiv_id))
    proc_paper_list = annot_iter.__next__()[1]

    spec2eqncount  = {}  # Stores Equation Counts Per Subject
    eqn_stats      = []  # Stores Equation Statistics
    #
    # Iterates through Each Paper
    while True:
        try:
            paper_dir, eqn_dirs, _ = annot_iter.__next__()
        except StopIteration:
            break
        #
        paper     = os.path.basename(paper_dir)
        spec      = id2spec_all.get(paper)
        eqn_count = len(eqn_dirs)
        print(paper, spec, eqn_count)
        #
        # Get
        count_list = spec2eqncount.get(spec)
        #
        if count_list:
            count_list.append(eqn_count)
            spec2eqncount.update({spec:count_list})
        else:
            spec2eqncount.update({spec:[eqn_count]})
        #
        # Iterates through Each Equation in Paper
        for i in range(eqn_count):
            #
            # Reads Context of Each Equation
            try:
                eqn_dir, _, files = annot_iter.__next__()
            except StopIteration:
                break
            context_file = [f for f in files if '.txt' in f][0]
            context_path = os.path.join(eqn_dir,context_file)
            context = read_txt(context_path)
            
            json_file    = [f for f in files if '.json' in f][0]
            json_path    = os.path.join(eqn_dir,json_file)
            num_tokens   = get_tokens_length(json_path)
            #
            # Finds all In-Text Equation Markers
            num_char = len(context)
            intext_eqn_idx = []
            for match in re.finditer('\$', context):
                intext_eqn_idx.append(match.start())
            #
            # Number of Characters in Each In-Text Equations in Context (incl. $$s)
            char_intext_eqn = [ x for x in 
                                [ intext_eqn_idx[2*i+1] - intext_eqn_idx[2*i] - 1
                                  for i in range(int(len(intext_eqn_idx)/2)) ]
                                if x > 0 ]
                               #
            # Number of In-Text Equations in Context
            num_intext_eqn = int(len(char_intext_eqn))

            # Fraction of Total Context in In-Text Equations
            frac_intext_eqn = sum(char_intext_eqn) / num_char
            #
            # Finds Stand Alone Equation Markers
            start_eqn_idx = []
            end_eqn_idx = []
            for mark in begin_eqnmarkers:
                for match in re.finditer(mark, context):
                    start_eqn_idx.append(match.end())
                
            for mark in end_eqnmarkers:
                for match in re.finditer(mark, context):
                    end_eqn_idx.append(match.start()-1)
            
            # Number of Stand Alone Equations in Context
            num_eqn = int(len(end_eqn_idx))
            #
            # Number of Characters in Each Stand Alone Equations in Context
            # (excl. \begin{} and \end{})
            if len(start_eqn_idx) == len(end_eqn_idx):
                char_eqn = [ len(context[start_eqn_idx[i]:end_eqn_idx[i]].strip()) for i in range(num_eqn)]
                #
                # Fraction of Total Context in In-Text Equations
                frac_eqn = sum(char_eqn) / num_char
                #
                eqn_dict = {"paper":paper,
                            "spec":spec,
                            "eqn_dir":os.path.basename(eqn_dir),
                            "num_ppr_eqn": eqn_count,
                            "context_length":num_char,
                            "num_intext_eqn":num_intext_eqn,
                            "char_intext_eqn":char_intext_eqn,
                            "frac_intext_eqn":round(frac_intext_eqn,3),
                            "num_eqn":num_eqn,
                            "char_eqn":char_eqn,
                            "frac_eqn":round(frac_eqn,3),
                            "avg_num_tokens":num_tokens
                           }
                eqn_stats.append(eqn_dict)
            #else:
                #print(paper, os.path.basename(eqn_dir), "failed.", len(start_eqn_idx), len(end_eqn_idx))
                #pass

    # Save Equation Statistics Data to File
    write_dictlist(eqn_stats, os.path.join(plot_dir, arxiv_id, 'eqn_stats_{0}.csv'.format(arxiv_id)))
    
    features_prop = [("num_ppr_eqn",
                      r"Number of Extracted Equations Environments in Paper",
                      r"Number of Papers",
                      os.path.join(plot_dir, arxiv_id, "eqn_count.png")),
                     
                     ("context_length",
                      r"Number of Characters in Equation Context",
                      r"Number of Extracted Equation Contexts",
                      os.path.join(plot_dir, arxiv_id, "context_length.png")),
                     
                     ("num_intext_eqn",
                      r"Number of In-Text Equations in Context",
                      r"Number of Extracted Equation Contexts",
                      os.path.join(plot_dir, arxiv_id, "num_intext_eqn.png")),
                     
                     ("frac_intext_eqn",
                      r"Fraction of Context Allocated to In-Text Equations",
                      r"Number of Extracted Equation Contexts",
                      os.path.join(plot_dir, arxiv_id, "frac_intext_eqn.png")),
                     
                     ("num_eqn",
                      r"Number of Equations Environments w/in Extracted Context",
                      r"Number of Extracted Equation Contexts",
                      os.path.join(plot_dir, arxiv_id, "num_eqn.png")),
                     
                     ("frac_eqn",
                      r"Fraction of Context Allocated to Equation Environments",
                      r"Number of Extracted Equation Contexts",
                      os.path.join(plot_dir, arxiv_id, "frac_eqn.png")),
                     
                     ("char_eqn",
                      r"Number of Characters in Context Equation Environments",
                      r"Number of Extracted Equation Contexts",
                      os.path.join(plot_dir, arxiv_id, "char_eqn.png")),
                     
                     ("avg_num_tokens",
                      r"Number of Tokens within Context Equation Environments",
                      r"Number of Extracted Equation Contexts",
                      os.path.join(plot_dir, arxiv_id, "num_tokens.png")) ]
    
    bins = [np.arange(0,75,5),       # num_ppr_eqn
            np.arange(0,20000,1000), # context_length
            np.arange(0,200,10),     # num_intext_eqn
            np.arange(0,1,0.05),     # frac_intext_eqn
            np.arange(0,50,5),       # num_eqn
            np.arange(0,1,0.05),     # frac_eqn
            np.arange(0,500,20),     # char_eqn
            np.arange(0,500,20)]     # num_tokens
            
    if plot_dir:
        for idx, (feature, xlabel, ylabel, fname) in enumerate(features_prop):
            plot_feature(feature, bins[idx], xlabel, ylabel, "No Filtering", spec_proc, eqn_stats, fname)

    eqn_filter_stats = filter(eqn_stats, excluded_fields = excluded_fields,
                                         max_eqn_ppr     = max_eqn_ppr,
                                         max_eqn_context = max_eqn_context,
                                         max_eqn_intext  = max_eqn_intext,
                                         max_eqn_token   = max_eqn_token,
                              src_dir=annot_dir,
                              dst_dir='final')

                                         
    bins = [np.arange(max_eqn_ppr+1),       # num_ppr_eqn
            np.arange(0,20000,1000),        # context_length
            np.arange(0,50,15),             # num_intext_eqn
            np.arange(0,0.6,0.05),          # frac_intext_eqn
            np.arange(0,50,5),              # num_eqn
            np.arange(0,0.25,0.01),         # frac_eqn
            np.arange(0,max_eqn_chars,20),  # char_eqn
            np.arange(0,max_eqn_token,20)]  # num_tokens

    if plot_dir:
        for idx, (feature, xlabel, ylabel, fname) in enumerate(features_prop):
            plot_feature(feature, bins[idx], xlabel, ylabel, "With Filtering",
                         spec_proc, eqn_filter_stats,
                         fname.replace(os.path.join(plot_dir, arxiv_id) + "/",
                                       os.path.join(plot_dir,  arxiv_id, 'filter_')))


    create_directory(brat_dir)

    # Consolidates Relevant BRAT & PNG Files from Filtered Equations into a Single Directory
    for eqn in eqn_filter_stats:
        # Iterates through Context & Bounding Box Files
        for file in ["context_k3.txt", "aabb.png"]:
            # Move File if it Exists.
            # Name Change for Convenience:  orig ---> new
            orig = os.path.join(annot_dir, arxiv_id, eqn.get("paper"), eqn.get("eqn_dir"), file)
            new  = os.path.join(brat_dir,
                    eqn.get("paper") + "_" +  eqn.get("eqn_dir") + os.path.splitext(file)[1])
            try:
                shutil.copy2(orig, new)
            except:
                print(new, "does not exist.")

        # Search for Rendered PDF & Copy
        try:
            pdf_new = os.path.join(brat_dir, eqn.get("paper") + ".pdf")
            if not os.path.isfile(pdf_new):
                pdf_loc = g.glob(os.path.join(pdf_dir, arxiv_id, eqn.get("paper"), "build", "*.pdf"))[0]
                shutil.copy2(pdf_loc, pdf_new)
        except:
            print("PDF does not exist for", eqn.get("paper"))
       


################################################################################

if __name__ == "__main__":
    
    main(arxiv_id        = '1805',
         annot_dir       = '/projects/automates/collect_2019SEPT19/annotation',
         pdf_dir         = '/projects/automates/collect_2019SEPT19/output',
         paper_prefix    = '',
         plot_dir        = '',
         brat_dir        = '/projects/automates/collect_2019SEPT19/final',
         meta_data       = '/projects/automates/collect_2019SEPT19/harvest_arxiv.json',
         max_eqn_ppr     = 10,     #5,
         max_eqn_context = 2,      #1,
         max_eqn_intext  = 100,    #50,
         max_eqn_token   = 500,    #200,
         max_eqn_chars   = 1000,   #500,
         excluded_fields = ['math'])

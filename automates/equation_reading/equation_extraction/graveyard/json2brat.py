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
import shutil
import subprocess

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

def remove_content(tex, previous_tex=None, content="table"):
    str_table = "\\begin{{{}}}".format(content)
    end_table = "\\end{{{}}}".format(content)
    str_idx   = tex.find(str_table)
    end_idx   = tex.find(end_table)
    
    # Recursively Removes Parts of Table in TeX Until None Left
    if str_idx > -1:
        if end_idx == -1:
            return tex[:str_idx]
        elif end_idx < str_idx:
            return remove_content(tex[end_idx + len(end_table):], tex, content)
        else:
            return remove_content(tex[:str_idx] + "\n\n" + \
                                  tex[end_idx + len(end_table):], tex, content)
    else:
        if end_idx != -1:
            return tex[end_idx + len(end_table):]
    return tex

################################################################################

def get_tokens(json_file, context_brat_file,
               add_lines=True, clobber=False, verbose=False):
    
    
    """
    Converts PDF image to PNG Image & Writes Out LaTeX Tokens
    
    Args:
    directory (str) - Name of Directory to Search
    extension (str) - Extension of File to Search
    prefix (str) - Start of Filename to Search.
    
    Returns:
    An iterator of filenames in directory satisfying prefix/extension.
    """
    
    # Store Contents of Text File
    with open(json_file) as f:     # Opens File
        data = json.load(f)        # Loads Data from JSON File
        
        # Extract LaTeX Tokens from Tex File & Write to LST File
        tex = "".join([d.get("value").strip() if d.get("type")=="EscapeSequence"
                       else d.get("value") for d in data])
        
        # Add Line Breaks between Equations
        if add_lines:
            
            # EQUATIONS & LISTS
            for content in [# EQUATION ENVIRONMENTS
                            "equation", "equation*", "eqnarray", "eqnarray*",
                            "align",    "align*",    "gather",   "gather*",
                            "multline", "multline*", "flalign",  "flalign*",
                            "alignat",  "alignat*",  "split",    "split*",
                            "subequations", "subequations*",
                            # LIST STRUCTURES
                            "itemize",  "itemize*",  "enumerate",  "enumerate*",
                            "labeling", "labeling*", "easylist",   "easylist*",
                            "tasks",  "tasks*",  "description",  "description*",
                            # THEOREMS
                            "theorem", "theorem*", "corollary",  "corollary*",
                            "proof",   "proof*",   "lemma",      "lemma*",
                            "remark",  "remark*",  "definition", "definition*",
                            "claim",   "claim*", "prop", "prop*", "thm", "thm*", "rem", "rem*",
                            "proposition", "proposition*",
                            # MISCELLANEOUS
                            "abstract"]:
                
                tex = tex.replace(    "\\begin{{{}}}".format(content),
                                  "\n\n\\begin{{{}}} ".format(content))
                tex = tex.replace("\\end{{{}}} ".format(content),
                                  "\\end{{{}}}".format(content))
                tex = tex.replace(  "\\end{{{}}}".format(content),
                                  "\n\\end{{{}}}\n\n".format(content))
        
            # SECTIONS & CHAPTERS
            for content in ["section", "section*", "subsection", "subsection*",
                            "subsubsection", "subsubsection*", "paragraph",
                            "chapter", "chapter*", "title",   "author", "date"]:
                tex = tex.replace(    "\\{0}{{".format(content),
                                  "\n\n\\{0}{{".format(content))

            # MISCELLANEOUS
            tex = tex.replace("\\item",       "\n\t\\item ")
            tex = tex.replace("\\label{",     "\n\\label{")
            tex = tex.replace("\\\\",         "\\\\\n\t")
            tex = tex.replace("\\maketitle ", "\n\\maketitle\n")
            tex = tex.replace("$$ ", "$$").replace(" $$", "$$").replace("$$", "\n$$\n")
            tex = tex.replace("\\[", "\n\n\\[\n").replace("\\]", "\n\\]\n\n")
    
        # Remove Anything before \begin{document}
        doc_idx =  tex.find("\\begin{document}")
        if doc_idx > -1:
            tex = tex[doc_idx:]
    
        # Remove Tables, Figures
        for content in ["table", "table*", "figure", "figure*", "thebibliography"]:
            tex = remove_content(tex, content=content)

        # Adjusts Spacing Issues
        for num in range(3,6):
            tex = tex.replace("\n"*num, "\n\n")
        tex = tex.replace("\n\n\\end", "\n\\end")
        
        # Print TeX
        if verbose:
            print(tex)
    
        # Removes Brat-Readable File if Clobber set to True
        if clobber:
            remove_file(context_brat_file)
    
        # Writes LaTeX Tokens into Brat-Readable File
        with open(context_brat_file, "w") as text_file:
            print(tex, file=text_file)

    return tex


################################################################################

def main(annot_dir="annotation_data",
         paper_dir="arxiv/output_venti",
         context_file="context_k3.json",
         aabb_file="aabb.png",
         brat_ext=".txt",
         add_lines=True,
         clobber=False,
         verbose=False,
         num_threads=4):
    
    # Remove Annotation Directory if Clobber set to True
    if clobber and os.path.exists(annot_dir) and os.path.isdir(annot_dir):
        shutil.rmtree(annot_dir)
        
    # Walks through paper directory & finds all context json files.
    base, ext = os.path.splitext(context_file)
    json_iter = get_data(paper_dir, extension=ext, prefix=base)

    p = mp.Pool(num_threads)

    # Iterates through All JSON Files
    for json_file in json_iter:
        
        # Brat-Readable Files
        dir       = os.path.dirname(json_file)
        brat_file = os.path.join(dir, base + brat_ext)

        # Creates an Annotation Directories
        create_directory(dir.replace(paper_dir, annot_dir))

        # Retrieves Tokens from JSON File & Saves into a Brat-Readable File
        get_tokens(json_file, brat_file,
                   add_lines=add_lines, clobber=clobber, verbose=verbose)

        # Saves a Copy of the Data into the Annotation Directory
        for file in [json_file, brat_file, os.path.join(dir, aabb_file)]:
            try:
                shutil.copy2(file, dir.replace(paper_dir, annot_dir))
            except:
                print(file, "not available for copy.")

################################################################################

if __name__ == "__main__":
    main(annot_dir="/projects/automates/collect_2019SEPT19/annotation/1801",
         paper_dir="/projects/automates/collect_2019SEPT19/output/1801",
         context_file="context_k3.json",
         brat_ext=".txt",
         add_lines=True,
         clobber=False,
         verbose=False,
         num_threads=8)

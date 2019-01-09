#!/usr/bin/env python

from __future__ import division, print_function

import os
import json
import argparse
import subprocess
import cv2
import jinja2
import numpy as np
from skimage import img_as_ubyte
from pdf2image import convert_from_path
from latex import tokenize, extract_equations, find_main_tex_file



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dirname')
    parser.add_argument('--outdir', default='output')
    parser.add_argument('--template', default='misc/template.tex')
    args = parser.parse_args()
    return args



def render_tex(filename, outdir):
    """render latex document"""
    dirname = os.path.dirname(filename)
    basename = os.path.basename(filename)
    command = ['latexmk', '-outdir=' + outdir, '-pdf', basename]
    returncode = subprocess.call(command, cwd=dirname)
    pdf_name = os.path.join(outdir, os.path.splitext(basename)[0] + '.pdf')
    return pdf_name



def render_equation(equation, template, filename):
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    equation_tex = template.render(equation=equation)
    with open(filename, 'w') as f:
        f.write(equation_tex)
    pdf_name = render_tex(filename, dirname)
    image = get_pages(pdf_name)[0]
    return image



def get_pages(pdf_name):
    pages = []
    for img in convert_from_path(pdf_name):
        page = np.array(img)
        page = cv2.cvtColor(page, cv2.COLOR_BGR2GRAY)
        pages.append(page)
    return pages



def match_template(pages, template):
    best_val = -np.inf
    best_loc = (-1, -1)
    best_page = -1
    h, w = template.shape[:2]
    for i, page in enumerate(pages):
        result = cv2.matchTemplate(page, template, cv2.TM_CCOEFF_NORMED)
        (min_val, max_val, min_loc, max_loc) = cv2.minMaxLoc(result)
        if best_val < max_val:
            best_val = max_val
            best_loc = max_loc
            best_page = i
    upper_left = best_loc
    lower_right = (best_loc[0] + w, best_loc[1] + h)
    return best_val, best_page, upper_left, lower_right



def process_paper(dirname, template, outdir):
    texfile = find_main_tex_file(dirname)
    paper_id = os.path.basename(os.path.normpath(dirname))
    outdir = os.path.abspath(os.path.join(outdir, paper_id))
    # read latex tokens from document
    tokens = tokenize(texfile)
    # extract equations from token stream
    equations = extract_equations(tokens)
    # compile pdf from document
    pdf_name = render_tex(texfile, outdir)
    # retrieve pdf pages as images
    pages = get_pages(pdf_name)
    # load jinja2 template
    template_loader = jinja2.FileSystemLoader(searchpath='.')
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template)
    for (i, (environment_name, eq_toks)) in enumerate(equations):
        eq_tex = ''.join(repr(c) for c in eq_toks)
        eq_name = 'equation%03d' % i
        # ensure directory exists
        dirname = os.path.join(outdir, eq_name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        # write environment name
        fname = os.path.join(outdir, eq_name, 'environment.txt')
        with open(fname, 'w') as f:
            f.write(environment_name)
        # write tex tokens
        fname = os.path.join(outdir, eq_name, 'tokens.json')
        with open(fname, 'w') as f:
            tokens = [dict(type=t.__class__.__name__, value=t.source) for t in eq_toks]
            json.dump(tokens, f)
        # render equation if possible
        if environment_name in ('equation', 'equation*'):
            # make pdf
            fname = os.path.join(outdir, eq_name, 'equation.tex')
            equation = render_equation(eq_tex, template, fname)
            # find page and aabb where equation appears
            match, p, start, end = match_template(pages, equation)
            # write image with aabb
            image = pages[p].copy()
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            cv2.rectangle(image, start, end, (0, 0, 255), 2)
            img_name = os.path.join(outdir, eq_name, 'aabb.png')
            cv2.imwrite(img_name, image)
            # write aabb to file (using relative coordinates)
            fname = os.path.join(outdir, eq_name, 'aabb.tsv')
            h, w = image.shape[:2]
            x1 = start[0] / w
            y1 = start[1] / h
            x2 = end[0] / w
            y2 = end[1] / h
            with open(fname, 'w') as f:
                values = [p, x1, y1, x2, y2]
                tsv = '\t'.join(map(str, values))
                print(tsv, file=f)



if __name__ == '__main__':
    args = parse_args()
    process_paper(args.dirname, args.template, args.outdir)

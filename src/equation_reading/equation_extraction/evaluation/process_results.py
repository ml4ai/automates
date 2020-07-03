# Script for processing the results from encoder-decoder
# The decoder's predictions are provided in one predicted sequence
# per line, tokens separated by whitespace.
# These predictions are compared with the gold versions, which are
# provided in the same format in a separate file.  We produce
# several files for analyzing the results: TODO details

import argparse
import os
import random

import cv2
import numpy as np
import sacrebleu
from matplotlib import pyplot as plt

from data_collection.collect_data import render_equation, mk_template
from utils import load_segments
from utils.image_utils import remove_background, resize, pixel_is_white


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pred', default='/data/pred.txt', help="predictions file")  # set to true to keep tarballs and pdfs
    parser.add_argument('--gold', default='/data/gold.txt', help="gold sequences file")
    parser.add_argument('--outdir', default='/data/output')
    parser.add_argument('--img-sample', type=int, default=0, help="downsample the images for the side by side and overlapping")
    parser.add_argument('--seed', type=int, default=426, help="random seed for image downsampling")
    parser.add_argument('--template', default='misc/template.tex')
    args = parser.parse_args()
    return args

def save_text(filename, texts):
    with open(filename, 'w') as outfile:
        for t in texts:
            outfile.write(t + "\n")


# Take a list of latex eqns (each is a String), a latex template to put them in, and a filename,
# and return a list of images.  Note, if the latex doesn't compile, the image will be None.
# Currently we're not keeping intermediate files.
def mk_images(equations, template, dir, prefix):
    print(f"making {prefix} images...")
    mkdir(dir)
    imgs = []
    for idx, eqn in enumerate(equations):
        tex_filename = os.path.join(dir, "{0}_{1}.tex".format(prefix, idx))
        print(f"making image: {tex_filename}")
        eqn_image = render_equation(dict(equation=eqn), template, filename=tex_filename, keep_intermediate=False)
        if eqn_image is None:
            eqn_image = np.zeros(shape=[50, 100, 3], dtype=np.uint8)
        eqn_image = cv2.cvtColor(eqn_image, cv2.COLOR_BGR2RGBA)
        imgs.append(eqn_image)
    return imgs

def score(predicted, predicted_imgs, gold, gold_imgs):
    scores = dict()
    # BLEU
    bleu = sacrebleu.raw_corpus_bleu(predicted, [gold]).score
    scores['bleu'] = bleu
    # todo: String edit distance
    # todo: Image difference
    return scores

def mk_score_report(scores):
    print(scores)
    return str([(k,v) for k,v in scores.items()]) #fixme

def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def mk_results_dirs(outdir):
    inputdir = os.path.join(outdir, "input")
    reportsdir = os.path.join(outdir, "reports")
    mkdir(outdir)
    mkdir(inputdir)
    mkdir(reportsdir)
    return inputdir, reportsdir

def save_results(outdir, report, side_by_side, overlapping, pred, gold):
    inputdir, reportsdir = mk_results_dirs(outdir)
    # Save copies of the original input
    save_text(os.path.join(inputdir, "predictions.txt"), pred)
    save_text(os.path.join(inputdir, "gold.txt"), gold)
    # Save the reports
    # TODO this isn't a string yet
    save_text(os.path.join(reportsdir, "score_report.txt"), [report])
    overlapping.savefig(os.path.join(reportsdir, "overlap_and_diff.pdf"), format='pdf', dpi=1200)
    side_by_side.savefig(os.path.join(reportsdir, "side_by_side.pdf"), format='pdf', dpi=1200)

def generate_side_by_side(predicted_imgs, gold_imgs, indices):
    interleaved = [img for pair in zip(gold_imgs, predicted_imgs) for img in pair]
    # TODO: revisit -- temporary
    columns = 2
    rows = len(gold_imgs)

    fig = plt.figure(figsize=(8, 0.8*rows))

    # add images as subplots
    for i in range(0, min(columns * rows, len(interleaved))):
        img = interleaved[i]
        fig.add_subplot(rows, columns, i+1)
        plt.imshow(img)
        if i%2==0:
            # plt.title(str(indices[int(i / 2)]))
            plt.ylabel(str(indices[int(i/2)]), rotation=90)
            plt.tight_layout()
        plt.xticks([])
        plt.yticks([])
    fig.suptitle("Side-by-Side comparison of gold (left) and predicted (right)")
    return fig

def generate_overlapping(predicted_imgs, gold_imgs, indices):
    diffs = []
    height, width = predicted_imgs[0].shape[:2]
    for i, pred in enumerate(predicted_imgs):
        pred = remove_background(pred, 'red')
        gold = remove_background(gold_imgs[i], 'blue')

        for row in range(height):
            for col in range(width):
                if gold[row][col][3] == 0 and pred[row][col][3] == 255:
                    gold[row][col] = pred[row][col]
                elif pixel_is_white(gold[row][col]) and pixel_is_white(pred[row][col]):
                    pass
                elif gold[row][col][3] == 255 and pred[row][col][3] == 255:
                    gold[row][col] = [0, 0, 0, 255]

        diffs.append(gold)

    # TODO: revisit -- temporary
    fig = plt.figure(figsize=(8, 8))
    columns = 3
    rows = 5

    # add images as subplots
    for i in range(0, min(columns * rows, len(diffs))):
        img = diffs[i]
        fig.add_subplot(rows, columns, i + 1)
        plt.imshow(img)
        plt.xlabel(str(indices[i]))
        plt.xticks([])
        plt.yticks([])
    fig.suptitle("Overlap between gold and predicted.\nGold-only is shown in blue, predicted-only in red, and overlap in black.")
    return fig


if __name__ == '__main__':
    args = parse_args()
    # Set the random seed, used for the image downsampling
    if args.img_sample > 0:
        random.seed(args.seed)
        np.random.seed(args.seed)

    # Load the predicted and gold equations
    predicted = load_segments(args.pred)
    gold = load_segments(args.gold)

    # render the latex equations, returning None if compilation failed
    template = mk_template(args.template)

    selected_indices = range(len(gold))
    if args.img_sample > 0:
        indices = np.arange(0,len(predicted))
        np.random.shuffle(indices)
        selected_indices = sorted(indices[:args.img_sample])
        predicted_sample = np.array(predicted)[selected_indices]
        gold_sample = np.array(gold)[selected_indices]
    else:
        predicted_sample = predicted
        gold_sample = gold

    # todo: option to load the images already made?
    predicted_imgs = mk_images(predicted_sample, template, '/Users/bsharp/tmp', "pred") #fixme with qqc with full path
    gold_imgs = mk_images(gold_sample, template, '/Users/bsharp/tmp', "gold")


    # Calculate all scores, where scores: Dict[String, Float]
    scores = score(predicted, predicted_imgs, gold, gold_imgs)

    # Output the various score reports and analysis documents
    report = mk_score_report(scores)

    predicted_imgs, gold_imgs, _, _ = resize(predicted_imgs, gold_imgs, num_channels=4)

    side_by_side = generate_side_by_side(predicted_imgs, gold_imgs, selected_indices)
    # overlapping = generate_overlapping(predicted_imgs, gold_imgs, selected_indices)
    overlapping = side_by_side

    save_results(args.outdir, report, side_by_side, overlapping, predicted, gold)
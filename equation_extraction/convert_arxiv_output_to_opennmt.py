import os
import glob
import sys
import json
import numpy as np
# from sklearn.model_selection import train_test_split
from utils import run_command

def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def get_tex(fn):
    with open(fn) as fi:
        tokens = json.load(fi)
    token_values = [t["value"] for t in tokens]
    return "".join(token_values)

def save_text(filename, texts):
    with open(filename, 'w') as outfile:
        for t in texts:
            outfile.write(t + "\n")

def gather_opennmt_data(month_path, outdir, imgs_dir, logfile):
    # makes a log file, needs to be run with docker, so the path is based on /data
    # todo: make an arg?
    # month_dirs = os.listdir(parent_dir)
    month = os.path.basename(month_path)
    counter = 0
    img_names = []
    eqn_strings = []
    # for month in month_dirs:
    print "processing month:", month
    # make output dir for month
    imgs_month_out = os.path.join(imgs_dir, month)
    mkdir(imgs_month_out)
    # keep an absolute path

    if os.path.isdir(month_path):
        paper_dirs = os.listdir(month_path)
        for paper in paper_dirs:
            # keep an absolute path
            print "processing paper:", paper
            paper_path = os.path.join(month_path, paper)
            if os.path.isdir(paper_path):
                equation_dirs = glob.glob(os.path.join(paper_path, "equation*"))
                for eqn_path in equation_dirs:
                    # This time, bc of glob, the eqn_path is the absolute path
                    # so here we get the base name for the equation
                    eqndir = os.path.basename(eqn_path)
                    eqn_tex_file = os.path.join(eqn_path, "tokens.json")
                    eqn_pdf_file = os.path.join(eqn_path, "equation.pdf")
                    # if these files exist:
                    if os.path.exists(eqn_tex_file) and os.path.exists(eqn_pdf_file):
                        equation_string = get_tex(eqn_tex_file)
                        # make filename with provenance
                        basename = '{0}_{1}'.format(paper, eqndir)
                        # keep the relative name bc the system will be looking in the `images` subdir
                        relative_png_name = os.path.join(month, basename + ".png")
                        full_png_name = os.path.join(imgs_dir, relative_png_name)
                        # Put a png version in the right place
                        run_command(["convert", "-background", "white", "-alpha", "remove", "-alpha", "off", "-density", "200", eqn_pdf_file, "-quality", "100", full_png_name], "/", logfile)
                        # Save the file names and the strings for the instances
                        img_names.append(relative_png_name)
                        eqn_strings.append(equation_string)
                        counter+=1
    print("Processed {0} equation instances from {1}!".format(counter, month))

    save_text(os.path.join(outdir, month + "_src_images.txt"), img_names)
    save_text(os.path.join(outdir, month + "_tgt_equations.txt"), eqn_strings)

    # Train/dev/test folds
    # assert len(img_names) == len(eqn_strings)
    # indices = range(len(img_names))
    # # 0.7 for train, 0.15 dev, 0.15 test
    # train_indices, devtest_indices = train_test_split(indices, train_size=0.7)
    # print("There are {0} train data points".format(len(train_indices)))
    # dev_indices, test_indices = train_test_split(devtest_indices, train_size=0.5)
    # print("There are {0} dev data points".format(len(dev_indices)))
    # print("There are {0} test data points".format(len(test_indices)))
    # # Image file names
    # img_names = np.array(img_names)
    # tr_imgs = img_names[train_indices]
    # dev_imgs = img_names[dev_indices]
    # test_imgs = img_names[test_indices]
    #
    # # Equation tokens
    # eqn_strings = np.array(eqn_strings)
    # tr_eqns = eqn_strings[train_indices]
    # dev_eqns = eqn_strings[dev_indices]
    # test_eqns = eqn_strings[test_indices]
    #
    # # Output:
    # # Source: Images
    # save_text(os.path.join(outdir, month + 'partial_src-train.txt'), tr_imgs)
    # save_text(os.path.join(outdir, month + 'partial_src-val.txt'), dev_imgs)
    # save_text(os.path.join(outdir, month + 'partial_src-test.txt'), test_imgs)
    # # Target: Tex
    # save_text(os.path.join(outdir, month + 'partial_tgt-train.txt'), tr_eqns)
    # save_text(os.path.join(outdir, month + 'partial_tgt-val.txt'), dev_eqns)
    # save_text(os.path.join(outdir, month + 'partial_tgt-test.txt'), test_eqns)

if __name__ == '__main__':
    args = sys.argv
    parent_dir = args[1]
    outdir = args[2]
    logsdir = args[3]

    imgs_dir = os.path.join(outdir, "images")
    mkdir(imgs_dir)

    mkdir(logsdir)
    mkdir(outdir)
    month = os.path.basename(parent_dir)
    gather_opennmt_data(parent_dir, outdir, imgs_dir, os.path.join(logsdir, month + '_formatting_for_opennmt_stdout.log'))
 

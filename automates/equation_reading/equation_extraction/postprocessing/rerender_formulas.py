import argparse
import os
from itertools import izip

import cv2
from skimage import io

from data_collection.collect_data import render_equation, mk_template
from postprocessing.augmentation_utils import select_random_augmentation
from utils import run_command


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default='data/src.txt', help='File with image paths, one per line, already pruned')
    parser.add_argument('--tgt', default='data/tgt.txt', help='File with latex formulas, one per line, already normalized and pruned')
    parser.add_argument('--imgdir', default='data/images', help='parent directory with the original images, orig image paths in src file should be relative to here')
    parser.add_argument('--src-out', default='data/src_augmented.txt', help='File with new image paths, one per line (to be appended to previous)')
    parser.add_argument('--tgt-out', default='data/tgt_augmented.txt', help='File with `new` formulas, to maintain parallelness with the src')
    parser.add_argument('--img-out', default='augmented', help='directory (relative to the opennmt data images dir) to store the augmented images')
    parser.add_argument('--template', default='misc/template_font.tex')
    args = parser.parse_args()
    return args


def rerender_font_size(tgt, src, tgt_out_name, src_out_name, img_out, template):
    template = mk_template(template)
    font_sizes = ['10pt', '11pt', '12pt']
    with open(src, 'r') as orig_src, open(tgt, 'r') as orig_tgt, open(src_out_name, 'w') as src_out, open(tgt_out_name, 'w') as tgt_out:
        for src_line, tgt_line in izip(orig_src, orig_tgt):
            equation_tokens = tgt_line.strip()
            orig_image_base = src_line.strip()[:-4]
            for size in font_sizes:
                tmp_tex_filename = os.path.join(img_out, "{0}-{1}.tex".format(orig_image_base, size))
                template_args = dict(equation=equation_tokens, fontsize=size)
                sized_image = render_equation(template_args, template, tmp_tex_filename, keep_intermediate=False)
                # Save the new image
                # fixme: is this a reasonable way to make the pngs?
                img_name = tmp_tex_filename[:-4] + ".png"
                cv2.imwrite(img_name, sized_image)
                # Save the img path and the tokens to the data augmentation src and tgt files
                src_out.write(img_name + "\n")
                tgt_out.write(tgt_line)

def add_padding(tgt, src, tgt_out_name, src_out_name, img_out, template):
    template = mk_template(template)
    WHITE = [255 * 3]
    padding = [10, 15]
    with open(src, 'r') as orig_src, open(tgt, 'r') as orig_tgt, open(src_out_name, 'w') as src_out, open(tgt_out_name, 'w') as tgt_out:
        for src_line, tgt_line in izip(orig_src, orig_tgt):
            equation_tokens = tgt_line.strip()
            orig_image_base = src_line.strip()[:-4]
            for pad in padding:
                tmp_tex_filename = os.path.join(img_out, "{0}-{1}.tex".format(orig_image_base, '10pt'))
                template_args = dict(equation=equation_tokens, fontsize='10pt')
                base_image = render_equation(template_args, template, tmp_tex_filename, keep_intermediate=False)
                # Save the new image
                # fixme: is this a reasonable way to make the pngs?
                img_name_base = tmp_tex_filename[:-4] + ".png"
                cv2.imwrite(img_name_base, base_image)
                # Save the img path and the tokens to the data augmentation src and tgt files
                src_out.write(img_name_base + "\n")
                tgt_out.write(tgt_line)
                # Pad

                img_pad = cv2.copyMakeBorder(base_image, pad, 0, pad, 0, cv2.BORDER_CONSTANT,
                                         value=WHITE)
                img_name_pad = tmp_tex_filename[:-4] + "-pad{0}.png".format(pad)
                cv2.imwrite(img_name_pad, img_pad)
                # Save the img path and the tokens to the data augmentation src and tgt files
                src_out.write(img_name_pad + "\n")
                tgt_out.write(tgt_line)

def degrade(tgt, src, tgt_out_name, src_out_name, img_out, template):
    template = mk_template(template)
    densities = [200, 100]
    with open(src, 'r') as orig_src, open(tgt, 'r') as orig_tgt, open(src_out_name, 'w') as src_out, open(tgt_out_name, 'w') as tgt_out:
        for src_line, tgt_line in izip(orig_src, orig_tgt):
            equation_tokens = tgt_line.strip()
            orig_image_base = src_line.strip()[:-4]
            for density in densities:
                tmp_tex_filename = os.path.join(img_out, "{0}-{1}.tex".format(orig_image_base, '10pt'))
                template_args = dict(equation=equation_tokens, fontsize='10pt')
                base_image = render_equation(template_args, template, tmp_tex_filename, keep_intermediate=False)
                pdf_name = tmp_tex_filename[:-4] + ".pdf"
                img_name_density = tmp_tex_filename[:-4] + "-dens{0}.png".format(density)
                # Save the img path and the tokens to the data augmentation src and tgt files
                run_command(["convert", "-background", "white", "-alpha", "remove", "-alpha", "off", "-density", str(density),
                     pdf_name, "-quality", "100", img_name_density], "/", "/data/log")
                src_out.write(img_name_density + "\n")
                tgt_out.write(tgt_line)


def augment_randomly(src, tgt, imgdir, src_out_name, tgt_out_name, img_out):
    with open(src, 'r') as orig_src, open(tgt, 'r') as orig_tgt, open(src_out_name, 'w') as src_out, open(tgt_out_name, 'w') as tgt_out:
        for src_line, tgt_line in izip(orig_src, orig_tgt):

            orig_image_rel_path = src_line.strip() # e.g., 1801/1801.04079_equation0252.png
            orig_image_abs_path = os.path.join(imgdir, orig_image_rel_path)
            orig_image_base = orig_image_rel_path[:-4] # e.g., 1801/1801.04079_equation0252

            # Load the image
            orig_image = io.imread(orig_image_abs_path)
            # The skeleton augmentation requires for there to be more than one color in the image,
            # but more broadly, if the image is all one color, it doesn't make sense to augment it
            if orig_image.min() != orig_image.max():

                # Choose an augmentation (flip a coin)
                augmented_image, augmentation_string = select_random_augmentation(orig_image)

                # Augmented image name and paths
                img_out_subdir = os.path.basename(img_out)
                augmented_img_rel_path = orig_image_base + "_{0}.png".format(augmentation_string)
                augmented_img_abs_path = os.path.join(img_out, augmented_img_rel_path)
                # The augmented images will be in a subdir, so include that subdir in the line written to src file
                augmented_im_src_line = os.path.join(img_out_subdir, augmented_img_rel_path) + "\n"

                # Save
                io.imsave(augmented_img_abs_path, augmented_image)

                # Save the relative img path and the tokens to the data augmentation src and tgt files
                src_out.write(augmented_im_src_line)
                tgt_out.write(tgt_line)



if __name__ == '__main__':
    args = parse_args()
    augment_randomly(args.src, args.tgt, args.imgdir, args.src_out, args.tgt_out, args.img_out)

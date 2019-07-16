import argparse
import cv2
import jinja2
import os
from itertools import izip
from utils import render_equation


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tgt', default='data/tgt.txt', help='File with latex formulas, one per line, already normalized and pruned')
    parser.add_argument('--src', default='data/src.txt', help='File with image paths, one per line, already pruned')
    parser.add_argument('--tgt-out', default='data/tgt_augmented.txt', help='File with `new` formulas, to maintain parallelness with the src')
    parser.add_argument('--src-out', default='data/src_augmented.txt', help='File with new image paths, one per line (to be appended to previous)')
    parser.add_argument('--img-out', default='augmented', help='directory (relative to the opennmt data images dir) to store the augmented images')
    parser.add_argument('--template', default='misc/template_font.tex')
    args = parser.parse_args()
    return args


def rerender_font_size(tgt, src, tgt_out_name, src_out_name, img_out, template):
    font_sizes = ['10', '11', '12']
    with open(src, 'r') as orig_src, open(tgt, 'r') as orig_tgt, open(src_out_name, 'w') as src_out, open(tgt_out_name, 'w') as tgt_out:
        for src_line, tgt_line in izip(orig_src, orig_tgt):
            equation_tokens = tgt_line.strip()
            orig_image_base = src_line.strip()[:-4]
            for size in font_sizes:
                tmp_tex_filename = os.path.join(img_out, "{0}-{1}pt.tex".format(orig_image_base, size))
                template_args = dict(equation=equation_tokens, fontsize=size)
                sized_image = render_equation(template_args, template, tmp_tex_filename, keep_intermediate=False)
                # Save the new image
                # fixme: is this a reasonable way to make the pngs?
                img_name = tmp_tex_filename[:-4] + ".png"
                cv2.imwrite(img_name, sized_image)
                # Save the img path and the tokens to the data augmentation src and tgt files
                src_out.write(img_name + "\n")
                tgt_out.write(tgt_line)


if __name__ == '__main__':
    args = parse_args()
    # font size
    rerender_font_size(args.tgt, args.src, args.tgt_out, args.src_out, args.img_out, args.template)

    # pad?
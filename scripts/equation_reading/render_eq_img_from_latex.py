# -----------------------------------------------------------------------------
# Script to read equation latex from source file (one eqn per line)
# and render each equation as a png
#
# NOTE: Assumes availability of ImageMagick: https://imagemagick.org/index.php
# -----------------------------------------------------------------------------

import os
import subprocess


# -----------------------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------------------

# NOTE: Must be updated to your local!
ASKE_GOOGLE_DRIVE_ROOT = '/Users/claytonm/Google Drive/ASKE-AutoMATES'

EQN_SOURCE_ROOT = os.path.join(ASKE_GOOGLE_DRIVE_ROOT, 'Data/Mini-SPAM/eqns/SPAM/PET')
PETPT_ROOT = os.path.join(EQN_SOURCE_ROOT, 'PETPT')


# -----------------------------------------------------------------------------
# Render image from latex
# -----------------------------------------------------------------------------

def standalone_eq_template(eqn):
    template = '\\documentclass{standalone}\n' \
               '\\usepackage{amsmath}\n' \
               '\\usepackage{amssymb}\n' \
               '\\begin{document}\n' \
               f'$\\displaystyle {{{{ {eqn} }}}} $\n' \
               '\\end{document}'
    return template


def render_image_from_latex(latex_src, eqn_tex_dst_root, image_dst_root, verbose=False, test_p=True):
    """

    Args:
        latex_src: filepath to file containing single latex equation on each line
        eqn_tex_dst_root: root path for individual latex .tex files (1 per eqn)
        image_dst_root: root path for generated .png files
        verbose:
        test_p: flag for whether to run in test mode (don't actually generate anything)

    Returns:

    """

    eqn_tex_dst_root = os.path.abspath(eqn_tex_dst_root)

    if not test_p:
        if not os.path.exists(eqn_tex_dst_root):
            os.makedirs(eqn_tex_dst_root)

    image_dst_root = os.path.abspath(image_dst_root)

    if not test_p:
        if not os.path.exists(image_dst_root):
            os.makedirs(image_dst_root)

    if verbose:
        print(f'latex_src: {latex_src}')
        print(f'eqn_tex_dst_root: {eqn_tex_dst_root}')
        print(f'image_dst_root: {image_dst_root}')

    with open(latex_src, 'r') as fin:
        for i, line in enumerate(fin.readlines()):
            eqn_latex = line.strip('\n')
            latex_output = standalone_eq_template(eqn_latex)
            if verbose:
                print('-'*20, i)

            eqn_tex_file = os.path.join(eqn_tex_dst_root, f'{i}.tex')

            if verbose:
                print(f'writing {eqn_tex_file}')
            if not test_p:
                with open(eqn_tex_file, 'w') as fout:
                    fout.write(latex_output)

            command_args = ['pdflatex', '-output-directory', eqn_tex_dst_root, eqn_tex_file]

            if verbose:
                print(f'suprocess.run({command_args})')
            if not test_p:
                subprocess.run(command_args)
                if verbose:
                    print('    after subprocess.run')
                # cleanup
                os.remove(os.path.join(eqn_tex_dst_root, f'{i}.aux'))
                os.remove(os.path.join(eqn_tex_dst_root, f'{i}.log'))

            eqn_pdf_file = os.path.join(eqn_tex_dst_root, f'{i}.pdf')
            eqn_png_file = os.path.join(image_dst_root, f'{i}.png')

            command_args = ['convert',
                            '-background', 'white', '-alpha',
                            'remove', '-alpha', 'off',
                            '-density', '200',
                            '-quality', '100',
                            f'{eqn_pdf_file}', f'{eqn_png_file}']

            if verbose:
                print(f'suprocess.run({command_args})')
            if not test_p:
                subprocess.run(command_args)
                if verbose:
                    print('    after subprocess.run')


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # TODO: provide proper cli interface
    PETPT_LATEX_SOURCE = os.path.join(PETPT_ROOT, 'PETPT_equations.txt')
    PETPT_EQN_TEX_DST_ROOT = os.path.join(os.path.join(PETPT_ROOT, 'manual_latex'), 'tex')
    PETPT_IMAGE_DST_ROOT = os.path.join(PETPT_ROOT, 'manual_eqn_images')
    render_image_from_latex(PETPT_LATEX_SOURCE,
                            PETPT_EQN_TEX_DST_ROOT,
                            PETPT_IMAGE_DST_ROOT,
                            verbose=True,
                            test_p=False)

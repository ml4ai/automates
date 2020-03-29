# -----------------------------------------------------------------------------
# Script to read equation latex from source file (one eqn per line)
# and render each equation as a png
#
# NOTE: Assumes availability of ImageMagick: https://imagemagick.org/index.php
# -----------------------------------------------------------------------------

import os
import src.equation_reading.equation_extraction.render_image_from_latex as rifl


# -----------------------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------------------

# NOTE: Must be updated to your local!
ASKE_GOOGLE_DRIVE_ROOT = '/Users/claytonm/Google Drive/ASKE-AutoMATES'

MODEL_ROOT = os.path.join(ASKE_GOOGLE_DRIVE_ROOT, 'Data/Mini-SPAM/eqns/SPAM/PET')
PETPT_ROOT = os.path.join(MODEL_ROOT, 'PETPT')


# -----------------------------------------------------------------------------
# Render image from latex
# -----------------------------------------------------------------------------

def render_images_for_model(model_root, model_name, verbose, test_p):
    model_latex_source = os.path.join(model_root, f'{model_name}_equations.txt')
    model_eqn_tex_dst_root = os.path.join(os.path.join(model_root, 'manual_latex'), 'tex')
    model_image_dst_root = os.path.join(model_root, 'manual_eqn_images')
    rifl.render_image_from_latex(model_latex_source,
                                 model_eqn_tex_dst_root,
                                 model_image_dst_root,
                                 verbose=verbose, test_p=test_p)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # TODO: provide proper cli interface

    render_images_for_model(PETPT_ROOT, 'PETPT', verbose=True, test_p=False)

    '''
    PETPT_LATEX_SOURCE = os.path.join(PETPT_ROOT, 'PETPT_equations.txt')
    PETPT_EQN_TEX_DST_ROOT = os.path.join(os.path.join(PETPT_ROOT, 'manual_latex'), 'tex')
    PETPT_IMAGE_DST_ROOT = os.path.join(PETPT_ROOT, 'manual_eqn_images')
    render_image_from_latex(PETPT_LATEX_SOURCE,
                            PETPT_EQN_TEX_DST_ROOT,
                            PETPT_IMAGE_DST_ROOT,
                            verbose=True,
                            test_p=False)
    '''

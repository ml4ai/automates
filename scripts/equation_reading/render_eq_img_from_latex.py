# -----------------------------------------------------------------------------
# Script to read equation latex from source file (one eqn per line)
# and render each equation as a png
#
# NOTE: Assumes availability of:
#     pdflatex
#     ImageMagick (for the 'convert' command): https://imagemagick.org/index.php
#
# Usage:
# TODO provide better cli interface
# Currently: comment out the line(s) for the corresponding model(s)
#   under __main__ that you want to process
#
# What it does:
# For each latex source line in <model>_equations.txt:
#     ... in the directory: <model>/manual_latex/tex/
#       Create a corresponding <#>.tex file with the latex line inside
#         a latex 'standalone' template
#       Calls pdflatex (subprocess) to render the <#>.tex as a PDF in <#>.pdf
#     Calls convert (subprocess) to convert the <#>.pdf to a <#>.png
#       ... where the <#>.png is saved in the directory:
#         <model>/manual_eqn_images/
#
# -----------------------------------------------------------------------------

import os
import automates.utils.parameters as parameters
import automates.equation_reading.equation_extraction.render_image_from_latex as rifl


# -----------------------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------------------

# NOTE: Must be updated to your local!
ASKE_GOOGLE_DRIVE_ROOT = parameters.get()['AUTOMATES_DATA']

MODEL_ROOT = os.path.join(ASKE_GOOGLE_DRIVE_ROOT, 'Mini-SPAM/eqns/SPAM/PET')
PETPT_ROOT = os.path.join(MODEL_ROOT, 'PETPT')
PETASCE_ROOT = os.path.join(MODEL_ROOT, 'PETASCE')
PETDYN_ROOT = os.path.join(MODEL_ROOT, 'PETDYN')
PETMEY_ROOT = os.path.join(MODEL_ROOT, 'PETMEY')
PETPEN_ROOT = os.path.join(MODEL_ROOT, 'PETPEN')
PETPNO_ROOT = os.path.join(MODEL_ROOT, 'PETPNO')


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

    print('render_images_for_model(): NEED TO UNCOMMENT')
    # UNCOMMENT the line(s) for the model(s) you want to process
    # render_images_for_model(PETPT_ROOT, 'PETPT', verbose=True, test_p=False)
    # render_images_for_model(PETASCE_ROOT, 'PETASCE', verbose=True, test_p=False)
    # render_images_for_model(PETDYN_ROOT, 'PETDYN', verbose=True, test_p=False)
    # render_images_for_model(PETMEY_ROOT, 'PETMEY', verbose=True, test_p=False)
    # render_images_for_model(PETPEN_ROOT, 'PETPEN', verbose=True, test_p=False)
    # render_images_for_model(PETPNO_ROOT, 'PETPNO', verbose=True, test_p=False)x

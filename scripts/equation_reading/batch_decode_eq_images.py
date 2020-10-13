# -----------------------------------------------------------------------------
# Script to batch decode PNG images equations to extract equation latex
#
# NOTE: Assumes eqdec app is running. See:
# https://github.com/ml4ai/automates/blob/master/src/equation_reading/equation_translation/eqdec/readme.txt
#
# Also, includes running render_image_from_latex, which requires:
#     pdflatex
#     ImageMagick (for the 'convert' command): https://imagemagick.org/index.php
#
# Usage:
# TODO provide better cli interface
# Currently: comment out the line(s) for the corresponding model(s)
#   under __main__ that you want to process
#
# What it does:
# Executes eqdec across the PNGs under the specified <model>/manual_eqn_images/
# Then calls render_decoded_eqns on the extracted json (containing the decoded latex
# -----------------------------------------------------------------------------

import os
import json
import re
import automates.utils.parameters as parameters
import automates.equation_reading.equation_translation.img_translator as decode
import automates.equation_reading.equation_extraction.render_image_from_latex as rifl

# -----------------------------------------------------------------------------
# NOTE: Must have eqdec app running. See:
# https://github.com/ml4ai/automates/blob/master/src/equation_reading/equation_translation/eqdec/readme.txt
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------------------

ASKE_GOOGLE_DRIVE_DATA_ROOT = parameters.get()['AUTOMATES_DATA']

MODEL_ROOT_PET = os.path.join(ASKE_GOOGLE_DRIVE_DATA_ROOT, 'Mini-SPAM/eqns/SPAM/PET')
PETPT_ROOT = os.path.join(MODEL_ROOT_PET, 'PETPT')
PETASCE_ROOT = os.path.join(MODEL_ROOT_PET, 'PETASCE')
PETDYN_ROOT = os.path.join(MODEL_ROOT_PET, 'PETDYN')
PETMEY_ROOT = os.path.join(MODEL_ROOT_PET, 'PETMEY')
PETPEN_ROOT = os.path.join(MODEL_ROOT_PET, 'PETPEN')
PETPNO_ROOT = os.path.join(MODEL_ROOT_PET, 'PETPNO')

MODEL_ROOT_COVID = os.path.join(ASKE_GOOGLE_DRIVE_DATA_ROOT, 'COVID-19')
CHIME_ROOT = os.path.join(MODEL_ROOT_COVID, 'CHIME/eqns/2020-08-04-CHIME-docs')

MODEL_ROOT_ASKEE = os.path.join(os.path.join(ASKE_GOOGLE_DRIVE_DATA_ROOT, 'ASKE-E'), 'epi-platform-wg')
ASKEE_SEIR_7_ROOT = os.path.join(MODEL_ROOT_ASKEE, 'eqns/SEIR-7')
ASKEE_SEIR_8_ROOT = os.path.join(MODEL_ROOT_ASKEE, 'eqns/SEIR-8')
ASKEE_SEIR_9_ROOT = os.path.join(MODEL_ROOT_ASKEE, 'eqns/SEIR-9')

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

# https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside

def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


def natural_sort_filenames(root, extension='.png'):
    """
    *Naturally* sorts files with extension found in root dir
    Natural sort: https://en.wikipedia.org/wiki/Natural_sort_order

    Args:
        root: path to directory
        extension: filename extension

    Returns:

    """
    files = list()
    for file in os.listdir(root):
        if file.endswith(extension):
            files.append(file)
    files.sort(key=natural_keys)
    return files


# -----------------------------------------------------------------------------
# Batch decode
# -----------------------------------------------------------------------------

def batch_decode(img_src_root, dec_dst_root, verbose=False):

    dec_dst_json_root = os.path.join(dec_dst_root, 'json')
    dec_latex_file = os.path.join(dec_dst_root, 'decoded_equations.txt')

    latex_src_list = list()

    dec_dst_json_root = os.path.abspath(dec_dst_json_root)

    if not os.path.exists(dec_dst_json_root):
        os.makedirs(dec_dst_json_root)

    # Ensure the filenames are naturally sorted, or else the
    # non-named equations will end up in the wrong order!
    files = natural_sort_filenames(img_src_root, extension='.png')

    # for file in files:
    #     print(file)

    for file in files:

        if file in []:  # ['1.png', '2.png'] # ['47.png']:  # HACK: skip list

            latex_src_list.append('None')

        else:

            if verbose:
                print('-'*20, file)

            json_path = decode.png2latex(os.path.join(img_src_root, file), dec_dst_json_root)

            if verbose:
                print(json_path)

            with open(json_path) as json_file:
                jeq = json.load(json_file)

            if verbose:
                # pprint.pprint(jeq)
                print(jeq['latex'])

            latex_src_list.append(jeq['latex'])

    if verbose:
        print('='*20)
        print(f'Writing {dec_latex_file}')

    with open(dec_latex_file, 'w') as fout:
        for latex_src in latex_src_list:
            fout.write(latex_src + '\n')

    return latex_src_list


def render_decoded_eqns(decoded_images_root, verbose, test_p):
    model_latex_source = os.path.join(decoded_images_root, f'decoded_equations.txt')
    model_eqn_tex_dst_root = os.path.join(decoded_images_root, 'tex')
    rifl.render_image_from_latex(model_latex_source,
                                 model_eqn_tex_dst_root,
                                 decoded_images_root,
                                 verbose=verbose, test_p=test_p)


def process_model(model_root, verbose, test_p):
    if verbose:
        print('='*20, f'\nBatch decode equation images: {model_root}')
    PETASCE_EQN_IMG_SRC_ROOT = os.path.join(model_root, 'manual_eqn_images')
    PETASCE_DECODED_ROOT = os.path.join(model_root, 'decoded_images')
    batch_decode(PETASCE_EQN_IMG_SRC_ROOT, PETASCE_DECODED_ROOT, verbose=verbose)
    render_decoded_eqns(PETASCE_DECODED_ROOT, verbose=verbose, test_p=test_p)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # TODO: provide proper cli interface

    print('batch_decode_eq_images(): NEED TO UNCOMMENT')
    # uncomment the line(s) for the model(s) you want to process
    # process_model(PETPT_ROOT, verbose=True, test_p=False)
    # process_model(PETASCE_ROOT, verbose=True, test_p=False)
    # process_model(PETDYN_ROOT, verbose=True, test_p=False)
    # process_model(PETMEY_ROOT, verbose=True, test_p=False)
    # process_model(PETPEN_ROOT, verbose=True, test_p=False)
    # process_model(PETPNO_ROOT, verbose=True, test_p=False)
    # process_model(CHIME_ROOT, verbose=True, test_p=False)
    # process_model(ASKEE_SEIR_7_ROOT, verbose=True, test_p=False)
    # process_model(ASKEE_SEIR_8_ROOT, verbose=True, test_p=False)
    process_model(ASKEE_SEIR_9_ROOT, verbose=True, test_p=False)

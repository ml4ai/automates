import os
import json
import re
import src.equation_reading.equation_translation.img_translator as decode
import src.equation_reading.equation_extraction.render_image_from_latex as rifl

# -----------------------------------------------------------------------------
# NOTE: Must have eqdec app running. See:
# https://github.com/ml4ai/automates/blob/master/src/equation_reading/equation_translation/eqdec/readme.txt
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------------------

# NOTE: Must be updated to your local!
ASKE_GOOGLE_DRIVE_ROOT = '/Users/claytonm/Google Drive/ASKE-AutoMATES'

MODEL_ROOT = os.path.join(ASKE_GOOGLE_DRIVE_ROOT, 'Data/Mini-SPAM/eqns/SPAM/PET')
PETPT_ROOT = os.path.join(MODEL_ROOT, 'PETPT')


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


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # TODO: provide proper cli interface
    PETPT_EQN_IMG_SRC_ROOT = os.path.join(PETPT_ROOT, 'manual_eqn_images')
    PETPT_DECODED_ROOT = os.path.join(PETPT_ROOT, 'decoded_images')
    batch_decode(PETPT_EQN_IMG_SRC_ROOT, PETPT_DECODED_ROOT, verbose=True)
    render_decoded_eqns(PETPT_DECODED_ROOT, verbose=True, test_p=False)

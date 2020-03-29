import os
import re


# -----------------------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------------------

# NOTE: Must be updated to your local!
ASKE_GOOGLE_DRIVE_ROOT = '/Users/claytonm/Google Drive/ASKE-AutoMATES'

MODEL_ROOT = os.path.join(ASKE_GOOGLE_DRIVE_ROOT, 'Data/Mini-SPAM/eqns/SPAM/PET')
PETPT_ROOT = os.path.join(MODEL_ROOT, 'PETPT')


# -----------------------------------------------------------------------------
# COMPARISON_SPEC
# -----------------------------------------------------------------------------

def generate_model_spec(model_root, model_name):
    return {'model': f'{model_name}',
            'src_latex': os.path.join(model_root, f'{model_name}_equations.txt'),
            'src_images_root': os.path.join(model_root, 'manual_eqn_images'),
            'dec_latex': os.path.join(model_root, 'decoded_equations.txt'),
            'dec_images_root': os.path.join(model_root, 'decoded_images')}


PETPT_SPEC = generate_model_spec(PETPT_ROOT, 'PETPT')

COMPARISON_SPEC = (PETPT_SPEC, )


# -----------------------------------------------------------------------------
# HTML
# -----------------------------------------------------------------------------

def html_outer(body):
    return f"""
<html>
<body>

{body}

</body>
</html>
"""


def html_model(model_name, body):
    return f"""
<h2>{model_name}</h2>
<table border="1" cellpadding="4" cellspacing="1">
<tr>
<th>Eqn Num</th>
<th>Original Image</th>
<th>Decoded Image</th>
</tr>

{body}

</table>
"""


def html_eqn_comparison(eqn_num, eqn_src, eqn_dec):
    return tr(td(eqn_num) + td(eqn_src) + td(eqn_dec))


def html_image(img_src, alt='None', width='400'):
    return f'<img src="{img_src}" alt="{alt}" width="{width}">'


def tr(value):
    return f'<tr> {value} </tr>'


def td(value):
    return f'<td>{value}</td>'


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
# Generate Comparison
# -----------------------------------------------------------------------------

def generate_comparison(root, comparison_spec):

    html_models = list()

    for i, model_spec in enumerate(comparison_spec):

        model_name = model_spec['model']
        src_latex = model_spec['src_latex']
        src_images_root = model_spec['src_images_root']
        dec_latex = model_spec['dec_latex']
        dec_images_root = model_spec['dec_images_root']

        print('-'*20, i, model_name)

        src_images_files = natural_sort_filenames(src_images_root, extension='.png')
        dec_images_files = natural_sort_filenames(dec_images_root, extension='.png')

        html_comparisons = list()

        for i, (src_file, dec_file) in enumerate(zip(src_images_files, dec_images_files)):

            src_file = os.path.join(model_name, f'manual_eqn_images/{src_file}')
            dec_file = os.path.join(model_name, f'decoded_images/{dec_file}')

            print(i)
            print(src_file)
            print(dec_file)

            html_comp = html_eqn_comparison(i, html_image(src_file, src_file), html_image(dec_file, dec_file))
            html_comparisons.append(html_comp)

        html_models.append(html_model(model_name, '\n'.join(html_comparisons)))

    html_string = html_outer('\n'.join(html_models))

    comparison_html_file = os.path.join(root, 'comparison.html')
    with open(comparison_html_file, 'w') as fout:
        fout.write(html_string)

    return comparison_html_file


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    generate_comparison(MODEL_ROOT, COMPARISON_SPEC)

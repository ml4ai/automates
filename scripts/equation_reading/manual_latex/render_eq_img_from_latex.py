# Script to read equation latex from source file (one eqn per line)
# and render each equation as a png

import os
import subprocess
# import pdf2image
# import sys

EQN_SOURCE_ROOT = '/Users/claytonm/Google Drive/ASKE-AutoMATES/Data/Mini-SPAM/eqns/SPAM/PET'

PETPT_ROOT = os.path.join(EQN_SOURCE_ROOT, 'PETPT')


def standalone_eq_template(eqn):
    template = '\\documentclass{standalone}\n' \
               '\\usepackage{amsmath}\n' \
               '\\usepackage{amssymb}\n' \
               '\\begin{document}\n' \
               f'$\\displaystyle {{{{ {eqn} }}}} $\n' \
               '\\end{document}'
    return template


def render_eqn_latex():
    pass


def process_latex_source(latex_src, image_dst_root, dpi=50, verbose=False, test_p=True):

    cwd = os.getcwd()
    if verbose:
        print(f'Initial CWD: {cwd}')
    os.chdir(os.path.join(image_dst_root, 'manual_latex'))
    if verbose:
        print(f'Changed to {os.getcwd()}')

    with open(latex_src, 'r') as fin:
        for i, line in enumerate(fin.readlines()):
            eqn_latex = line.strip('\n')
            latex_output = standalone_eq_template(eqn_latex)
            if verbose:
                print('-'*20, i)
                # print(i, eqn_latex)
                # print(i, latex_output)

            eqn_latex_file = f'{i}.tex'

            if verbose:
                print(f'writing {eqn_latex_file}')
            if not test_p:
                with open(eqn_latex_file, 'w') as fout:
                    fout.write(latex_output)

            command_args = ['pdflatex', f'{i}.tex']

            if verbose:
                print(f'suprocess.run({command_args})')
            if not test_p:
                subprocess.run(command_args)
                if verbose:
                    print('    after subprocess.run')

            # cleanup
            os.remove(f'{i}.aux')
            os.remove(f'{i}.log')

            eqn_pdf_file = f'{i}.pdf'
            eqn_png_file = f'../{i}.png'

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

            '''
            print(f'waiting for {eqn_pdf_file}', end='')
            while not os.path.exists(eqn_pdf_file):
                print('.', end='')
            print('!')
            '''

            '''
            if verbose:
                print(f'pdf2image.convert_from_path(\'{eqn_pdf_file}\', fmt=\'png\', dpi={dpi}), output_file=\'{eqn_png_file}\'')
            if not test_p:
                images = pdf2image.convert_from_path(eqn_pdf_file, fmt='png', dpi={dpi},
                                                     output_file=eqn_png_file)
                print(images)
                print(type(images))

            sys.exit()
            '''

    if verbose:
        print(f'Current CWD: {os.getcwd()}')
    os.chdir(cwd)
    if verbose:
        print(f'Returning CWD, now: {os.getcwd()}')


if __name__ == '__main__':
    PETPT_LATEX_SOURCE = os.path.join(PETPT_ROOT, 'PETPT_equations.txt')
    process_latex_source(PETPT_LATEX_SOURCE, PETPT_ROOT, 50, True, False)

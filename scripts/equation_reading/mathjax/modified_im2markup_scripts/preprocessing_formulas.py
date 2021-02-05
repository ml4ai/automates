#!/usr/bin/env python
# tokenize latex formulas
import sys, os, argparse, logging, subprocess, shutil

root = '/projects/temporary/automates/er/gaurav'

def is_ascii(str):
    try:
        str.decode('ascii')
        return True
    except UnicodeError:
        return False

def process_args(args):
    parser = argparse.ArgumentParser(description='Preprocess (tokenize or normalize) latex formulas')

    parser.add_argument('--mode', dest='mode',
                        choices=['tokenize', 'normalize'], required=True,
                        help=('Tokenize (split to tokens seperated by space) or normalize (further translate to an equivalent standard form).'
                        ))
    parser.add_argument('--input-file', dest='input_file',
                        type=str, required=True,
                        help=('Input file containing latex formulas. One formula per line.'
                        ))
    parser.add_argument('--output-file', dest='output_file',
                        type=str, required=True,
                        help=('Output file.'
                        ))
    parser.add_argument('--num-threads', dest='num_threads',
                        type=int, default=4,
                        help=('Number of threads, default=4.'
                        ))
    parser.add_argument('--log-path', dest="log_path",
                        type=str, default='log.txt',
                        help=('Log file path, default=log.txt'
                        ))
    parameters = parser.parse_args(args)
    return parameters

def main(args):

    global root

    parameters = process_args(args)
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
        filemode='w',
        filename=os.path.jon(root, f'{str(parameters.year)}/im2markup_Logs/{parameters.directories[0]}_{parameters.directories[-1]}_cropped_images.log'))
    logger = logging.getLogger()

    for DIR in parameters.directories:
        input_dir = os.path.join(root, f'{str(parameters.year)}/{DIR}/SLE/single_line_equations')

        # output directories
        output_dir = os.path.join(root, f'{str(parameters.year)}/{DIR}/im2markup/tokenized_formulas')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for folder in os.listdir(im2markup_dir):
            folder_path = os.path.join(input_dir, folder)
            for tyf in os.listdir(folder_path):
                tyf_path = os.path.join(folder-path, tyf)
                # output folder
                output_folder = os.path.join(output_dir, folder)
                output_tyf = os.path.join(output_folder, tyf)
                for F in [output_folder, output_tyf]:
                    if not os.path.exists(F):
                        os.makedirs(F)

                filenames = glob.glob(os.path.join(tyf-path, '*'+'.txt'))
                temp = [(filename, os.path.join(output_tyf, filename)) for filename in filenames]

        with Pool(multiprocessing.cpu_count()-10) as pool:
            results = pool.map(main_parallel, temp)

def main_parallel(l):
    input_file, output_file = l

    assert os.path.exists(input_file), input_file
    cmd = "perl -pe 's|hskip(.*?)(cm\\|in\\|pt\\|mm\\|em)|hspace{\\1\\2}|g' %s > %s"%(input_file, output_file)
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        logging.error('FAILED: %s'%cmd)

    temp_file = output_file + '.tmp'
    with open(temp_file, 'w') as fout:
        with open(output_file) as fin:
            for line in fin:
                fout.write(line.replace('\r', ' ').strip() + '\n')  # delete \r

    cmd = "cat %s | node scripts/preprocessing/preprocess_latex.js %s > %s "%(temp_file, parameters.mode, output_file)
    ret = subprocess.call(cmd, shell=True)
    os.remove(temp_file)
    if ret != 0:
        logging.error('FAILED: %s'%cmd)
    temp_file = output_file + '.tmp'
    shutil.move(output_file, temp_file)
    with open(temp_file) as fin:
        with open(output_file, 'w') as fout:
            for line in fin:
                tokens = line.strip().split()
                tokens_out = []
                for token in tokens:
                    if is_ascii(token):
                        tokens_out.append(token)
                fout.write(' '.join(tokens_out)+'\n')
    os.remove(temp_file)

if __name__ == '__main__':
    main(sys.argv[1:])
    logging.info('Jobs finished')

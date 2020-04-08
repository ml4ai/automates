import argparse
import os
import shutil
import zipfile


# -----------------------------------------------------------------------------
# utilities
# -----------------------------------------------------------------------------


def json_p(fname):
    if fname.lower().endswith('.json'):
        return True


def findfiles(path, test_fn):
    res = list()
    for root, dirs, fnames in os.walk(path):
        for fname in fnames:
            if test_fn(fname):
                res.append(os.path.join(root, fname))
    return res


def copy_to_tmp(paths, dst, verbose, test):
    if os.path.exists(dst):
        raise IOError('dst directory already exists')
    else:
        try:
            os.makedirs(dst)
        except OSError:
            print(f'Creation of directory {dst} has failed')
        else:
            if verbose or test:
                print(f'Successfully created directory {dst}')
    if verbose and not test:
        print(f'Copying {len(paths)} files to {dst}')
    if test:
        print(f'TEST - would copy {len(paths)} files to {dst}')
    for path in paths:
        filename = os.path.split(path)[1]
        dstpath = os.path.join(dst, filename)
        if verbose and not test:
            print(f'copy from: {path}')
            print(f'copy to:   {dstpath}')
        if test:
            print(f'TEST copy from: {path}')
            print(f'TEST copy to:   {dstpath}')
        if not test:
            shutil.copyfile(path, dstpath)


def zipfiles(dst, paths):
    zipf = zipfile.ZipFile(dst, 'x', zipfile.ZIP_DEFLATED)
    for path in paths:
        print(f'>>> path: {path}')
        zipf.write(path)
    print('>>> closing...')
    zipf.close()


def zipdir(dst, verbose):
    if verbose:
        print(f'Zipping dir: {args.dst}')
    dst_zip_filename = f'{dst}.zip'
    zipf = zipfile.ZipFile(dst_zip_filename, 'x', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(dst):
        for file in files:
            src = os.path.join(root, file)
            reldst = os.path.relpath(src, os.path.join(dst, '..'))
            if verbose:
                print(f'zip src:    {src}')
                print(f'zip reldst: {reldst}')
            zipf.write(src, reldst)
    zipf.close()


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    usage = '\nHelper utility to gather any .json annotation file under\n' \
            '<root> directory, copy them to a temporary <dst> directory,\n' \
            'zip the <dst> directory as <dst>.zip, then delete the temporary\n' \
            '<dst> directory.\n\n' \
            'Use -t to run in TEST mode: searches for .json in <root> and\n' \
            'shows where files would be copied but without copying.\n\n' \
            'NOTE: if there are multiple instances of the same source .json\n' \
            'file, the most recent read while walking the <root> tree will\n' \
            'overwrite any others.'
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('root', help='Source root directory')
    parser.add_argument('dst', help='Destination root (will create)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Run in verbose mode')
    parser.add_argument('-t', '--test', action='store_true',
                        help='Run in test mode: only report .json files found')
    args = parser.parse_args()

    if args.verbose and args.test:
        print(f'Reading from root: {args.root}')
    paths = findfiles(args.root, json_p)
    if args.verbose and args.test:
        print('found:')
        print(paths)
    if paths:
        copy_to_tmp(paths, args.dst, args.verbose, args.test)
        if not args.test:
            zipdir(args.dst, args.verbose)
            shutil.rmtree(args.dst)
    else:
        if args.verbose:
            print('No files found to zip')
    print('DONE.')

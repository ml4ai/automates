import os
import pathlib
import subprocess
import argparse


def compile_source_in_dir(bin_root_dir='', dst_root_dir=None, execute_p=False):
    if execute_p:
        # create destination root directory if does not already exist
        pathlib.Path(dst_root_dir).mkdir(parents=True, exist_ok=True)

    errors = list()

    # iterate through the src_root_dir
    for subdir, dirs, files in os.walk(bin_root_dir):
        for file in files:
            src_filepath = subdir + os.sep + file
            output_filename = file + '__objdump'
            output_filepath = os.path.join(dst_root_dir, output_filename) + '.txt'
            command_list = ['objdump', '-d', src_filepath]  # , '>', output_filepath]
            if not execute_p:
                print(command_list)
            else:
                print(f'Executing {command_list}')
                result = subprocess.run(command_list, stdout=subprocess.PIPE)
                if result.returncode != 0:
                    errors.append(result)
                else:
                    with open(output_filepath, 'w') as dump_file:
                        dump_file.write(result.stdout.decode('utf-8'))
    return errors


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--execute',
                        help='execute script (as opposed to running in test mosde)',
                        action='store_true', default=False)
    parser.add_argument('-b', '--bin_root_dir',
                        help='specify the binary root directory',
                        type=str,
                        default='examples_bin')
    parser.add_argument('-d', '--dst_root_dir',
                        help='specify the destination root directory',
                        type=str,
                        default='examples_objdump')
    args = parser.parse_args()
    if args.execute:
        print(f'EXECUTE! {args.bin_root_dir} {args.dst_root_dir}')
    else:
        print(f'Running in TEST mode {args.bin_root_dir} {args.dst_root_dir}')

    errors = compile_source_in_dir(bin_root_dir=args.bin_root_dir,
                                   dst_root_dir=args.dst_root_dir,
                                   execute_p=args.execute)
    for e in errors:
        print(f'ERROR: {e}')


if __name__ == '__main__':
    main()

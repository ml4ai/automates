import os
import platform
import subprocess
import pathlib
import json


def compile_source_in_dir(src_root_dir='', dst_root_dir=None, ext='c', command=None, binary_postfix=None, test_p=True):
    if test_p:
        print('Running in TEST mode')

    errors = list()

    # create destination root directory if does not already exist
    pathlib.Path(dst_root_dir).mkdir(parents=True, exist_ok=True)

    # iterate through the src_root_dir
    for subdir, dirs, files in os.walk(src_root_dir):
        for file in files:
            src_filepath = subdir + os.sep + file
            if src_filepath.endswith(ext):
                output_filepath = src_filepath
                if dst_root_dir:
                    output_filepath = os.path.join(dst_root_dir, os.path.basename(src_filepath))
                output_filepath = os.path.splitext(output_filepath)[0]
                if binary_postfix is not None:
                    output_filepath += binary_postfix
                command_list = command + [src_filepath, '-o', output_filepath]
                if test_p:
                    print(command_list)
                else:
                    print(f'Executing {command_list}')
                    result = subprocess.run(command_list, stdout=subprocess.PIPE)
                    if result.returncode != 0:
                        errors.append(result)
    return errors


def config_requirement_message():
    print("To us this script you must first create a file 'config.json'")
    print("with the following contents -- replace <path_to_gcc> with the")
    print("appropriate absolute path within a string:")
    print("{")
    print("  \"gcc\": \"<path_to_gcc>\"")
    print("}")


def get_gcc_version(gcc_path):
    """
    Helper to extract the gcc version
    :param gcc_path: path to gcc
    :return: string representing gcc version
    """
    version_bytes = subprocess.check_output([gcc_path, '--version'])
    version_str = version_bytes.decode('utf-8')
    if 'clang' in version_str:
        clang_idx = version_str.find('clang')
        version_str = version_str[clang_idx:version_str.find(')', clang_idx)]
        print('CLANG:', version_str)
    else:
        version_str = 'gcc-' + version_str.split('\n')[0].split(' ')[2]
        print(f"GCC: {version_str}")
    return version_str


def main(src_root_dir='', dst_root_dir='', test_p=True):
    # verify config.json exists
    if not os.path.isfile('config.json'):
        config_requirement_message()
        return

    # get gcc_path
    gcc_path = ''
    with open('config.json', 'r') as json_file:
        data = json.load(json_file)
        if 'gcc' not in data:
            print("config.json must specify field 'gcc'")
            return
        gcc_path = data['gcc']
        print(f"using gcc: {gcc_path}")

    # get gcc version
    gcc_version = get_gcc_version(gcc_path)

    # get platform name
    pname = platform.platform()
    pname_base = pname.split('-')[0]
    dst_root_dir = os.path.join(dst_root_dir, pname_base)

    errors = compile_source_in_dir(src_root_dir=src_root_dir,
                                   dst_root_dir=dst_root_dir,
                                   ext='.c',
                                   command=[gcc_path, '-O0'],
                                   binary_postfix='_' + pname,
                                   test_p=test_p)
    for e in errors:
        print(f'ERROR: {e}')


if __name__ == '__main__':
    main(src_root_dir='examples_src', dst_root_dir='examples_dst', test_p=True)

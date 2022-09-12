import subprocess
import os
from pathlib import Path
import datetime
import shutil
from typing import List, Tuple
import argparse


# -----------------------------------------------------------------------------
# Script to automate using swagger-codegen to generate the Python data model
#   Three generation modes: CAST, GROMET, METADATA
# Requires that swagger-codegen is installed
#   On Mac with homebrew:  $ brew install swagger-codegen
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

# Current highest versions
CAST_VERSION = "1.2.1"
GROMET_VERSION = "0.1.4"

RELATIVE_AUTOMATES_ROOT = '../../'

URL_BASE_MODEL = "https://raw.githubusercontent.com/ml4ai/automates-v2/master/docs/source/"
URL_BASE_CAST_MODEL = f"{URL_BASE_MODEL}cast_v"
URL_BASE_GROMET_MODEL = f"{URL_BASE_MODEL}gromet_FN_v"
URL_BASE_METADATA_MODEL = f"{URL_BASE_MODEL}gromet_metadata_v"
SWAGGER_COMMAND = ["swagger-codegen", "generate", "-l", "python", "-o", "./client", "-i"]

GENERATED_MODEL_ROOT = "client/swagger_client/models"
GENERATED_MODEL_IMPORT_PATH = "swagger_client.models"

MODEL_ROOT_CAST = "automates/program_analysis/CAST2GrFN/model/cast"
IMPORT_PATH_CAST = "automates.program_analysis.CAST2GrFN.model.cast"

MODEL_ROOT_GROMET = "automates/gromet/fn"
IMPORT_PATH_GROMET = "automates.gromet.fn"

MODEL_ROOT_METADATA = "automates/gromet/metadata"
IMPORT_PATH_METADATA = "automates.gromet.metadata"


# -----------------------------------------------------------------------------
# Implementation
# -----------------------------------------------------------------------------

def get_timestamp() -> str:
    return '{:%Y_%m_%d_%H_%M_%S_%f}'.format(datetime.datetime.now())


def get_url(url_base: str, version: str) -> str:
    return f"{url_base}{version}.yaml"


def move_existing_model_dir(model_root: str, model_type: str, copy_readme: bool, verbose=True):
    if verbose:
        print(f"(1) mv existing {model_type} model")
    if os.path.exists(model_root):
        if os.path.isdir(model_root):
            datestr = '{:%Y_%m_%d}'.format(datetime.datetime.now())
            renamed_old_dir = model_root + f'_orig_{datestr}'
            if verbose:
                print("    Moving")
                print(f"      {model_root} to")
                print(f"      {renamed_old_dir}")
            shutil.move(model_root, renamed_old_dir)

            if verbose:
                print(f"    Creating new: {model_root}")
            if os.path.exists(model_root):
                raise Exception(f"create_new_target_model_dir(): model_root already exists!: {model_root}")

            Path(model_root).mkdir(parents=True, exist_ok=False)

            if copy_readme:
                readme_path_src = os.path.join(renamed_old_dir, 'README.md')
                if verbose:
                    print(f"    Copying README.md from {readme_path_src}")
                if not os.path.exists(readme_path_src):
                    raise Exception(f"move_existing_model_dir(): README.md not found here: {readme_path_src}")
                else:
                    shutil.copyfile(readme_path_src, os.path.join(model_root, "README.md"))

            if verbose:
                print("    DONE.")
        else:
            print(f"NOTE: The following path exists but is not a dir: {model_root}")
    else:
        print(f"NOTE: CAST model does not already exist at: {model_root}")


def call_swagger_command(model_url: str, verbose: bool = True):
    path = 'client'  # assumed relative path to swagger-generated model root
    if verbose:
        print("(2) call_swagger_command()")

    if os.path.exists(path):
        raise Exception(f"call_swagger_command(): Path already exists!: {path}")

    command = SWAGGER_COMMAND + [model_url]
    if verbose:
        print(f'  command: "{command}"')
    ret = subprocess.run(command)
    if verbose:
        print(f'    call_swagger_command() return code: {ret.returncode}')
    if ret.returncode != 0:
        raise Exception(f"call_swagger_commend(): return code {ret.returncode} != 0")
    else:
        print("    DONE.")


def collect_filepaths(root: str, ext: str = '.py',
                      ignore: List[str] = None,
                      verbose=True) -> List[str]:
    """
    Collect all filepaths in `root` directory with extension `ext`
    but not matching a name in `ignore`.
    :param root: root directory within which to collect files
    :param ext: file extension; if match, collect the filepath
    :param ignore: list of filenames to ignore even if they have ext
    :param verbose:
    :return:
    """
    if ignore is None:
        ignore = list()
    if verbose:
        print("(3) collect_filepaths_with_extension()")
        print(f"    root: {root}")
        print(f"    ext: {ext}")
        print(f"    ignore: {ignore}")
    collected_files = list()
    for root, dirs, files in os.walk(root):
        for file in files:
            if file in ignore:
                if verbose:
                    print(f"    IGNORING: {file}")
            else:
                if file.endswith(ext):
                    collected_files.append(file)
                else:
                    if verbose:
                        print(f"    SKIPPING: {file}")
    if verbose:
        print("    DONE.")
    return collected_files


def read_lines_from_file(filepath: str) -> List[str]:
    with open(filepath, 'r') as fin:
        lines = list(fin.readlines())
    return lines


def replace_lines(lines: List[str], old: str, new: str) -> Tuple[List[str], List[int]]:
    new_lines = list()
    line_nums = list()
    for line_num, line in enumerate(lines):
        if old in line:
            line_nums.append(line_num)
        new_lines.append(line.strip('\n').replace(old, new))
    return new_lines, line_nums


def write_lines_to_file(dst_filepath: str, lines: List[str]):
    with open(dst_filepath, 'w') as fout:
        for line in lines:
            fout.write(f'{line}\n')


def comment_metadata(lines: List[str], verbose: str = True):
    new_lines = list()
    comment_line_nums = list()
    for i, line in enumerate(lines):
        if 'import Metadata' in line:
            line = '# ' + line
            comment_line_nums.append(i)
        new_lines.append(line)
    if verbose:
        print(f"    Commented metadata, lines: {comment_line_nums}")
    return new_lines


def copy_and_replace_import_paths(src_files: List[str], src_root: str, dst_root: str,
                                  import_path: str, model_type: str,
                                  verbose: bool = True):
    if verbose:
        print("(4) copy_and_replace_import_paths()")
    for filename in src_files:
        src_filepath = os.path.join(src_root, filename)
        dst_filepath = os.path.join(dst_root, filename)
        if verbose:
            print(f"        reading lines from {src_filepath}")
        lines = read_lines_from_file(src_filepath)
        lines, line_nums = replace_lines(lines, GENERATED_MODEL_IMPORT_PATH, import_path)
        if verbose and line_nums:
            print(f'          replaced {dst_filepath}: {line_nums}')
        if model_type == 'GROMET' and filename == '__init__.py':
            lines = comment_metadata(lines)
        write_lines_to_file(dst_filepath, lines)
    if verbose:
        print("    DONE.")


def delete_generated_client_dir(verbose: bool = True):
    if verbose:
        print("(5) delete_generated_client_dir")
    shutil.rmtree('client')
    if verbose:
        print("    DONE.")


def process(model_type: str, model_version: str, verbose: bool = True):

    if model_type == 'CAST':
        model_root = os.path.join(RELATIVE_AUTOMATES_ROOT, MODEL_ROOT_CAST)
        model_url = get_url(URL_BASE_CAST_MODEL, model_version)
        copy_readme = False
        import_path = IMPORT_PATH_CAST
        ignore = list()
    elif model_type == 'GROMET':
        model_root = os.path.join(RELATIVE_AUTOMATES_ROOT, MODEL_ROOT_GROMET)
        model_url = get_url(URL_BASE_GROMET_MODEL, model_version)
        copy_readme = True
        import_path = IMPORT_PATH_GROMET
        ignore = ['metadata.py']
    elif model_type == 'METADATA':
        model_root = os.path.join(RELATIVE_AUTOMATES_ROOT, MODEL_ROOT_METADATA)
        model_url = get_url(URL_BASE_METADATA_MODEL, model_version)
        copy_readme = True
        import_path = IMPORT_PATH_METADATA
        ignore = list()
    else:
        raise Exception(f"process(): Unknown model_type: {model_type}")

    if verbose:
        print(f"\n========== Process {model_type} version {model_version} ==========")

    move_existing_model_dir(model_root, model_type=model_type, copy_readme=copy_readme, verbose=verbose)

    call_swagger_command(model_url, verbose=verbose)

    src_files = collect_filepaths(GENERATED_MODEL_ROOT, ignore=ignore, verbose=verbose)

    copy_and_replace_import_paths(src_files,
                                  src_root=GENERATED_MODEL_ROOT,
                                  dst_root=model_root,
                                  import_path=import_path,
                                  model_type=model_type,
                                  verbose=verbose)

    delete_generated_client_dir(verbose=verbose)


# -----------------------------------------------------------------------------
# SCRIPT
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Use swagger-codegen to generate '
                                                 'CAST, GROMET and/or METADATA data model')
    # parser.add_argument()
    process('CAST', CAST_VERSION)
    process('GROMET', GROMET_VERSION)
    process('METADATA', GROMET_VERSION)


if __name__ == "__main__":
    main()

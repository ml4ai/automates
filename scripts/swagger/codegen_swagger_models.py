import subprocess
import os
import datetime

# Script to automate using swagger-codegen to generate the CAST Python data model
# Requires that swagger-codegen is installed
#   On Mac with homebrew:  $ brew install swagger-codegen

RELATIVE_AUTOMATES_ROOT = '../../'

CAST_VERSION = "1.2.1"
URL_BASE_MODEL = "https://raw.githubusercontent.com/ml4ai/automates-v2/master/docs/source/"
URL_BASE_CAST_MODEL = f"{URL_BASE_MODEL}cast_v"
URL_BASE_GROMET_MODEL = f"{URL_BASE_MODEL}gromet_FN_v"
URL_BASE_METADATA_MODEL = f"{URL_BASE_MODEL}gromet_metadata_v"
SWAGGER_COMMAND = ["swagger-codegen", "generate", "-l", "python", "-o", "./client", "-i"]

GENERATED_MODEL_ROOT = "client/swagger_client/models"
GENERATED_MODEL_IMPORT_PATH = "swagger_client.models"

MODEL_ROOT_CAST = "automates/program_analysis/CAST2GrFN/model/cast"
IMPORT_PATH_CAST = "automates.program_analysis.CAST2GrFN.model.cast"

MODEL_ROOT_GROMET = "automates/model_assembly/gromet/model"
IMPORT_PATH_GROMET = "automates.model_assembly.gromet.model"

MODEL_ROOT_METADATA = "automates/model_assembly/gromet/metadata"
IMPORT_PATH_METADATA = "automates.model_assembly.gromet.metadata"


def get_timestamp():
    return '{:%Y_%m_%d_%H_%M_%S_%f}'.format(datetime.datetime.now())


def get_cast_url(version: str) -> str:
    return f"{URL_BASE_CAST_MODEL}{version}.yaml"


def call_swagger_command(url):
    command = SWAGGER_COMMAND + [url]
    print(command)
    ret = subprocess.run(command)
    print(ret.returncode)
    print(ret)


def replace_lines_in_file(filepath, old, new):
    lines = list()
    with open(filepath, 'r') as fin:
        for line in fin.readlines():
            lines.append(line.strip('\n').replace(old, new))
    return lines


def replace_import_paths(import_path):
    init_filepath = os.path.join(GENERATED_MODEL_ROOT, '__init__.py')
    lines = replace_lines_in_file(init_filepath, GENERATED_MODEL_IMPORT_PATH, import_path)
    for line in lines:
        print(f'>>{line}<<')
    return lines


def write_lines_to_file(dst_filepath, lines):
    with open(dst_filepath, 'w') as fout:
        for line in lines:
            fout.write(f'{line}\n')


def collect_files_with_extension(root: str, ext: str = '.py'):
    collected_files = list()

    print(os.getcwd())
    print(root)
    print(os.listdir('../..'))

    for root, dirs, files in os.walk(root):
        for file in files:
            if file.endswith(ext):
                collected_files.append(os.path.join(root, file))
    return collected_files


# -----------------------------------------------------------------------------
# CAST
# -----------------------------------------------------------------------------

def process_cast():
    cast_root = os.path.join(RELATIVE_AUTOMATES_ROOT, MODEL_ROOT_CAST)
    cast_files = collect_files_with_extension(cast_root)
    for f in cast_files:
        print(f)
    # replace_import_paths(cast_root)


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    process_cast()
    # print(call_swagger_command(get_cast_url(CAST_VERSION)))

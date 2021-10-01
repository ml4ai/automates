import os
import json
import csv
import random
import shutil

from enum import Enum, auto
from posix import O_APPEND

from automates.program_analysis.GCC2GrFN.gcc_plugin_driver import run_gcc_plugin
from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast import GCC2CAST

GCC_PLUGIN_IMAGE_DIR = "automates/program_analysis/gcc_plugin/plugin/"


class ValidationResult(Enum):
    SUCCESS = auto()
    GCC_COMPILATION_ERROR = auto()
    GCC_AST_PARSE_ERROR = auto()
    GCC_AST_TO_CAST_ERROR = auto()
    CAST_TO_GRFN_ERROR = auto()
    GRFN_EXECUTION_ERROR = auto()


def mkdir_p(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def report_error(error_type, msg):
    if error_type == "GCC":
        return f"{error_type}: {msg}"
    elif error_type == "CAST":
        return f"{error_type}: {msg}"
    elif error_type == "GrFN":
        return f"{error_type}: {msg}"


def test_execution(grfn):

    grfn_inputs = grfn.inputs
    inputs = dict()
    for i in grfn_inputs:
        inputs[str(i.identifier)] = random.randint(0, 100)
    grfn(inputs)


def validate_example(example_name, example_files, path):
    example_c_files = [f"{path}/{f}" for f in example_files if f.endswith(".c")]
    try:
        gcc_ast_files = run_gcc_plugin(
            "c", example_c_files, GCC_PLUGIN_IMAGE_DIR, compile_binary=True
        )
    except Exception as e:
        # TODO actually catch exception
        return (
            example_name,
            ValidationResult.GCC_COMPILATION_ERROR,
            str(e),
        )

    # Move gcc AST files and binary if compilation works
    new_gcc_ast_file_paths = list()
    for gcc_ast_file in gcc_ast_files:
        new_path = f"{path}/{gcc_ast_file}"
        shutil.move(gcc_ast_file, new_path)
    new_gcc_ast_file_paths.append(new_path)
    shutil.move("./a.out", f"{path}/{example_name}")

    try:
        gcc_asts = [json.load(open(a)) for a in new_gcc_ast_file_paths]
    except Exception as e:
        # TODO specify exception
        return (
            example_name,
            ValidationResult.GCC_AST_PARSE_ERROR,
            str(e),
        )

    try:
        cast = GCC2CAST(gcc_asts).to_cast()
    except Exception as e:
        # TODO specify exception
        return (
            example_name,
            ValidationResult.GCC_AST_TO_CAST_ERROR,
            str(e),
        )

    json.dump(cast.to_json_object(), open(f"{path}/{example_name}--CAST.json", "w"))

    try:
        grfn = cast.to_GrFN()
    except Exception as e:
        # TODO specify exception
        return (
            example_name,
            ValidationResult.CAST_TO_GRFN_ERROR,
            str(e),
        )

    grfn.to_json_file(f"{path}/{example_name}--GrFN.json")

    try:
        test_execution(grfn)
    except Exception as e:
        # TODO specify exception
        return (example_name, ValidationResult.GRFN_EXECUTION_ERROR, str(e))

    return (example_name, ValidationResult.SUCCESS, "")


def open_results_csv_writer(result_location):
    validate_csv_file_name = f"./{result_location}/validate-results.csv"
    try:
        validate_csv_file = open(validate_csv_file_name, "w")
    except:
        print(
            f'Error: Unable to access results location "{result_location}", stopping '
        )
        return None

    validate_csv_file_writer = csv.writer(
        validate_csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    validate_csv_file_writer.writerow(
        ["Example Name", "Example Status", "Extra Information"]
    )

    return validate_csv_file_writer


def write_results_to_csv(validate_results, validate_csv_file_writer):
    for (result, reason, verbose) in validate_results:
        validate_csv_file_writer.writerow([result, reason.name, verbose])


def validate_many_single_directory(directory, result_location):
    validate_results = list()
    validate_csv_file_writer = open_results_csv_writer(result_location)
    if validate_csv_file_writer == None:
        return

    mkdir_p(f"{result_location}/results/")

    example_files = os.listdir(directory)
    for example in example_files:
        if example.endswith(".c"):
            example_name = "".join(example.rsplit(".", 1)[:-1])
            dir_name = f"{result_location}/results/{example_name}"

            mkdir_p(dir_name)
            shutil.copy2(f"{directory}/{example}", f"{dir_name}")

            validate_results.append(validate_example(example_name, [example], dir_name))

    write_results_to_csv(validate_results, validate_csv_file_writer)


def validate_example_per_directory(root_directory, result_location):
    validate_results = list()
    validate_csv_file_writer = open_results_csv_writer(result_location)
    if validate_csv_file_writer == None:
        return

    directories = os.listdir(root_directory)
    for example_directory_name in directories:
        example_directory_full_path = f"{root_directory}/{example_directory_name}"
        example_files = os.listdir(example_directory_full_path)
        validate_results.append(
            validate_example(
                example_directory_name, example_files, example_directory_full_path
            )
        )

    successful = [
        result for result in validate_results if result[0] == ValidationResult.SUCCESS
    ]
    print(f"Successful examples: {len(successful)}")

    write_results_to_csv(validate_results, validate_csv_file_writer)

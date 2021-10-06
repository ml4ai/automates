import os
import sys
import json
import csv
import random
import shutil
import math
import multiprocessing

from enum import Enum, auto
from posix import O_APPEND

from automates.program_analysis.GCC2GrFN.gcc_plugin_driver import run_gcc_plugin
from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast import GCC2CAST

GCC_PLUGIN_IMAGE_DIR = "automates/program_analysis/gcc_plugin/plugin/"

# TODO why does the gcc_ast.jsons still exist in root?
# TODO capture better messages when gcc compilation fails
# TODO improve how we attempt to compile?


def progress(count, total, status=""):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + "-" * (bar_len - filled_len)

    sys.stdout.write("[%s] %s%s ...%s\r" % (bar, percents, "%", status))
    sys.stdout.flush()


class ValidationException(Exception):
    pass


class ValidationResult(Enum):
    SUCCESS = auto()
    GCC_COMPILATION_ERROR = auto()
    GCC_AST_PARSE_ERROR = auto()
    GCC_AST_TO_CAST_ERROR = auto()
    CAST_TO_GRFN_ERROR = auto()
    GRFN_EXECUTION_ERROR = auto()


def mkdir_p(dir):
    if not os.path.exists(dir):
        os.makedirs(dir, exist_ok=True)


def select_manual_samples(successful, dir):

    num_success = len(successful)
    manual_samples_indices = random.sample(
        range(num_success), math.ceil(num_success / 100)
    )
    manual_samples_file = open(f"{dir}/manualSamples.json", "w")
    json.dump(
        {"samplesToManuallyVerify": [successful[i][0] for i in manual_samples_indices]},
        manual_samples_file,
    )
    manual_samples_file.close()


def test_execution(grfn):

    grfn_inputs = grfn.inputs
    inputs = dict()
    for i in grfn_inputs:
        inputs[str(i.identifier)] = random.randint(0, 100)

    p = multiprocessing.Process(target=lambda: grfn(inputs))
    p.start()
    p.join(10)
    if p.is_alive():
        raise ValidationException("GrFN execution exceeded allowed time.")


def validate_example(example_name, example_files, path):
    example_c_files = [f"{path}/{f}" for f in example_files if f.endswith(".c")]
    try:
        gcc_ast_files = run_gcc_plugin(
            "c", example_c_files, GCC_PLUGIN_IMAGE_DIR, compile_binary=True
        )
    except Exception as e:
        # Remove generated AST in failed compilation cases
        for name in example_c_files:
            gcc_ast_file = f"{''.join(name.rsplit('.', 1)[:-1])}_gcc_ast.json"
            if os.path.exists(gcc_ast_file):
                os.remove(gcc_ast_file)

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
        gcc_ast_files = [open(a) for a in new_gcc_ast_file_paths]
        gcc_asts = [json.load(f) for f in gcc_ast_files]
        [f.close() for f in gcc_ast_files]
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

    cast_file = open(f"{path}/{example_name}--CAST.json", "w")
    json.dump(cast.to_json_object(), cast_file)
    cast_file.close()

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
    mkdir_p(f"{result_location}/results/")

    validate_results = list()
    validate_csv_file_writer = open_results_csv_writer(result_location)
    if validate_csv_file_writer == None:
        return

    example_files = os.listdir(directory)
    total_count = len(example_files)
    i = 0
    for example in example_files:
        progress(i, total_count, status="Processing examples files...")
        i += 1

        if example.endswith(".c"):
            example_name = "".join(example.rsplit(".", 1)[:-1])
            dir_name = f"{result_location}/results/{example_name}"

            mkdir_p(dir_name)
            shutil.copy2(f"{directory}/{example}", f"{dir_name}")

            validate_results.append(validate_example(example_name, [example], dir_name))

    write_results_to_csv(validate_results, validate_csv_file_writer)
    select_manual_samples(validate_results, result_location)


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
    select_manual_samples(successful, result_location)

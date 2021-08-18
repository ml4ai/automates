from gromet_extract_variables import collect_variables

import argparse
import json
import copy


def generate_gromet_with_var_objects(gromet_dict):
    new_gromet_dict = copy.deepcopy(gromet_dict)
    variables_extracted = collect_variables(gromet_dict)
    new_gromet_dict["variables"] = variables_extracted
    return new_gromet_dict


def run(args):
    gromet_file = args.gromet_file

    gromet = None
    with open(gromet_file) as f:
        gromet_dict = json.load(f)

    updated_gromet_dict = generate_gromet_with_var_objects(gromet_dict)

    gromet_file_prefix = gromet_file.split(".json")[0]
    with open(f"{gromet_file_prefix}-with-vars--GroMEt.json", "w") as f:
        json.dump(updated_gromet_dict, f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gromet_file", help="GroMEt file to parse variables from.")
    run(parser.parse_args())


if __name__ == "__main__":
    main()

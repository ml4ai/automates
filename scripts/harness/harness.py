import argparse

from validate import validate_many_single_directory, validate_example_per_directory
from generate import move_sample_data


def main(args):
    mode = args.mode
    if mode == "validate":
        if args.example_directory == None or args.results_directory == None:
            print("Error: results_directory and example_directory are required.")
            return
        validate_many_single_directory(args.example_directory, args.results_directory)
        # validate_example_per_directory(args.example_directory, args.results_directory)
    elif mode == "generate":
        if args.sample_directory == None or args.results_directory == None:
            print("Error: sample_directory and results_directory are required.")
            return
        move_sample_data(args.sample_directory, args.results_directory)
    else:
        print(f"Error: Unknown mode {mode}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode", help="Mode of execution, either 'validate' or 'generate'."
    )
    parser.add_argument(
        "--example_directory",
        help="The directory contiaining folders with c files to generate data from.",
    )
    parser.add_argument(
        "--results_directory",
        help="The directory where generated results should be stored.",
    )
    parser.add_argument(
        "--sample_directory",
        help="The directory where the interemediate results should are stored.",
    )
    main(parser.parse_args())

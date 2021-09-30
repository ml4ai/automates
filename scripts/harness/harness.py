import argparse

from validate import validate_many_single_directory, validate_example_per_directory


def main(args):
    validate_many_single_directory(args.example_directory, args.results_directory)
    # validate_example_per_directory(args.example_directory, args.results_directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--example_directory",
        help="The directory contiaining folders with c files to generate data from.",
        required=True,
    )
    parser.add_argument(
        "--results_directory",
        help="The directory where generated results should be stored.",
        required=True,
    )
    main(parser.parse_args())

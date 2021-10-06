# Data Harness

The data harness is used to validate and create data for the NMT using example sets of C code.

Link to architecture: https://docs.google.com/presentation/d/1i0tSmiFngvz14IkmPteVyK8wuWrXqVNzZDhYAqrS9Sc/edit#slide=id.geeec382814_0_0

# How to run

Lets consider an example where we have a folder called `add_examples` which is a flat directory containing .c files where each .c file is an independent code example. We can then try to validate and then generate the data as stated below. 

## Validation

To validate the data, we will run the script like so:

`python harness.py validate --example_directory=./add_examples/ --results_directory=./harness-example-validate-results/`

The first argument tells the script to run in validate mode. Then, the `--example_directory` option points to the directory containing the example .c files. Finally, the `--results_directory` points to where the results from validation should be stored.

After running, the results directory will have several files:
1. validate-results.csv: This is a csv file where each row represents an example input and if validation was successful or a reason for why it wasnt successful.
2. manualSamples.json: This is a list of sample names that were successfully validated. A random sampling of successful results is selected for manual validation. This list is that random sampling.
3. results: This is a directory containing subdirectories. Each subdirectory represents the results from a data sample we attempted to validate. It will have the code / gcc ast / binary / CAST / GrFN for the particular sample (or at least as much of it as it was able to generate).

## Generation

The generate portion of the script should be run after the manual samples were reviewed and shown to be correct. This script takes in the path to the results directory from the validation step. It will then move all of the successful examples to a specified location.

`python harness.py generate --sample_directory=./harness-example-validate-results/ --results_directory=./harness-example-generate-results/`

The first argument tells the script to run in generate mode. Then, the `--sample-directory` option points to the directory containing the results of the validation step. Finally, the `--results_directory` points to where the successful examples results should be moved to.

# Arguments

This script takes one positional argument which is either `validate` or `generate`. This dictates the mode the script runs in.

## Validate mode

Validate mode requires two arguments

 `--example_directory` option points to the directory containing the example .c files. This directory should be structured such that there are many .c files in it and each .c file is an independent example. An option to run with different directory structures is being worked on.
 `--results_directory` points to where the results from validation should be stored.

## Generate mode

Generate mode requires two arguments

 `--sample-directory` option points to the directory containing the results of the validation step. 
 `--results_directory` points to the directory where the successful examples results from validation should be moved to.
# Equation reading scripts

The scripts for processing equations are found here:
`https://github.com/ml4ai/automates/tree/master/src/equation_reading/equation_extraction`
There are LOTS of scripts, I have tried to organize them into folders by category.

### data_collection

Scripts for getting data out of arXiv.

- `expand_arxiv.py`: the script to run to recursively traverse and expand the download from arXiv
- `collect_data.py` : the code that operates over expanded arXiv files to generate the files that are consumed downstream.
     arguments:
        - **indir** - directory of a single paper
        - **outdir** - output directory (todo: for all? for paper?)
        - **logfile** - where to write log from the console commands (e.g., compiling the latex, etc.)
        - **template** - the latex template to render the extracted equation
        - **rescale-factor** - used to rescale pages to speedup template matching
        - **dump-pages** - whether or not you want to save a pdf of each page
        - **keep-intermediate-files**
        - **pdfdir** - if you have the directory with the already compiled pdfs from arxiv, speeds things up a lot
        - **num-paragraphs** - was used for the `pdfalign` work, size of window above and below the equation to save for context
- `latex.py`: contains the latex tokenizer, these methods are imported and used in `collect_data.py`
- `run_data_collection.sh`: the shell script used to actually do the data collection.  Makes use of "poor man's parallelization" (i.e., xargs), so you can specify the number of processes to give it.
    - note: this needs to be run _through docker_ to have access to all the latex stuff (with a command like`./docker.sh run_data_collection.sh <args>`), so all paths need to be relative to the docker container.

### postprocessing

Scripts which convert the output of data collection to a different format (e.g., opennmt)

- `convert_arxiv_output_to_opennmt.py`: Converts the output of `collect_data.py` above into the format needed to serve as opennmt input (i.e., to train the equation decoder model).  The code operates at the _month_ level.
- `run_conversion_to_opennmt.sh`: the shell script that calls `convert_arxiv_output_to_opennmt.py`, to make use of xargs parallelization.
- `opennmt_data_splits.sh`: not fully sure, but as I recall it takes the opennmt format and creates train/dev/test partitions
- `normalize_formulas.py`: this is run on the opennmt data to normalize the formulas (remove labels, adjust some formatting for consistency etc.).  Unfortunately, it relies on code in the im2markup repo (so you need to clone that repo) AND even worse, you need to make a small change to the code base for marking formulas that fail to compile.  These instructions are given [here](https://github.com/ml4ai/automates/wiki/README_equation_decoding).
- `augmentation_utils.py`: Contains utils used to do image augmentation (i.e., blur, downsample, skeletonize).  Used by `rerender_formulas.py`
- `rerender_formulas.py`: The actual code you run to make the augmented files.

### evaluation

Scripts for evaluating results.

- `process_results.py`: takes the output of the decoder and evaluates it against gold, using BLEU score.  Also produces a side-by-side rendering of the predicted equation next to the gold.
    Arguments:
     - **pred** - predictions file
     - **gold** gold sequences file
     - **outdir** - directory where to generate output files, the script produces a series of output files in a self-contained subdir.
     - **img-sample** - the number of images you want to (randomly) render for the side-by-side (in case you don't want to make all of them, as it's decently slow, especially if you're considering 10k images).
     - **seed** - Seed for the sampling above
     - **template** - the standalone latex equation template for rendering

### random

Scripts which are not ready for the graveyard, but also not likely to be a part of any regular workflows

### graveyard

scripts which are pretty much not used anymore


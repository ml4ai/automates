# Align Latex

## Conda
Use the conda environment from the pdfalign tool.

## Run
Data on the servers.  Most of it is in: `/data/nlp/corpora/latex_formulas`
The pdfalign annotations are in `annotations`
The bboxes are in `bounding_boxes`
NOTE: The latex source is located here: `amy:/data1/home/bsharp/annotation_src`
(It's big, so we haven't moved it yet, but the folder has `nlp` as the group)

Run:

    conda activate pdfalign
    cd automates/pdfalign/align_latex
    ./collect_latex.sh -a <annotations_dir> -b <bbox_dir> -l <latex_src_dir> -o <output_dir>

## TODO

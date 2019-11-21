#!/bin/bash

# read options
OPTIONS=$(getopt -o a:b:l:o:n: -l annotations:,bboxes:,latex:,output:,nproc: -- "$@")

# report errors
if [ $? != 0 ]; then
    echo "Terminating ..." >&2
    exit $?
fi

# set parsed options
eval set -- $OPTIONS

# default values
NPROC=1

# extract options and their arguments
while true; do
    case "$1" in
        -a|--annotations)
            ANNOTATIONS=${2%/}
            shift 2
            ;;
        -b|--bboxes)
            BBOXES=${2%/}
            shift 2
            ;;
        -l|--latex)
            LATEX=${2%/}
            shift 2
            ;;
        -o|--output)
            OUTPUT=${2%/}
            shift 2
            ;;
        -n|--nproc)
            NPROC=$2
            shift 2
            ;;
        --)
            break
            ;;
    esac
done

# fail if input dirs was not specified
if [ -z "$ANNOTATIONS" ]; then
    echo "Please specify the annotations directory with the --annotations argument." >&2
    echo "Terminating ..." >&2
    exit 1
fi
if [ -z "$BBOXES" ]; then
    echo "Please specify the bounding boxes directory with the --bboxes argument." >&2
    echo "Terminating ..." >&2
    exit 1
fi
if [ -z "$LATEX" ]; then
    echo "Please specify the latex directory with the --latex argument." >&2
    echo "Terminating ..." >&2
    exit 1
fi

echo "ANNOTATIONS: $ANNOTATIONS"
echo "BBOXES: $BBOXES"
echo "LATEX: $LATEX"
echo "OUTPUT: $OUTPUT"
echo "NPROC: $NPROC"
echo "-----"

collect_latex() {
    annotation=$1
    name=${annotation##*/}
    name=${name%.*}
    aabb=$2/$name/aabb.tsv
    latex=$3/$(echo $name | sed -E -e 's/([0-9]+\.[0-9]+).+/\1/')
    output=$4/$name
    results=$output/aligned.tsv
    echo "collecting $annotation ..."
    python align_eq_bb.py $latex $output $annotation $aabb
    python collect_results.py $output $results 
    find $output -mindepth 1 -type d -print0 | xargs -0 -I{} rm -rf {}
}

export -f collect_latex

# do the work
find $ANNOTATIONS -name '*.json' -print0 | xargs -0 -I{} -n 1 -P $NPROC bash -c 'collect_latex "$@"' _ {} $BBOXES $LATEX $OUTPUT

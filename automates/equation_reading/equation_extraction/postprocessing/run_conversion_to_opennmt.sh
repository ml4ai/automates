#!/bin/bash

# read options
OPTIONS=$(getopt -o i:o:l:n: -l indir:,outdir:,logdir:,nproc: -- "$@")

# report errors
if [ $? != 0 ]; then
    echo "Terminating ..." >&2
    exit $?
fi

# set parsed options
eval set -- $OPTIONS

# default values
ARGS=""
NPROC=1

# extract options and their arguments
while true; do
    case "$1" in
        -i|--indir)
            INDIR=$2
            shift 2
            ;;
        -o|--outdir)
            OUTDIR=$2
            shift 2
            ;;
        -l|--logdir)
            LOGDIR=$2
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

# fail if input dir was not specified
if [ -z "$INDIR" ]; then
    echo "Please specify the input directory with the --indir argument." >&2
    echo "Terminating ..." >&2
    exit 1
fi

echo "INDIR: $INDIR"
echo "NPROC: $NPROC"
echo "ARGS: $ARGS"

# read papers
find $INDIR -type d -regextype posix-awk -regex '.*/[0-9]{4}' -print0 | xargs -0 -I{} -n 1 -P $NPROC python -u /equation_extraction/convert_arxiv_output_to_opennmt.py {} $OUTDIR $LOGDIR

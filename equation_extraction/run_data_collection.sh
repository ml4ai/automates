#!/bin/bash

# read options
OPTIONS=$(getopt -o i:o:l:t:r:dkp:n:c: -l indir:,outdir:,logfile:,template:,rescale-factor:,dump-pages,keep-intermediate-files,pdfdir:,nproc:,num-paragraphs: -- "$@")

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
            ARGS="$ARGS --outdir=$2"
            shift 2
            ;;
        -l|--logfile)
            touch $2
            ARGS="$ARGS --logfile=$2"
            shift 2
            ;;
        -t|--template)
            ARGS="$ARGS --template=$2"
            shift 2
            ;;
        -r|--rescale-factor)
            ARGS="$ARGS --rescale-factor=$2"
            shift 2
            ;;
        -d|--dump-pages)
            ARGS="$ARGS --dump-pages"
            shift
            ;;
        -k|--keep-intermediate-files)
            ARGS="$ARGS --keep-intermediate-files"
            shift
            ;;
        -p|--pdfdir)
            ARGS="$ARGS --pdfdir=$2"
            shift 2
            ;;
        -n|--nproc)
            NPROC=$2
            shift 2
            ;;
        -c|--num-paragraphs)
            ARGS="$ARGS --num-paragraphs=$2"
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
find $INDIR -type d -regextype posix-awk -regex '.*/[0-9]{4}\.[0-9]{5}' -print0 | xargs -0 -I{} -n 1 -P $NPROC python -u /equation_extraction/collect_data.py {} $ARGS

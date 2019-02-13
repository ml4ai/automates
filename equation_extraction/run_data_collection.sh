#!/bin/bash

# read options
OPTIONS=$(getopt ... -- "$@")
eval set -- "$OPTIONS"

# extract options and their arguments
while true; do
    case "$1" in
        -i|--indir)
            ;;
        -o|--outdir)
            ;;
        -l|--logfile)
            ;;
        -t|--template)
            ;;
        -r|--rescale-factor)
            ;;
        -d|--dump-pages)
            ;;
        -k|--keep-intermediate-files)
            ;;
        -p|--pdfdir)
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "ERROR"
            exit 1
            ;;
    esac
done

INPUTDIR=$1
OUTPUTDIR=$2
#logfile
#template
# rescale-factor
# dump-pages
#keep-intermediate-files
# pdfdir
PDFDIR=$3
NPROCS=$3

# read papers
find $DATADIR -type d -regextype posix-awk -regex '.*/[0-9]{4}\.[0-9]{5}' -print0 | xargs -0 -I{} -n 1 -P $NPROCS python -u /equation_extraction/collect_data.py {}

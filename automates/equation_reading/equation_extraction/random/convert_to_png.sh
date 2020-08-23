#!/bin/bash
INDIR=$1
OUTDIR=$2
FILTER_FILE=$3
FORMULA_FILE=$4

mkdir -p $OUTDIR/png

CTR=0
for pdf in $INDIR/*.pdf; do
    name=$(basename $pdf .pdf)
    echo "$name.png $CTR" >> $FILTER_FILE
    echo "x x x" >> $FORMULA_FILE
    convert -density 200 -quality 100 -resize 50% $pdf $OUTDIR/png/$name.png
    CTR=$((CTR+1))
done

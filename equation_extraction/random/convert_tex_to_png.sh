#!/bin/bash
INDIR=$1
OUTDIR=$2
FILTER_FILE=$3
FORMULA_FILE=$4

mkdir -p $OUTDIR/png
mkdir -p $OUTDIR/pdf

CTR=0
for tex in $INDIR/*.tex; do
    latexmk -pdf -halt-on-error -outdir=$OUTDIR/pdf $tex
    latexmk -C -outdir=$OUTDIR/pdf
    name=$(basename $tex .tex)
    echo "$name.png $CTR" >> $FILTER_FILE
    echo "x x x" >> $FORMULA_FILE
    convert -background white -alpha remove -alpha off -density 200 -quality 100 $OUTDIR/pdf/$name.pdf $OUTDIR/png/$name.png
    CTR=$((CTR+1))
done

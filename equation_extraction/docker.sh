#!/bin/bash
IMAGE=clulab/equations
#DATADIR=/projects/automates # hard coded for venti
DATADIR=$PWD # hard coded for laptop
# DATADIR=/Users/bsharp/github/automates/equation_extraction
docker run --rm -i --user="$(id -u):$(id -g)" --net=none -v "$DATADIR":/data "$IMAGE" "$@"

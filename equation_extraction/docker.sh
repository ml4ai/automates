#!/bin/bash
DATA=$1
IMAGE=clulab/equations
docker run --rm -i --user="$(id -u):$(id -g)" --net=none -v "$DATA":/data "$IMAGE" "$@"

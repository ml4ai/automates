#!/bin/bash
IMAGE=maskrcnn-gpu
DATA=$PWD
docker run --runtime=nvidia --rm -i --user="$(id -u):$(id -g)" -v "$DATA":/data "$IMAGE" "$@"

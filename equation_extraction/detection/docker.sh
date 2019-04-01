#!/bin/bash
IMAGE=maskrcnn-cpu
DATA=$PWD
# docker run --rm -i --user="$(id -u):$(id -g)" --net=none -v "$DATA":/data "$IMAGE" "$@"
docker run -p 8888:8888 -v "$DATA":/data "$IMAGE" jupyter notebook --allow-root

# FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04
FROM tensorflow/tensorflow:1.6.0-devel-gpu-py3
# FROM ubuntu:16.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-utils git curl vim unzip openssh-client wget \
    build-essential cmake libopenblas-dev \
    python3.5 python3.5-dev python3-pip python3-tk \
    libjpeg-dev zlib1g-dev \
    libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libgtk2.0-dev \
    liblapacke-dev checkinstall

#
# Python 3.5
#
# For convenience, alias (but don't sym-link) python & pip to python3 & pip3 as recommended in:
# http://askubuntu.com/questions/351318/changing-symlink-python-to-python3-causes-problems
RUN pip3 install --no-cache-dir --upgrade setuptools && \
    echo "alias python='python3'" >> /root/.bash_aliases && \
    echo "alias pip='pip3'" >> /root/.bash_aliases

# Pillow and it's dependencies
RUN pip3 --no-cache-dir install Pillow

# Science libraries and other common packages
RUN pip3 --no-cache-dir install \
    numpy scipy sklearn scikit-image==0.14.2 pandas matplotlib Cython requests pandas imgaug

#
# Tensorflow 1.6.0 - GPU
#
# Install TensorFlow
# RUN pip3 --no-cache-dir install tensorflow-gpu==1.6.0
# RUN pip3 --no-cache-dir install tensorflow

# Expose port for TensorBoard
EXPOSE 6006

#
# OpenCV 3.4.1
#
RUN pip3 install opencv-python

#
# Keras 2.1.5
#
RUN pip3 install --no-cache-dir --upgrade h5py pydot_ng keras

#
# PyCocoTools
#
# Using a fork of the original that has a fix for Python 3.
# I submitted a PR to the original repo (https://github.com/cocodataset/cocoapi/pull/50)
# but it doesn't seem to be active anymore.
RUN pip3 install --no-cache-dir git+https://github.com/waleedka/coco.git#subdirectory=PythonAPI

WORKDIR "/data"

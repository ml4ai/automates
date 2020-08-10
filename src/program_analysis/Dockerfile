#FROM        ubuntu:20.04
FROM        688e6dc5af10
MAINTAINER  Paul D. Hein <pauldhein@email.arizona.edu>
CMD         bash

# ==============================================================================
# INSTALL SOFTWARE VIA THE UBUNTU PACKAGE MANAGER
# ==============================================================================
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get -y --no-install-recommends install git curl pkg-config
RUN apt-get -y --no-install-recommends install build-essential gcc g++ gfortran
RUN apt-get -y --no-install-recommends install python3 python3-dev python3-pip
RUN apt-get -y --no-install-recommends install r-base r-base-dev
RUN apt-get -y --no-install-recommends install make
RUN apt-get -y --no-install-recommends install g++-multilib
RUN apt-get -y --no-install-recommends install libgmp3-dev

RUN git config --global user.email "pauldhein@email.arizona.edu"
RUN git config --global user.name "Paul Hein"
# ==============================================================================

# ==============================================================================
# INSTALL PYTHON PACKAGES VIA PIP
# NOTE: Packages are installed in stages to avoid memory errors on DockerHub
# ==============================================================================
# Upgrading setuptools and installing wheel
RUN pip3 install --upgrade setuptools
RUN pip3 install wheel
RUN pip3 install tqdm==4.46.0 numpy==1.18.4

# ==============================================================================

# ==============================================================================
# COPY GCC PLUGIN INTO IMAGE AND COMPILE
# ==============================================================================
WORKDIR /gcc-plugin
COPY ./gcc-plugin/ast_plugin.cpp /gcc-plugin/
COPY ./gcc-plugin/gcc_ast_json_to_dot.py /gcc-plugin/
COPY ./gcc-plugin/Makefile /gcc-plugin/
RUN make
# ==============================================================================

# ==============================================================================
# SETUP THE AUTOMATES REPOSITORY AND ENVIRONMENT
# ==============================================================================
WORKDIR /
RUN git clone https://github.com/ml4ai/automates
ENV PYTHONPATH="/automates/src:$PYTHONPATH"
WORKDIR /automates/src/program_analysis
# ==============================================================================

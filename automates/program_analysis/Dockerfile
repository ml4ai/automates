FROM        ubuntu:20.04
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
# SETUP THE AUTOMATES REPOSITORY AND ENVIRONMENT
# ==============================================================================
WORKDIR /
RUN git clone https://github.com/ml4ai/automates
ENV PYTHONPATH="/automates/src:$PYTHONPATH"
WORKDIR /automates/src/program_analysis
# ==============================================================================

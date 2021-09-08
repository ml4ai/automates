FROM  ubuntu:20.04
CMD   bash

# ==============================================================================
# INSTALL SOFTWARE VIA THE UBUNTU PACKAGE MANAGER
# =============================================================================
ARG DEBIAN_FRONTEND=noninteractive
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN apt-get update && \
    apt-get -y --no-install-recommends install apt-utils
RUN apt-get update --fix-missing

# Use individual commands to prevent excess time usage when re-building
RUN apt-get -y --no-install-recommends install curl wget gnupg2 git 
RUN apt-get -y --no-install-recommends install openjdk-8-jdk antlr4 doxygen
RUN apt-get -y --no-install-recommends install gcc build-essential pkg-config
RUN apt-get -y --no-install-recommends install graphviz libgraphviz-dev
RUN apt-get -y --no-install-recommends install python3-dev python3-pip python3-venv

# Add dependencies needed to compile GCC for use in PA pipeline
RUN apt-get -y --no-install-recommends install make
RUN apt-get -y --no-install-recommends install g++-multilib
RUN apt-get -y --no-install-recommends install libgmp3-dev
RUN apt-get -y --no-install-recommends install libtool
RUN apt-get -y --no-install-recommends install binutils

RUN apt-get clean && rm -rf /var/lib/apt/lists/*
# =============================================================================

# =============================================================================
# RETRIEVE AND COMPILE GCC 10.0.1 FOR PA PIPELINE
# =============================================================================
WORKDIR /gcc_all
RUN curl -L https://ftpmirror.gnu.org/gcc/gcc-10.1.0/gcc-10.1.0.tar.xz -o gcc-10.1.0.tar.xz 
RUN tar xf gcc-10.1.0.tar.xz
WORKDIR /gcc_all/gcc-10.1.0 
RUN ./contrib/download_prerequisites
WORKDIR /gcc_all/gcc-10.1.0/build
RUN ../configure --prefix=/usr/local/gcc-10.1.0 --enable-plugin --enable-checking=release --enable-languages=c,c++,fortran --program-suffix=-10.1 --enable-multilib
RUN make -j$(getconf _NPROCESSORS_ONLN)
RUN make install
WORKDIR  /
RUN rm -r gcc_all
# =============================================================================

# =============================================================================
# CREATE A PYTHON VENV AND UPGRADE PYTHON TOOLS
# =============================================================================
ENV VIRTUAL_ENV=/opt/automates_venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade setuptools
RUN pip install wheel
# =============================================================================

# =============================================================================
# SETUP THE AUTOMATES REPOSITORY AND ENVIRONMENT
# =============================================================================
RUN mkdir -p /automates/automates
COPY setup.py /automates/
COPY automates /automates/automates
WORKDIR /automates
RUN pip install -e .
RUN rm -rf automates setup.py
# =============================================================================

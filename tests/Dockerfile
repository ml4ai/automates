FROM        ubuntu:19.10
MAINTAINER  Paul D. Hein <pauldhein@email.arizona.edu>
CMD         bash

# ==============================================================================
# INSTALL SOFTWARE VIA THE UBUNTU PACKAGE MANAGER
# ==============================================================================
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y --no-install-recommends install apt-utils
RUN apt-get -y --no-install-recommends install \
  git curl gcc build-essential \
  pkg-config openjdk-8-jdk antlr4 \
  python3 python3-dev python3-pip \
  graphviz libgraphviz-dev doxygen

RUN git config --global user.email "pauldhein@email.arizona.edu"
RUN git config --global user.name "Paul Hein"
# ==============================================================================

# ==============================================================================
# UPGRADE PYTHON TOOLS
# ==============================================================================
RUN pip3 install --upgrade setuptools
RUN pip3 install wheel
# ==============================================================================

# ==============================================================================
# SETUP THE AUTOMATES REPOSITORY AND ENVIRONMENT
# ==============================================================================
RUN git clone https://github.com/ml4ai/automates
WORKDIR /automates
RUN pip3 install -e .
# ==============================================================================

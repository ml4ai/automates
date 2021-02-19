FROM  ubuntu:20.04
CMD   bash

# ==============================================================================
# INSTALL SOFTWARE VIA THE UBUNTU PACKAGE MANAGER
# ==============================================================================
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y --no-install-recommends install apt-utils
RUN apt-get -y --no-install-recommends install \
  curl gcc build-essential pkg-config openjdk-8-jdk \
  antlr4 graphviz libgraphviz-dev doxygen \
  python3 python3-dev python3-pip python3-venv
# ==============================================================================

# ==============================================================================
# CREATE A PYTHON VENV AND UPGRADE PYTHON TOOLS
# ==============================================================================
ENV VIRTUAL_ENV=/opt/automates_venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade setuptools
RUN pip install wheel
# ==============================================================================

# ==============================================================================
# SETUP THE AUTOMATES REPOSITORY AND ENVIRONMENT
# ==============================================================================
RUN mkdir -p /automates
COPY * /automates/
WORKDIR /automates
RUN pip install -e .
# ==============================================================================

FROM        ubuntu:19.10
MAINTAINER  Paul D. Hein <pauldhein@email.arizona.edu>
CMD         bash

RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:ubuntu-toolchain-r/test \
    && apt-get update \
    && apt-get -y install \
      apt-utils \
      git \
      python3.7 \
      python3-venv \
      doxygen \
      openjdk-8-jdk \
      graphviz

# RUN apt-get -y install python3-numpy python3-scipy python3-matplotlib python3-pandas python3-sympy

# Set up virtual environment
ENV VIRTUAL_ENV=/automates_venv
RUN python3.7 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Add necessary Python packages
ADD requirements.txt /
RUN pip install -r /requirements.txt

RUN git clone https://github.com/ml4ai/automates
RUN git config --global user.email "pauldhein@email.arizona.edu"
RUN git config --global user.name "Paul Hein"

WORKDIR /automates

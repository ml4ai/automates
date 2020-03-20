FROM        ubuntu:19.10
MAINTAINER  Paul D. Hein <pauldhein@email.arizona.edu>
CMD         bash

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get -y install git pkg-config python3 python3-pip openjdk-8-jdk
RUN apt-get -y install graphviz libgraphviz-dev doxygen

# Add necessary Python packages
ADD requirements.txt /
RUN pip3 install -r /requirements.txt

RUN git clone https://github.com/ml4ai/automates
WORKDIR /automates

FROM  ubuntu:20.04
CMD   bash

# ==============================================================================
# INSTALL SOFTWARE VIA THE UBUNTU PACKAGE MANAGER
# =============================================================================
ARG DEBIAN_FRONTEND=noninteractive
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN apt-get update && \
    apt-get -y --no-install-recommends install apt-utils

# Use individual commands to prevent excess time usage when re-building
RUN apt-get -y --no-install-recommends install curl wget gnupg2 git 
RUN apt-get -y --no-install-recommends install openjdk-8-jdk antlr4 doxygen
RUN apt-get -y --no-install-recommends install gcc build-essential pkg-config
RUN apt-get -y --no-install-recommends install python3-dev python3-pip python3-venv

# Add Scala and SBT
RUN wget www.scala-lang.org/files/archive/scala-2.13.0.deb
RUN dpkg -i scala*.deb
RUN echo "deb https://dl.bintray.com/sbt/debian /" | tee -a /etc/apt/sources.list.d/sbt.list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823
RUN apt-get update && apt-get -y --no-install-recommends install sbt

RUN apt-get clean && rm -rf /var/lib/apt/lists/*
# =============================================================================

# =============================================================================
# Add PACKAGES FOR TR PIPELINE
# =============================================================================
RUN update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java
RUN mkdir -p /TR_utils
WORKDIR /TR_utils
RUN git clone https://github.com/lum-ai/regextools.git
WORKDIR /TR_utils/regextools
RUN sbt publishLocal
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
# SETUP THE AUTOMATES TR ENVIRONMENT
# =============================================================================
RUN mkdir -p /text_reading
COPY . /text_reading
WORKDIR /text_reading
RUN pip install -r requirements.txt

# In order for the test suite to work, you need vector files. Run the following to get them:
RUN wget http://vanga.sista.arizona.edu/automates_data/vectors.txt -O /text_reading/src/test/resources/vectors.txt
RUN sbt test
# =============================================================================

# =============================================================================
# PREPARE FOR USE
# =============================================================================
CMD ["sbt", "webapp/run"]
# =============================================================================
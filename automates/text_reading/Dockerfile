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
RUN echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | tee /etc/apt/sources.list.d/sbt.list
RUN echo "deb https://repo.scala-sbt.org/scalasbt/debian /" | tee /etc/apt/sources.list.d/sbt_old.list
RUN curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | apt-key add
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
RUN mkdir -p /automates/automates/text_reading
RUN mkdir -p /automates/automates/apps/pdfalign
COPY automates/text_reading /automates/automates/text_reading
COPY automates/apps/pdfalign /automates/automates/apps/pdfalign
WORKDIR /automates/automates/text_reading
RUN pip install -r requirements.txt

# In order for the test suite to work, you need vector files. Run the following to get them:
RUN wget http://vanga.sista.arizona.edu/automates_data/vectors.txt -O /automates/automates/text_reading/src/test/resources/vectors.txt
RUN sbt -Dapps.projectDir=/automates test
# =============================================================================

# =============================================================================
# PREPARE FOR USE
# =============================================================================
CMD ["sbt", "webapp/run"]
# =============================================================================
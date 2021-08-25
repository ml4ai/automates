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
RUN apt-get -y --no-install-recommends install graphviz libgraphviz-dev
RUN apt-get -y --no-install-recommends install python3-dev python3-pip python3-venv

# Add Scala and SBT
RUN wget www.scala-lang.org/files/archive/scala-2.13.0.deb
RUN dpkg -i scala*.deb
RUN echo "deb https://dl.bintray.com/sbt/debian /" | tee -a /etc/apt/sources.list.d/sbt.list

RUN echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | tee /etc/apt/sources.list.d/sbt.list
RUN echo "deb https://repo.scala-sbt.org/scalasbt/debian /" | tee /etc/apt/sources.list.d/sbt_old.list
RUN curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | apt-key add
RUN apt-get update && apt-get -y --no-install-recommends install sbt

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
# SETUP THE AUTOMATES REPOSITORY AND ENVIRONMENT
# =============================================================================
RUN mkdir -p /automates/automates
COPY setup.py /automates/
COPY automates /automates/automates
WORKDIR /automates
RUN pip install -e .
WORKDIR /automates/automates/text_reading
# In order for the test suite to work, you need vector files. Run the following to get them:
# wget http://vanga.sista.arizona.edu/automates_data/vectors.txt -O /local/path/to/automates/automates/text_reading/src/test/resources/vectors.txt
RUN sbt test
WORKDIR /automates
RUN rm -rf automates setup.py
# =============================================================================

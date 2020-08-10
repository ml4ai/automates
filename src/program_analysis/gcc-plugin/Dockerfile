FROM ubuntu:20.04

# Install required software
RUN apt-get update && \
    yes | apt-get install wget gcc g++ make libtool gcc-multilib

# Download the gcc 9.3.0 tar ball and extract
RUN wget http://ftp.gnu.org/gnu/gcc/gcc-9.3.0/gcc-9.3.0.tar.gz
RUN tar xvf gcc-9.3.0.tar.gz

WORKDIR gcc-9.3.0
RUN ./contrib/download_prerequisites

# Create the build directoy and change into it
RUN mkdir ../gcc-build
WORKDIR /gcc-build

# Set the installation directory, configure the installation for the system, make the initial files needed, and then install the files
RUN export INSTALLDIR=/gcc-9.3.0/install/ 
RUN ../gcc-9.3.0/configure --prefix=$INSTALLDIR --enable-languages=c,c++,fortran --enable-multilib
RUN make -j$(getconf _NPROCESSORS_ONLN) 
RUN make install
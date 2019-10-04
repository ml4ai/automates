FROM ubuntu:18.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
build-essential python-pip cython texlive-full latexmk biber graphviz \
chktex dot2tex imagemagick python-opencv python-plastex python-jinja2 \
python-skimage poppler-utils python-pypdf2 python-poppler \
&& rm -rf /var/lib/apt/lists/*
RUN pip install pdf2image imgaug
RUN pip install -U scikit-image
RUN pip install chainmap
# replace imagemagick's policy with our own to enable PDF support
COPY misc/policy.xml /etc/ImageMagick-6/policy.xml
RUN mkdir -p /equation_extraction/misc
ADD *.py /equation_extraction/
ADD misc/* /equation_extraction/misc/
ADD run_data_collection.sh /equation_extraction/
ADD run_conversion_to_opennmt.sh /equation_extraction/
WORKDIR /equation_extraction

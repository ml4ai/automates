FROM ubuntu:18.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -q update
RUN apt-get -qy install build-essential python-pip cython \
texlive-full latexmk biber graphviz chktex dot2tex imagemagick \
python-opencv python-plastex python-jinja2 python-skimage \
poppler-utils python-pypdf2
RUN pip install pdf2image
# replace imagemagick's policy with our own to enable PDF support
COPY misc/policy.xml /etc/ImageMagick-6/policy.xml
WORKDIR /data

FROM continuumio/miniconda3

RUN conda update -n base -c defaults conda
RUN apt-get install -y build-essential git

# set a directory for all eqdec stuff
RUN mkdir /home/eqdec

# add files
ADD app.py /home/eqdec/app.py
ADD environment.yml /home/eqdec/environment.yml
ADD arxiv2018-downsample-aug-model_step_80000.pt /home/eqdec/model.pt

# make dir for uploaded images
RUN mkdir /home/eqdec/images

# make a new conda environment
RUN conda env create -f /home/eqdec/environment.yml
RUN echo "source activate eqdec" > ~/.bashrc
ENV PATH /opt/conda/envs/eqdec/bin:$PATH

# clone and install opennmt
WORKDIR /home/eqdec
RUN git clone https://github.com/OpenNMT/OpenNMT-py.git
WORKDIR /home/eqdec/OpenNMT-py
RUN python setup.py install

WORKDIR /home/eqdec
EXPOSE 8000
CMD uvicorn --host 0.0.0.0 --reload app:app

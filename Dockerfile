FROM        ubuntu:19.10
MAINTAINER  Paul D. Hein <pauldhein@email.arizona.edu>
CMD         bash

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get -y install git pkg-config python3 python3-pip openjdk-8-jdk
RUN apt-get -y install graphviz libgraphviz-dev doxygen

# Add necessary Python packages
RUN pip3 install pytest==5.4.1 pytest-cov==2.8.1 Pygments==2.3.1 tqdm==4.29.0
RUN pip3 install networkx==2.4 numpy==1.18.2 pandas==1.0.3 sympy==1.5.1
RUN pip3 install scikit_learn==0.22.2.post1 torch==1.4.0 torchtext==0.5.0
RUN pip3 install pygraphviz==1.5 SALib==1.3.8 nltk==3.4.5 WTForms==2.2.1
RUN pip3 install matplotlib==3.2.1 plotly==4.5.4 seaborn==0.10.0
RUN pip3 install Flask==1.1.1 flask_codemirror==1.1 flask_wtf==0.14.3
ENV PYTHONPATH="/automates/src:$PYTHONPATH"

# Clone the repository
RUN git clone https://github.com/ml4ai/automates
WORKDIR /automates

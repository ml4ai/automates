#!/usr/bin/env bash
# This set of commands sets up the AutoMATES demo on a fresh AWS EC2 instance

# Symlink automates demo

sudo ln -sfT ~/automates/demo /var/www/html/automates_demo

# Update package lists
sudo apt-get update
cd
wget https://repo.anaconda.com/archive/Anaconda3-2018.12-Linux-x86_64.sh
bash Anaconda3-2018.12-Linux-x86_64.sh

conda create -n automates
source activate automates
pip install -r requirements.txt

# Install required packages using apt
sudo apt-get install \
  graphviz\
  libgraphviz-dev\
  pkg-config\
  apache2\
  apache2-dev\
  libapache2-mod-wsgi-py3\
  default-jre\



# Clone repos
git clone https://github.com/ml4ai/delphi
mv delphi ../../
sudo ln -sfT ~/delphi /var/www/html/delphi


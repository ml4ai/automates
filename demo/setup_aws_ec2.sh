# This set of commands sets up the AutoMATES demo on a fresh AWS EC2 instance

# Symlink automates demo

sudo ln -sfT ~/automates/demo /var/www/html/automates_demo

# Update package lists
sudo apt-get update

# Install required packages using apt
sudo apt-get install \
  graphviz\
  libgraphviz-dev\
  pkg-config\
  python3-pip\
  apache2\
  libapache2-mod-wsgi-py3\
  default-jre\
  python3-flask

# Install virtualenv
sudo pip3 install virtualenv

# Clone repos
git clone https://github.com/ml4ai/delphi
sudo ln -sfT ~/delphi /var/www/html/delphi
sudo virtualenv venv
. venv/bin/activate
sudo pip3 install -r requirements.txt

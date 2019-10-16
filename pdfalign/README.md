# pdfalign annotation tool 

## Setup instructions (using the Anaconda Python distribution)

    conda create -n pdfalign python=3 --yes
    conda activate pdfalign

    conda install lxml pillow chardet pycryptodome sortedcontainers six poppler --yes
    pip install webcolors pdf2image

    # install the ml4ai fork of pdfminer
    pip install -e git+ssh://git@github.com/ml4ai/pdfminer.six.git#egg=pdfminer.six

    # for mac only, install tk
    conda install -c anaconda tk

If you need to remove the conda environment:

    conda remove -n pdfalign --all

## Setup instructions (without Anaconda)

Here we give instructions for installing pdfalign without Anaconda, just using
pip and a package manager.

### MacOS

#### XQuartz

Install XQuartz from https://www.xquartz.org

If you don't have a package manager, get one. Homebrew and MacPorts are the
most popular ones.

#### MacPorts

  sudo port install tk +quartz
  sudo port install poppler

#### Homebrew

  brew install tcl-tk
  brew install poppler

#### Creating and activating a virtual environment for pdfalign

Create and activate a virtual environment for pdfalign.

##### Using venv

You may want to create a directory for your virtual environments, let's say
`~/.venvs` - and if you wanted to create a virtual environment named `pdfalign`
within that directory, you could do:

  mkdir -p ~/.venvs
  python -m venv ~/.venvs/pdfalign pdfalign --system-site-packages

(The `--system-site-packages` flag is required when using MacPorts to give the
virtual environment access to the `_tkinter.so` extension.)

Then activate the virtual environment with:

  source ~/.venvs/pdfalign/bin/activate

##### Using virtualenvwrapper

    # Create new python venv (the name venv_pdfalign is arbitrary):
    python3 -m venv venv_pdfalign

    # Activate the virtual environment.
    workon venv_pdfalign


#### Installing pdfalign dependencies

Once the virtual environment is activated, then in this directory, run the
following commands to install the package and its dependencies.

  pip install -e git+ssh://git@github.com/ml4ai/pdfminer.six.git#egg=pdfminer.six
  pip install lxml webcolors pdf2image

#### Installing pdfalign

You can either just get the pdfalign script using 
  
  curl -O https://raw.githubusercontent.com/ml4ai/automates/master/pdfalign/pdfalign.py

Or install it as a package within the virtual environment, with an entry point
  
  git clone https://github.com/ml4ai/automates
  cd automates/pdfalign
  pip install -e .

#### Running pdfalign

If you just downloaded the script using `curl`, you can launch `pdfalign` with

  python pdfalign.py

If you installed the package, you can instead just type
  
  pdfalign

to launch the program.

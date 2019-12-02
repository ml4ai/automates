# pdfalign annotation tool 

PDFAlign is a tool to facilitate annotation of mathematical formula identifiers
in scientific papers and link them to their textual descriptions.

![Snapshot of the our annotation tool, PDFAlign, currently part way through annotation the first mathematical for-
mula of arXiv paper
1801.00269](http://vanga.sista.arizona.edu/automates_data/pdfalign_1801-00269_equation0000.png)

## 1. Setup instructions (using the Anaconda Python distribution)

    conda create -n pdfalign python=3 --yes
    conda activate pdfalign

    conda install lxml pillow chardet pycryptodome sortedcontainers six poppler texlive-core --yes
    pip install webcolors pdf2image tqdm

    # install the ml4ai fork of pdfminer
    pip install -e git+https://github.com/ml4ai/pdfminer.six.git#egg=pdfminer.six

    # for mac only, install tk
    conda install -c anaconda tk

If you need to remove the conda environment:

    conda remove -n pdfalign --all

## 2. Setup instructions (without Anaconda)

Here we give instructions for installing pdfalign without Anaconda, just using
pip and a package manager.

### 2.1 MacOS

#### 2.1.1 XQuartz

If you don't already have it, install XQuartz from https://www.xquartz.org

If you don't have a package manager, get one. Homebrew and MacPorts are the
most popular ones.

#### 2.1.2 Installing dependencies using package manager

Install non-Python dependencies using your package manager - the commands for
MacPorts and Homebrew are given below.

##### 2.1.2.1 MacPorts

    sudo port install tk +quartz
    sudo port install poppler

##### 2.1.2.2 Homebrew

    brew install tcl-tk
    brew install poppler

#### 2.1.3 Creating and activating a virtual environment for pdfalign

Create and activate a virtual environment for pdfalign, using one of the two
methods below.

##### 2.1.3.1 Using venv

You may want to create a directory for your virtual environments, let's say
`~/.venvs` - and if you wanted to create a virtual environment named `pdfalign`
within that directory, you could do:

    mkdir -p ~/.venvs
    python -m venv ~/.venvs/pdfalign pdfalign --system-site-packages

(The `--system-site-packages` flag is required when using MacPorts to give the
virtual environment access to the `_tkinter.so` extension.)

Then activate the virtual environment with:

    source ~/.venvs/pdfalign/bin/activate

##### 2.1.3.2 Using virtualenvwrapper

If you instead use virtualenvwrapper, do:

    # Create new python venv (the name venv_pdfalign is arbitrary):
    python3 -m venv venv_pdfalign

    # Activate the virtual environment.
    workon venv_pdfalign


#### 2.1.4 Installing pdfminer

Once the virtual environment is activated, then in this directory, run the
following commands to install the pdfminer package:

    pip install -e git+ssh://git@github.com/ml4ai/pdfminer.six.git#egg=pdfminer.six

#### 2.1.5 Installing and launching pdfalign

Install additional Python dependencies and launch `pdfalign` using one of the two
methods below.

##### 2.1.5.1 Using curl

You can either just get the `pdfalign` script and its dependencies using 
  
    pip install lxml webcolors pdf2image tqdm
    curl -O https://raw.githubusercontent.com/ml4ai/automates/master/pdfalign/pdfalign.py

Then, launch it with:

    python pdfalign.py

##### 2.1.5.2 Installing pdfalign as a package

Or install it as a package within the virtual environment, with an 'entry point'.
  
    git clone https://github.com/ml4ai/automates
    cd automates/pdfalign
    pip install -e .

Then, launch it with:

    pdfalign

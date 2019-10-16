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

Below we give instructions for MacPorts. The commands for Homebrew are likely
similar, but without the `sudo`, and replacing `port` with `brew`.

#### Installing tk and poppler using MacPorts

```
sudo port install tk +quartz
sudo port install poppler
```

#### Creating and activating a virtual environment for pdfalign

Create a virtual environment for pdfalign. For example, you may want to create
a directory `~/.venvs` for your virtual environments - and if you wanted to
create a virtual environment named `pdfalign` within that directory, you could
do:

```
mkdir -p ~/.venvs
python -m venv ~/.venvs/pdfalign pdfalign --system-site-packages
```

(The `--system-site-packages` flag is required when using MacPorts to give the
virtual environment access to the `_tkinter.so` extension.)

Then activate the virtual environment with:

```
source ~/.venvs/pdfalign/bin/activate
```

#### Installing pdfalign

Once the virtual environment is activated, then in this directory, run the
following commands to install the package and its dependencies.

```
pip install -e git+ssh://git@github.com/ml4ai/pdfminer.six.git#egg=pdfminer.six
pip install -e .
```

#### Running pdfalign

Then you can launch `pdfalign` with the following command:

```
pdfalign
```

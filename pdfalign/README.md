# pdfalign annotation tool 

## Setup instructions (assuming the presence of the Anaconda Python distribution)

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

## Setup instructions with pip and OS-specific package managers

# MacOS (MacPorts)

Install XQuartz: https://www.xquartz.org

```
sudo port install tk +quartz
sudo port install poppler
```

(If you use Homebrew, there are probably analogous commands, like `brew install poppler`)

# pip (OS-independent)

Install the required Python packages (you should probably create and activate a
virtual environment for this).

```
pip install lxml pillow chardet pycryptodome sortedcontainers six webcolors pdf2image
pip install -e git+ssh://git@github.com/ml4ai/pdfminer.six.git#egg=pdfminer.six
```

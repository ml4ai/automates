# pdfalign annotation tool 

## Setup instructions

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

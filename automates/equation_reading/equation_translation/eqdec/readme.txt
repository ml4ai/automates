* Installation

In order to use the eqdec app, you must first, copy the model file. 
The model file is located in the Google Drive here:

    ASKE-AutoMATES/Data/equation_decoding/arxiv2018-downsample-aug-model_step_80000.pt

Copy that file to this location in your local AutoMATES repo:

    <automates_root>/automates/equation_reading/equation_translation/eqdec


* Use

The following commands are assumed to be executed in the following
directory context of your local AutoMATES repo:

    <automates_root>/automates/equation_reading/equation_translation

To build the docker container:

    docker build -t eqdec .

To launch the server:

    docker run -d -p 8000:8000 -t eqdec

Access the API documentation at http://localhost:8000/docs

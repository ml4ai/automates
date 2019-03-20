### Equation Detection and Parsing

#### Architecture

>TODO: Description of current state of the overall equation reading architecture.
Possibly include a figure (architecture diagram)?

>TODO: describe lessons learned so far, state of the art methods tried, shortcomings, plans/strategies for adapting. Summarize results, include figures.

- data collection
- equation detection
    - mask-rcnn implementation
        - ignore mask, basically just faster rcnn
        - single class (equation)
            - in future: titles, tables, etc
- decoding image to pdf
    - pretrained model with image preprocessing
    - train custom model from collected data
    - data augmentation (not done)
    - currently pretrained model is highly sensitive to exact preprocessing pipeline (i.e. font and font size, dimensions, background, etc)
        this restrictiveness prevents a straight forward interaction between the detection model and the decoder, as the detected equations will be
        whatever size and font they appeared in the original paper. in order to lessen this restriction we will train the model with augmented data ...
    - ensuring grammatical output
        - maybe crf
        - or something else (see ai2 paper)
    - reimplement in (prob pytorch) to be able to extend model and run on cpu
- conversion to sympy

#### Instructions for running components

>TODO: Describe how each individual component of the equation pipeline works, so someone could train/run if desired.

- detection will be in docker container
- decoding is in singularity container (needs gpu)
- sympy can be anywhere

#### Data set

>TODO: Description of dataset and how to obtain it.

- link to pretrained model
- arxiv currently on UofA servers
- provide scripts to unpack and extract training data

#### Updates

>TODO: Summary (bullet points) of updates since last report.

- macro expansion
- template rescaling
- reproduced results from original paper
- trained custom model
- processed data to train detection model
- added latex-to-sympy component (WIP)

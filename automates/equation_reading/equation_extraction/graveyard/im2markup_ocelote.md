# Im2Markup on Ocelote
***

## Testing the Model
### Use Ocelote High Performance Computing Cluster


To log into Ocelote: ```ssh username@hpc.arizona.edu```

You will be asked for a password and two-factor authentication. (Follow these [instructions](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-on-ubuntu-1604) to bypass this step on future logins.) Next, specify the cluster: ```ocelote```

Your ```$HOME``` and PBS directories are limited to 15GB in total. Use ```/extra/username``` storage to prevent disk space errors. 

```
USER=$(whoami)
cd /extra/$USER
```

### Download Data & Scripts
While [Yuntian Deng's study](https://arxiv.org/abs/1609.04938) analyzed the full [im2latex-100k](https://zenodo.org/record/56198#.XFEhQ89KjMV) dataset, we use a [smaller sample dataset](https://github.com/harvardnlp/im2markup) for this exercise. The sample dataset, Python and Lua scripts can be cloned from the [**im2markup**](https://github.com/harvardnlp/im2markup) GitHub repository:

```
git clone https://github.com/harvardnlp/im2markup.git
cd im2markup
```


### Download Singularity Images
The [UA-hpc-containers](https://www.singularity-hub.org/collections/2226) Singularity Hub contains a repository of Singularity images and recipes for the [AutoMATES team](https://ml4ai.github.io/automates/).

We will run the Singularity image on the cluster. Create a folder to store containers:

```
mkdir containers
cd containers
```

We built [containers](https://www.singularity-hub.org/containers/6652) for (1) the Python pre-processing & evaluation steps and (2) the [**im2markup**](https://github.com/harvardnlp/im2markup) model training/testing step. The Singularity image for the model was built to run CUDA and Torch on NVIDIA GPUs in [Ocelote](https://docs.hpc.arizona.edu/display/UAHPC/Ocelote+Quick+Start).

To load Singularity and download the images:

```
module load singularity
singularity pull shub://ml4ai/UA-hpc-containers:torch
singularity pull shub://ml4ai/UA-hpc-containers:im2markup
```

_Further Reading_: [Quick Start Guide to Singularity](https://singularity.lbl.gov/quickstart#download-pre-built-images)


### Preprocess Data
##### DISCLAIMER: I preprocessed the data on my local machine before scp-ing the data & pre-processed goods to the HPC, so I need to create the PBS script for this step. For now, preprocess the data by running the scripts locally on your machine. When you scp the files, ensure that the resulting files/directories are located in the appropriate directory on the HPC by analyzing the  ```--output-dir``` flag of the following commands. The data products MUST be pre-processed in order for the model to run!!!

```
python scripts/preprocessing/preprocess_images.py --input-dir data/sample/images --output-dir data/sample/images_processed
python scripts/preprocessing/preprocess_formulas.py --mode normalize --input-file data/sample/formulas.lst --output-file data/sample/formulas.norm.lst
```

```
python scripts/preprocessing/preprocess_filter.py --filter --image-dir data/sample/images_processed --label-path data/sample/formulas.norm.lst --data-path data/sample/train.lst --output-path data/sample/train_filter.lst 
python scripts/preprocessing/preprocess_filter.py --filter --image-dir data/sample/images_processed --label-path data/sample/formulas.norm.lst --data-path data/sample/validate.lst --output-path data/sample/validate_filter.lst 
python scripts/preprocessing/preprocess_filter.py --no-filter --image-dir data/sample/images_processed --label-path data/sample/formulas.norm.lst --data-path data/sample/test.lst --output-path data/sample/test_filter.lst 
```

```
python scripts/preprocessing/generate_latex_vocab.py --data-path data/sample/train_filter.lst --label-path data/sample/formulas.norm.lst --output-file data/sample/latex_vocab.txt
```
To secure copy the data and scripts to the HPC from your local machine:

```
scp -r local_directory username@filexfer.hpc.arizona.edu:/extra/username/im2latex/
```

### Download the Trained Model
To download the trained model to the HPC:

```
cd /extra/$USER/im2markup
mkdir -p model/latex
wget -P model/latex/ http://lstm.seas.harvard.edu/latex/model/latex/final-model
```


### Portable Batch System (PBS) Scripts
The PBS scripts are not required to run from your home directory.  

```
cd ~
touch script_test.pbs
```

Use your favorite text editor and copy the following code into the text file:

```~/script_test.pbs```.

```
# Your job will use 1 node, 28 cores, and 224gb of memory total.
#PBS -q standard
#PBS -l select=1:ncpus=28:mem=224gb:ngpus=1

### Specify a name for the job
#PBS -N im2latex

### Specify the group name
#PBS -W group_list=claytonm

### Used if job requires partial node only
#PBS -l place=pack:exclhost

### CPUtime required in hhh:mm:ss.
### Leading 0's can be omitted e.g 48:0:0 sets 48 hours
#PBS -l cput=00:28:00

### Walltime is how long your job will run
#PBS -l walltime=00:02:00

### Joins standard error and standard out
#PBS -o im2latex.o
#PSB -e im2latex.e

### Sends e-mail when job aborts/ends
#PBS -m ae
#PBS -M username@email.arizona.edu

### Checkpoints job after c (integer min) CPU time
#PBS -c c=2

##########################################################

module load singularity

### DIRECTORIES / NAMES ###
USER=$(whoami)
CONTAINER=containers/UA-hpc-containers_torch.sif
MODEL=model/latex
DATA=data/sample
IMAGES=$DATA/images_processed
RESULTS=$DATA/results
LOGS=$DATA/logs
LOGNAME=im2latex

cd /extra/$USER/im2markup/
mkdir --parents $RESULTS $LOGS

##########################################################

date +"Start - %a %b %e %H:%M:%S %Z %Y"

singularity exec --nv $CONTAINER th src/train.lua \
-phase test  \
-gpu_id 1    \
-load_model  \
-visualize   \
-model_dir     $MODEL     \
-data_base_dir $IMAGES    \
-output_dir    $RESULTS   \
-data_path     $DATA/test_filter.lst    \
-label_path    $DATA/formulas.norm.lst  \
-max_num_tokens   500  \
-max_image_width  800  \
-max_image_height 800  \
-batch_size       5    \
-beam_size        5

date +"End - %a %b %e %H:%M:%S %Z %Y"

# Renames Log Files
export STAMP=$(date +"%Y%m%d_%H%M%S")
mv log.txt $LOGS/$LOGNAME_$STAMP.log
```

Ensure to change the e-mail address ```username@email.arizona.edu``` in the script to receive updates when the job terminates or is aborted.

### Submitting a Job on the HPC
From the directory containing ```script_test.pbs```, submit the job to Ocelote's PSB scheduler:

```
qsub script_test.pbs
```

Once the job has been submitted to the scheduler, you can check the status of your jobs via

```
qstat -u $USER
```

You can also peek at the progress of your script with

```
qpeek <jobid>
```

or interactively with [Open OnDemand](https://ood.hpc.arizona.edu/pun/sys/dashboard/apps/show/activejobs). The total compute time for testing is <2 minutes with exclusive access to 28 cores on 1 GPU on Ocelote.

### Debugging

```
uquota
```

```
module load unsupported
module load ferng/find-pbs-files
pbs-files $USER
```

When debugging, it maybe helpful to run the code interactively:

```
qsub -I script_test.pbs
```
Make sure there is no file called ```log.txt``` in ```/extra/$USER/im2markup```; otherwise, the logging script called by the ```im2markup``` model will continuously prompt the user for instructions to overwrite/append the ```log.txt``` file until all allocated time is used.

***
## Evaluating the Model

### Scripts & Data
```
```

### Portable Batch System (PBS) Scripts
```
python scripts/evaluation/evaluate_text_edit_distance.py --result-path results/results.txt
```

### Submitting a Job on the HPC
```
```


### notes march 15

```
conda create -n im2markup python=2.7
source activate im2markup
conda install numpy pillow
(install node.js)

git clone git@github.com:harvardnlp/im2markup.git
(follow preprocessing steps above)
tar czvf im2markup.tar.gz im2markup
```

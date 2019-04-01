# Running the equation decoder

### Getting set-up

1. Make you have access to a GPU

2. Install Singularity with GPU support:

   - Singularity homepage: <https://www.sylabs.io/docs/>
   - Typically, singularity images are run on HPCs...

3. Pull the singularity container from singularity hub OR build it yourself

   - pulling from singularity hub: `singularity pull shub://ml4ai/UA-hpc-containers:im2markup`
   - [build from the recipe file](https://singularity.lbl.gov/docs-build-container#building-containers-from-singularity-recipe-files) provided in the repository [here](https://github.com/ml4ai/automates/blob/2f5c2499152c0d9dd27f5ad6b9b1ecb95999a110/equation_extraction/containers/Singularity.im2markup)

4. Download Data & Scripts from Deng et al., (2017): 

   1. Python and Lua scripts can be cloned from the [im2markup](https://github.com/harvardnlp/im2markup) GitHub repository:

      ```
      git clone https://github.com/harvardnlp/im2markup.git
      cd im2markup
      ```

5. Preprocess Data:

    - This library expects to have the gold formulas (`formulas.norm.lst` in the script below), even during inference because the evaluation code is always called.  We can avoid this requirement by provided random strings as the gold formulas so that the input is in the right format, but we don't cheat (and we don't have to know the answer before we ask the question)!  

      The format of this random string formula file we generate is:

      ```
        x x x
        x x x
        x x x
        ...
      ```
      The library also wants to have list of the images to be decoded (`test_filter.lst` in the script below).  

      The format of this file is:

      ```
        equation0.png 0
        equation1.png 1
        equation2.png 2
        equation3.png 3
        ...
      ```

      We generate these files in the process of formatting the images with [ImageMagick](https://www.imagemagick.org) using [this bash script](https://github.com/ml4ai/automates/blob/d14c69372b7cd20f6085812f66970b0bd9230409/equation_extraction/convert_to_png.sh) (please modify as needed).  

    - Then, preprocess the images:

    ```
    cd im2markup
    python scripts/preprocessing/preprocess_images.py --input-dir <path_to_images> --output-dir <path_to_output_images_processed>
    ```

 6. Download the Trained Model:

     ```
     mkdir -p model/latex
     wget -P model/latex/ http://lstm.seas.harvard.edu/latex/model/latex/final-model
     ```



###Running the model on your equation images

At the University of Arizona, we run the code on the HPC.  This is the PBS script we use to do so.  Please modify to meet your needs. 

script: ```~/script_test.pbs```

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

We submit this job using the above script on the HPC:

```
qsub script_test.pbs
```

The results (i.e., predicted LaTeX equations) will be in the `RESULTS` directory specificed in the pbs script.


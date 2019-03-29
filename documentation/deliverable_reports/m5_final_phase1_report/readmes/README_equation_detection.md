# Running the equation detection module

1. Clones the AutoMATES [mask-rcnn repo]() 

2. Clone the [matterport Mask-RCNN](https://github.com/matterport/Mask_RCNN) repo inside our repo

   cd maskrcnn

   git clone https://github.com/matterport/Mask_RCNN.git

3. Download and extract data 

   - Contact us for the file, we don't have rights to post...

     cd maskrcnn

     tar -zxvf output_objdet.tar.gz

4. Put the extracted `equation` directory in the ...

`equations` inside MaskRCNN repo, `maskrcnn/Mask_RCNN/samples/equation`

5. Build the docker container
6. Run the docker container using the desired mode and base model

training/inference based on argument in script, tell where data lives

at beginning we have examples

inside docker container, wdir = /data so when running, we have to map our dir to /data

shell s
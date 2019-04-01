# Running the equation detection module

1. Clones the [AutoMATES repo](https://github.com/ml4ai/automates) 

2. Clone the [matterport Mask-RCNN](https://github.com/matterport/Mask_RCNN) repo inside the detection subdirectory

   ```
   cd automates/equation_extraction/detection
   git clone https://github.com/matterport/Mask_RCNN.git
   ```

3. Download and extract data 

   - Contact us for the data tar file, we don't have rights to post...

     ```
     tar -zxvf output_objdet.tar.gz
     ```


5. Build the docker container

    ```
    docker build -t maskrcnn-gpu .
    ```

6. Run the docker container using the desired mode (train or detect) and base model (i.e., imagenet)

   - train:

     ```
     sudo ./docker.sh python3 equation.py train --dataset=dataset --subset=train --weights=imagenet
     ```

   - detect (i.e., find AABBs for the test images):

     ```
     sudo ./docker.sh python3 equation.py detect --dataset=dataset --subset=test --weights=last
     ```

     Note: updates with corresponding timestamps will be added with more information regarding the detection model training and evaluation. 


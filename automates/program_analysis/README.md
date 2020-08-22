# Program Analysis Module

### PA Docker Image
The Dockerfile in this directory is used to create docker image tagged `pa` under the ML4AI Lab AUTOMATES DockerHub repository. You can pull that image using the command:
`docker pull ml4ailab/automates:pa`

##### Running the PA programming idiom tests
Start the PA docker container using the following command which will mount your local checkout of AUTOMATES prgoramming-idioms test examples into the docker container for testing/inspection:
`docker run -it --mount type=bind,src=<path/to/local/copy/of/ASKE-AutoMATES/Data/programming-idioms>,dst=/programming-idioms ml4ailab/automates:pa bash`

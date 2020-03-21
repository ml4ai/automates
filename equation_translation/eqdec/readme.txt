First, copy the model file to the current directory.
Then, to build the docker container:

    docker build -t eqdec .

To launch the server:

    docker run -d -p 8000:8000 -t eqdec

Access the API documentation at http://localhost:8000/docs

# Using the Docker containers for the ScienceParse and GrobidQuantities clients

First, launch the containers:

    cd automates/text_reading/docker
    docker-compose up

The first time, it will take a little while, as things are downloading.  Subsequent runs should be much faster.
There are two different docker containers being loaded, when they are both ready you can use them!

Note: science parse is known to be memory intensive, see [this](https://github.com/allenai/science-parse/blob/master/server/README.md#running-the-server-yourself) for details.

## Running only one of the services

If you want to only run one of the services (either scienceparse or grobid) you can do so by giving docker-compose
the name of the service you want to call, for example:

    docker-compose up grobidquantities

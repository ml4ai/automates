

1) Build the automates docker image but do not delete the automates source like the end of the docker file does (docker build -t automates/local .)
2) In the automates app dir, run `docker-compose up --build -d`

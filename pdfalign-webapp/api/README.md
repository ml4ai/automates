#### Description

This directory holds the code for the API used by the pdf align web app. This service offers several endpoints that support annotating papers, managing the processing of papers, and storing their annotations.

#### Endpoints


#### Deploying application

#### Running locally

##### Python Dependencies

See requirements.txt for python app dependencies.

##### Anaconda

##### Virtual env

1) create venv

2) `pip install -r requirements.txt`

##### Running Postgres

First, ensure that [docker](https://docs.docker.com/v17.09/engine/installation/) is installed and running. Additionally, make sure [docker-compose](https://docs.docker.com/compose/install/) is installed.

From the root directory of pdfalign-webapp

```
cd env
docker-compose up -d
```

Postgres should now be running. To verify, run `docker ps` and verify a container is running postgres.

Next, run the migration scripts. To generate and execute, run the following commands from the root directory of pdfalign-webapp.

```
python manage.py db init  # Initialize script directory
python manage.py db migrate --message 'initial database migration'  # Create the migration scripts
python manage.py db upgrade  # Apply the migration scripts
```

This will create a directory called migrations containing the scripts.

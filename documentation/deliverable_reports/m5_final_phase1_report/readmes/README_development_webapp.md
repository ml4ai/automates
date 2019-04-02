---
title: README for the development webapp
---

# Running the Development Webapp

1. Install [docker](https://docs.docker.com/install/)

2. Install [Java 8](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)

3. Install [sbt](https://www.scala-sbt.org/release/docs/Setup.html)

4. Clone the [automates repo](https://github.com/ml4ai/automates)

5. Go to the text reading docker subdirectory and launch the grobid-quantities docker container

   ```
   cd automates/text_reading/docker
   docker-compose up grobidquantities
   ```

6. In another session, go to the main text reading subdirectory and launch the webapp
    ```
    cd automates/text_reading
    sbt webapp/run
    ```

    **Note:** The first time you run this, it will take a while because it is downloading and installing scala as well as the library dependencies and compiling the code.  Subsequent runs will be MUCH faster. 

7. Open a browser and go to `localhost:9000`

8. Enter text, click `submit`.  The first query will take longer (~60 seconds) because of model loading.  Subsequent queries will be much faster.


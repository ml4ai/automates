---
title: README for the ExtractAndAlign entrypoint
---

# Running text reading pipeline to generate GrFN with Alignments

1. Install [docker](https://docs.docker.com/install/)

2. Install [Java 8](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)

3. Install [sbt](https://www.scala-sbt.org/release/docs/Setup.html)

4. Clone the [automates repo](https://github.com/ml4ai/automates)

5. Go to the text reading docker subdirectory and launch the grobid-quantities docker container

   ```
   cd automates/text_reading/docker
   docker-compose up grobidquantities
   ```

6. In another session, go to the main text reading subdirectory and run the pipeine:

   `sbt "runMain org.clulab.aske.automates.apps.ExtractAndAlign"

7. If needed, modify the settings in the [configuration file](https://github.com/ml4ai/automates/blob/master/text_reading/src/main/resources/automates.conf)


FROM ubuntu:18.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -q update
RUN apt-get -qy install build-essential git openjdk-8-jdk
WORKDIR /
RUN git clone https://github.com/kermitt2/grobid.git
WORKDIR /grobid
RUN git checkout 0.5.3
RUN ./gradlew clean install
RUN git clone https://github.com/kermitt2/grobid-quantities.git
WORKDIR /grobid/grobid-quantities
RUN ./gradlew clean install copyModels
RUN ./gradlew appRun
EXPOSE 8060
CMD ["./gradlew", "appStart"]

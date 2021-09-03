from automates/local:latest

ENV FLASK_APP=automates.apps.automates.automates

EXPOSE 80

#COPY /home/dpdicken/dev/automates/ /automates/
#VOLUME /automates/ /home/dpdicken/dev/automates/ 

WORKDIR /automates/automates/program_analysis/gcc_plugin/plugin
#RUN ls
RUN make clean && make linux

WORKDIR /automates
ENTRYPOINT python3 -m flask run --host=0.0.0.0 --port=80

#ENV FLASK_APP=automates
#RUN python3 -m flask run --host=0.0.0.0 --port=80


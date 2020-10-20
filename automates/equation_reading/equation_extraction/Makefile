IMAGE=clulab/equations

.PHONY: dockerize

all: dockerize

dockerize: Dockerfile
	docker build -t $(IMAGE) .

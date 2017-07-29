

.PHONY: dockerimage test


all: 
	@echo make image --> Pull centos:7 and build a docker image called roletest 
	@echo make test --> Run the role in the docker image called roletest


image: Dockerfile
	docker pull centos:7
	docker build -t roletest:centos7 .

test: Dockerfile
	@echo Not yet implented 1>&2
	exit 1


#!/bin/bash

###
### Build Docker images required to run the API server and push
### them to a container registry.
###

SCRIPT_DIR="$(dirname $0)"
docker-compose -f "${SCRIPT_DIR}/../build.yml" build lawliet-hub
docker tag lawliet-hub wshand/lawliet-hub:latest
docker push wshand/lawliet-hub:latest

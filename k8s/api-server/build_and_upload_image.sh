#!/bin/bash

set -e

docker build -t penlite-k8s-api-server:latest .
docker tag penlite-k8s-api-server:latest michaelmdresser/penlite:k8s-api-server-latest
docker push michaelmdresser/penlite:k8s-api-server-latest

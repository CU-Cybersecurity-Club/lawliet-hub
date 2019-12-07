#!/bin/bash

set -e

docker build -t penlite-k8s-api-server:latest .
docker tag penlite-k8s-api-server:latest gcr.io/csci5253-datacenter/penlite-k8s-api-server:latest
docker push gcr.io/csci5253-datacenter/penlite-k8s-api-server:latest

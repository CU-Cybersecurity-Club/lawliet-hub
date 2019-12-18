#!/bin/bash

set -e

docker build -t lawliet-k8s-api-server:latest .
docker tag lawliet-k8s-api-server:latest michaelmdresser/lawliet:k8s-api-server-latest
docker push michaelmdresser/lawliet:k8s-api-server-latest

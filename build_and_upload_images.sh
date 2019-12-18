#!/bin/bash

set -e

pushd docker

docker build -t lawliet:test-vnc -f Dockerfile.vnc .
docker tag lawliet:test-vnc michaelmdresser/lawliet:vnc-latest
docker push michaelmdresser/lawliet:vnc-latest

popd

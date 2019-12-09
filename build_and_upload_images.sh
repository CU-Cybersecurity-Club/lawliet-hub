#!/bin/bash

set -e

pushd docker

docker build -t penlite:test-vnc -f Dockerfile.vnc .
docker tag penlite:test-vnc michaelmdresser/penlite:vnc-latest
docker push michaelmdresser/penlite:vnc-latest

popd

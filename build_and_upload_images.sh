#!/bin/bash

set -e

pushd docker

docker build -t penlite:test -f Dockerfile .
docker build -t penlite:test-vnc -f Dockerfile.vnc .
docker tag penlite:test gcr.io/csci5253-datacenter/penlite:test
docker tag penlite:test-vnc gcr.io/csci5253-datacenter/penlite:test-vnc
docker push gcr.io/csci5253-datacenter/penlite:test
docker push gcr.io/csci5253-datacenter/penlite:test-vnc

popd

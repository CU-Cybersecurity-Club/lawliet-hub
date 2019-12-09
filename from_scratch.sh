#!/bin/bash
set -e

echo "assumes project is named 'csci5253-datacenter', this needs work"
echo "remove exit if this is the case"
exit 1

gcloud container clusters create --preemptible mykube
./build_and_upload_images.sh

pushd k8s
./full_deploy.sh
popd

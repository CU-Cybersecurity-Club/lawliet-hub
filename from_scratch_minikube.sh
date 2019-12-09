#!/bin/bash
set -e

./build_and_upload_images.sh

pushd k8s
./full_deploy_minikube.sh
popd

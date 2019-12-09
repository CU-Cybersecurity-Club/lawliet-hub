#!/bin/bash

set -e

./edit-kubelets_minikube.sh
pushd api-server
./deploy.sh
popd

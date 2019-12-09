#!/bin/bash

set -e

./edit-kubelets.sh
pushd api-server
./deploy.sh
popd

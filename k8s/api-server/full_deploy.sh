#!/bin/bash

set -e

./build_and_upload_image.sh

kubectl apply -f api-server-serviceaccount.yaml
kubectl apply -f api-server-role.yaml
kubectl apply -f api-server-role-binding.yaml
kubectl apply -f api-server-deployment.yaml
kubectl apply -f api-server-svc.yaml

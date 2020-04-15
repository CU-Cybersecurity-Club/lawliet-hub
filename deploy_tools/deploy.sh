#!/bin/bash

K8S_DIR="$(dirname $0)/../k8s"

set -e

kubectl apply -f "$(K8S_DIR)/api-server-serviceaccount.yaml"
kubectl apply -f "$(K8S_DIR)/api-server-role.yaml"
kubectl apply -f "$(K8S_DIR)/api-server-role-binding.yaml"
kubectl apply -f "$(K8S_DIR)/api-server-deployment.yaml"
kubectl apply -f "$(K8S_DIR)/api-server-svc.yaml"

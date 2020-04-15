# API Server

This is the meat of the Hub's Kubernetes code. It contains the main server code as well as specifications for the Docker container and all necessary Kubernetes resources.

## `deploy.sh`
The main deployment script: creates all necessary Kubernetes resources. This method of deployment should probably be deprecated in favor of a Helm chart. Does not build/upload latest images - that must be done with `build_and_upload_image.sh`.

## `pod-api-server.py`
The main server code. A Flask server that interfaces with the Kubernetes API to provide a simplified interface for creating, inspecting, deleting, and "cleaning up" containers. The API is documented in the top-level README.

## `Dockerfile`
The specification for the server's Docker image. It is a relatively straightforward container build on Alpine Linux.

## `build_and_upload_image.sh`
A convenience script for a developer when working on the server code and testing in a Kubernetes environment. Example usage:
```
./build_and_upload_image.sh && k delete pod -l app=lawliet-k8s-api-server && k logs -l app=lawliet-k8s-api-server -f
```

## Some example requests that can be run from within the cluster for testing
Please note that SSH key support is currently disabled - considered unnecessary due to a focus on graphical environments.
```
curl -XPUT lawliet-k8s-api-server/container/testssh2 --data-urlencode "ssh_key=$(cat /root/.ssh/id_rsa.pub)"
curl -XDELETE lawliet-k8s-api-server/container/testssh2
curl -XPOST lawliet-k8s-api-server/container/cleanup --data-urlencode "minutes_alive=720"
```

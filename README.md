# penlite
CSCI 4253/5253 Fall 2019 Course Project


## Architecture

### Containerized Penetration Testing Environments
The core of the project is the containers we provide. They are the penetration testing environments
that we provide for our users. Everything else just smooths out the process of getting these containers
and accessing them.

##### Regular
The regular container is the current kali image with metasploit and ssh added on top. The one tricky bit is making `/dev/net/tun`, which is necessary for OpenVPN to work successfully. If this was a one-off container we could just add the host's `/dev/net/tun` or just run the container in `privileged` mode, but those obviously aren't good ideas on a "multi-tenant" system like this.

##### Regular + VNC
This is the regular container with a vnc server (tigervnc + xxfce) added on top. Most of the extra work in the Dockerfile is setting up the vnc server, gratefully stolen from [kernelmethod/dockerfiles](https://github.com/kernelmethod/dockerfiles).

### Website
This is the main interface for all of our users. This is where they can sign up, manage credentials, launch environments, get access to environments, and close environments. It is exposed as a service internal to the cluster.

### Kubernetes API Server
This is a wrapper around several calls to the Kubernetes API to provide an easy interface for internal services to create, delete, and cleanup pods. It is exposed as a service internal to the cluster.

### Proxy
This is a standard proxy, redirecting primary web traffic to the website and all user sessions (such as SSH and VNC traffic) to the respective user environments. It is exposed as a service external to the cluster.

### Diagram
![Architecture Diagram](k8s-architecture-v2.png)

## Setting up an Environment

### Local
```
minikube start --cpus=4 --memory='4000mb'
# ONLY IF YOU NEED TO UPDATE THE IMAGES
# ./build_and_upload_images.sh
cd k8s
./full_deploy_minikube.sh
```

### GCP
Create a GKE cluster, then:

```
# ONLY IF YOU NEED TO UPDATE THE IMAGES
# ./build_and_upload_images.sh
cd k8s
./full_deploy.sh
```

## Testing

### API Server
Create a debug container with

```
kubectl run debug -it --rm --restart=Never --image alpine -- sh
```

Within the container, run

```
# apk add curl openssh-client
# ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
```

Then you can try running the example requests in `k8s/api-server/examplerequest.txt`

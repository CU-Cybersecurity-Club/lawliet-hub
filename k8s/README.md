# Kubernetes Deployment of Lawliet Hub

Hub server code and Kubernetes service, deployment, etc. files are found in `./api-server`. The other files in this directory exist to modify a necessary option of `kubelet` on the deployment platform of choice and to simplify deployment for the user.

## Editing Kubelets
`edit-kubelets.sh` and `edit-kubelets_minikube.sh` are scripts that modify `kubelet`'s options on GCP (GKE) and Minikube respectively to enable modification of the `net.ipv6.conf.all.disable_ipv6` sysctl, which is necessary as specified by the repos root directory README.

## Full Deployment
`full_deploy.sh` and `full_deploy_minikube.sh` are simply helpful wrappers over `edit-kubelets.sh` and `api-server/deploy.sh` for the respective platform.

## Development Notes and Link Dump
https://kubernetes.io/docs/tasks/administer-cluster/sysctl-cluster/#enabling-unsafe-sysctls

#!/bin/bash

SCRIPT_DIR="$(dirname $0)"

set -e

###
### Set Minikube kubelet options
###

echo "adding kubelet option on minikube for sysctl"
#minikube ssh 'sudo sed -i "/ExecStart/c\ExecStart=/var/lib/minikube/binaries/v1.16.2/kubelet --allowed-unsafe-sysctls net.ipv6.conf.all.disable_ipv6" /usr/lib/systemd/system/kubelet.service && sudo systemctl daemon-reload && sudo systemctl restart kubelet'
minikube ssh "echo 'allowedUnsafeSysctls:' | sudo tee -a /var/lib/kubelet/config.yaml"
minikube ssh "echo '- \"net.ipv6.conf.all.disable_ipv6\"' | sudo tee -a /var/lib/kubelet/config.yaml"
minikube ssh "sudo systemctl daemon-reload"
minikube ssh "sudo systemctl restart kubelet"
echo "done editing kubelet on minikube"

###
### Deploy services to Minikube
###

$(SCRIPT_DIR)/deploy.sh

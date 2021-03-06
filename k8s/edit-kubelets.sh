#!/bin/bash

set -e

for instance in $(gcloud compute instances list --filter="name~'gke.*pool'" --format="value(name)")
do
		echo "now editing: " $instance
		gcloud compute ssh $instance \
				--command='sudo sed -i "/ExecStart/c\ExecStart=/home/kubernetes/bin/kubelet --allowed-unsafe-sysctls net.ipv6.conf.all.disable_ipv6 \$KUBELET_OPTS" /etc/systemd/system/kubelet.service && sudo systemctl daemon-reload && sudo systemctl restart kubelet'
		echo "done editing: " $instance
done

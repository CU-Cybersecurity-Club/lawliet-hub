#!/bin/bash

set -e

MACHINENAME=penlite-test-8

# the commented out stuff is how you would theoretically do a docker save -> docker load
# it runs out that scp'ing all that (1.5-2+ gb) takes a while, so I opted for the build on the vm
# DOCKERSAVE=penlitetest.tar.gz
# 
# echo "running docker save"
# docker save penlite:test penlite:test-vnc | gzip > $DOCKERSAVE

echo "making gcp instance"
gcloud compute instances create $MACHINENAME \
		--boot-disk-size=40G \
		--machine-type="n1-standard-1" \
		--image-project="ubuntu-os-cloud" \
		--image-family="ubuntu-1804-lts" \
		--tags "penlite" \
		--metadata-from-file startup-script=./vm-startup.sh \
		--zone=us-west1-a

echo "copying dockerfiles and docker-server.py"
# gcloud compute scp ./$DOCKERSAVE $MACHINENAME:~/
gcloud compute scp \
		Dockerfile \
		Dockerfile.vnc \
		docker-server.py \
		start.sh \
		add-vnc-user.sh \
		start-vnc.sh \
		xstartup \
		$MACHINENAME:~/

echo "waiting for startup to finish"
gcloud compute ssh $MACHINENAME --command "sudo tail -n 1000 -f /var/log/syslog | grep -m 1 VMSTARTUPISNOWDONE"

echo "running docker build and server in screen session"
gcloud compute ssh $MACHINENAME --command "screen -d -m sudo docker build -f Dockerfile -t penlite:test ."
gcloud compute ssh $MACHINENAME --command "screen -d -m sudo docker build -f Dockerfile.vnc -t penlite:test-vnc ."
gcloud compute ssh $MACHINENAME --command "screen -d -m sudo python3 docker-server.py"

# echo "loading docker tar onto remote"
# gcloud compute ssh $MACHINENAME "docker load -i ~/$DOCKERSAVE"

# rm $DOCKERSAVE

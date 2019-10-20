#!/bin/bash

# ASSUMES UBUNTU

apt update && apt upgrade -y && apt install -y docker.io python3-pip
pip3 install Flask docker python-dateutil pytz

# ipv6 is necessary for the hackthebox vpn
# this sysctl section is necessary to enable ipv6 on the host machine
echo '' >> /etc/sysctl.conf
echo 'net.ipv6.conf.all.disable_ipv6 = 0' >> /etc/sysctl.conf
echo 'net.ipv6.conf.default.disable_ipv6 = 0' >> /etc/sysctl.conf
echo 'net.ipv6.conf.lo.disable_ipv6 = 0' >> /etc/sysctl.conf
sysctl -p

# we then must enable ipv6 in the docker daemon
echo '{ "ipv6": true, "fixed-cidr-v6": "2001:db8:1::/64" }' >> /etc/docker/daemon.json

systemctl enable docker
systemctl start docker

# echo a unique string for the wait to pick up
echo "VMSTARTUPISNOWDONE"

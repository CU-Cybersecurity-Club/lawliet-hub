#!/bin/bash

# ASSUMES UBUNTU

apt update && apt upgrade -y && apt install -y python3-pip
pip3 install Flask

gsutil cp gs://cu-cyber-lawliet/lb-server.tar.gz ./
tar -xvf lb-server.tar.gz

screen -d -m python3 lb-server.py

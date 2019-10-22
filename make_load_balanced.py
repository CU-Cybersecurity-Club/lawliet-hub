#!/usr/bin/env python3

import tarfile
import fileinput
import os
import subprocess
import time

import google.auth
import googleapiclient.discovery
from google.cloud import storage

def create_instance(compute, project, zone, name, is_docker=True, is_lb=False):
    if (is_docker and is_lb) or (not is_docker and not is_lb):
        raise ValueError("must be either docker or lb host")

    image_response = compute.images().getFromFamily(
        project='ubuntu-os-cloud', family='ubuntu-1804-lts').execute()
    source_disk_image = image_response['selfLink']

    if is_docker:
        machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
        startup_script = open(
            os.path.join(
                os.path.dirname(__file__), 'vm-startup-docker.sh'), 'r').read()
    elif is_lb:
        machine_type = "zones/%s/machineTypes/f1-micro" % zone
        startup_script = open(
            os.path.join(
                os.path.dirname(__file__), 'vm-startup-lb.sh'), 'r').read()

    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                    'diskSizeGb': 40
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        # 'serviceAccounts': [{
        #     'email': 'default',
        #     'scopes': [
        #         'https://www.googleapis.com/auth/devstorage.read_write',
        #         'https://www.googleapis.com/auth/logging.write'
        #     ]
        # }],

        'tags': { 'items': ['penlite'] },

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }
            ]
        }
    }

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()

def config_bucket_create(name):
    client = storage.Client()
    buckets = client.list_buckets()
    exists = False

    for bucket in buckets:
        if bucket.name == name:
            exists = True
            break

    if not exists:
        client.create_bucket(name)

        # TODO: this is awful
        subprocess.run(["gsutil", "defacl", "ch", "-u", "AllUsers:R", "gs://%s" % name])


def upload_docker_tar(name):
    client = storage.Client()
    bucket = client.get_bucket(name)

    # make docker-server.tar.gz for docker host
    # should contain:
    #  docker-server.py
    #  docker-server.ini (edited for the upload, eventually auto)
    #  Dockerfile
    #  Dockerfile.vnc
    #  start.sh
    #  add-vnc-user.sh
    #  start-vnc.sh
    #  xstartup
    tar = tarfile.open("docker-server.tar.gz", "w:gz")
    for name in [
            "docker-server.py",
            "docker-server.ini",
            "Dockerfile",
            "Dockerfile.vnc",
            "start.sh",
            "add-vnc-user.sh",
            "start-vnc.sh",
            "xstartup"]:
        tar.add(name)
    tar.close()
    blob = bucket.blob("docker-server.tar.gz")
    blob.upload_from_filename("docker-server.tar.gz")

def upload_lb_tar(name, docker_ips):
    client = storage.Client()
    bucket = client.get_bucket(name)

    # make lb-server.tar.gz for lb host
    # should contain:
    #  lb-server.py
    #  lb-server.ini (edited right here for the right hosts)

    for line in fileinput.input("lb-server.ini", inplace=True):
        if "DockerServers" in line:
            print("DockerServers: %s" % ",".join(map(lambda x: "%s:8080" % x, docker_ips)), end="")
        else:
            print(line, end="")

    tar = tarfile.open("lb-server.tar.gz", "w:gz")
    for name in [
            "lb-server.py",
            "lb-server.ini"]:
        tar.add(name)
    tar.close()
    blob = bucket.blob("lb-server.tar.gz")
    blob.upload_from_filename("lb-server.tar.gz")

def wait_for_ip(compute, project, zone, name):                                                                                                                                             
    while True:
        result = compute.instances().get(project=project, zone=zone, instance=name).execute()
        print(result)
        try:
            return result['networkInterfaces'][0]['accessConfigs'][0]['natIP']
        except KeyError as e:
            print("no nat ip yet, waiting")
            time.sleep(3)
            continue

if __name__ == "__main__":
    credentials, project = google.auth.default()
    service = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)
    zone = "us-west1-b"

    bucket_name = "cu-cyber-penlite"
    lb_host = "penlite-lb-0"
    docker_host_pattern = "penlite-docker-0-%s"
    docker_host_count = 1
    docker_hosts = [docker_host_pattern % i for i in range(docker_host_count)]

    config_bucket_create(bucket_name)
    upload_docker_tar(bucket_name)

    for hostname in docker_hosts:
        response = create_instance(
                service,
                project,
                zone,
                hostname,
                is_docker=True,
                is_lb=False)

    docker_host_ips = []
    for hostname in docker_hosts:
        ip = wait_for_ip(service, project, zone, hostname)
        docker_host_ips.append(ip)

    print("host ips:", docker_host_ips)

    upload_lb_tar(bucket_name, docker_host_ips)
    response = create_instance(service, project, zone, lb_host, is_docker=False, is_lb=True)

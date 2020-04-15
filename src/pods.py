from flask import Flask, request, jsonify
from kubernetes import client, config
from pprint import pprint
from typing import Optional, List

import datetime
import json
import logging
import requests
import traceback

logger = logging.getLogger("kubernetes")

# for local testing with LOCAL kubectl set up for the cluster
# config.load_kube_config()
# v1 = client.CoreV1Api()

# for the pod
config.load_incluster_config()
v1 = client.CoreV1Api()


def get_pod_name(id):
    """
    Return the internal hostname for a pod with a given id.
    """
    return f"lawliet-env-{id}"


def get_pod_spec(
    id: str, image: str, ports: List[int], ssh_key: Optional[str] = None,
):
    pod = client.V1Pod()
    pod.api_version = "v1"
    pod_name = get_pod_name(id)

    labels = {"app": "lawliet-env", "app-specific": pod_name}
    pod.metadata = client.V1ObjectMeta(name=pod_name, labels=labels)
    ports = [client.V1ContainerPort(container_port=port) for port in ports]

    container = client.V1Container(
        name=pod_name,
        image=image,
        image_pull_policy="Always",
        # command=["/bin/bash"],
        # args=["-c", "echo '%s' > ~/.ssh/authorized_keys && service ssh start; mkdir -p /dev/net && mknod /dev/net/tun c 10 200 && chmod 0666 /dev/net/tun; /start.sh" % ssh_key],
        ports=ports,
        security_context=client.V1SecurityContext(
            capabilities=client.V1Capabilities(add=["NET_ADMIN"])
        ),
    )

    context = client.V1PodSecurityContext(
        sysctls=[client.V1Sysctl(name="net.ipv6.conf.all.disable_ipv6", value="0")]
    )
    logging.debug("made context")

    pod.spec = client.V1PodSpec(containers=[container], security_context=context)
    return pod


def get_svc_spec(id):
    pod_name = get_pod_name(id)
    svc = client.V1Service()

    labels = {"app": "lawliet-env", "app-specific": pod_name}
    svc.metadata = client.V1ObjectMeta(name=pod_name, labels=labels)

    svc.spec = client.V1ServiceSpec(
        type="NodePort",
        ports=[
            {"name": "ssh", "port": 22, "targetPort": 22, "protocol": "TCP"},
            {
                "name": "tigervnc-screen-1",
                "port": 6080,
                "targetPort": 6080,
                "protocol": "TCP",
            },
        ],
        selector={"app-specific": pod_name},
    )

    return svc


def get_pod_status(id):
    """
    Retrieve the status of a pod from Kubernetes
    """

    logger.info(f"Retrieving pod status for pod {id}")
    namespace = "default"

    try:
        api_response = v1.read_namespaced_pod_status(get_pod_name(id), namespace)
        pod = api_response
        logger.debug(f"Retrieved status for pod {id}: {api_response}")

        return jsonify(
            {
                "name": pod.metadata.name,
                "created": pod.metadata.creation_timestamp,
                "deleted": pod.metadata.deletion_timestamp,
                "conditions": [
                    {
                        "message": cond.message,
                        "reason": cond.reason,
                        "status": cond.status,
                        "type": cond.type,
                    }
                    for cond in pod.status.conditions
                ],
            }
        )

    except client.rest.ApiException as ex:
        if '"reason":"NotFound"' in str(ex):
            logger.debug(f"Retrieve status for pod {id} failed: pod not found")
            return jsonify({"id": id, "status": "NotFound"}), 404

        logger.error(f"Exception when calling CoreV1Api->read: {ex}")
        return jsonify({"error": "failed to get pod status"}), 500


def create_pod(id, image: str, ports: List[int], ssh_key: Optional[str] = None):
    """
    Create a new pod using a container image.
    """

    logger.info(f"Creating new pod {id}")
    namespace = "default"

    body = get_pod_spec(id, image, ports, ssh_key=ssh_key)
    pretty = "true"

    try:
        api_response = v1.create_namespaced_pod(namespace, body, pretty=pretty)
        logger.debug(f"Response for create pod {id}: {api_response}")
        api_response = v1.create_namespaced_service(
            namespace, get_svc_spec(id), pretty=pretty
        )
        logger.debug(f"Response for create service {id}: {api_response}")

        pod_name = get_pod_name(id)
        logger.info(f"Created new pod with id {id!r} (pod name: {pod_name!r})")

        return jsonify({"id": id, "image": image, "pod_name": pod_name})

    except client.rest.ApiException as ex:
        logger.error(f"Exception when calling CoreV1Api->create: {ex}")
        logger.debug(f"\n{traceback.format_exc()}")
        return jsonify({"error": "failed to create pod"}), 500


def delete_pod(id, literal_name=False):
    logger.info(f"Deleting pod {id}")
    namespace = "default"

    if literal_name:
        pod_name = id
    else:
        pod_name = get_pod_name(id)
    pretty = "true"

    try:
        api_response = v1.delete_namespaced_pod(pod_name, namespace, pretty=pretty)
        logging.debug(f"Response for delete pod {id}: {api_response}")
        api_response = v1.delete_namespaced_service(pod_name, namespace, pretty=pretty)
        logger.debug(f"Response for delete service {id}: {api_response}")
        return jsonify({"status": "success"}), 200

    except client.rest.ApiException as ex:
        logger.error("Exception when calling CoreV1Api->delete: {ex}")
        return jsonify({"error": "Failed to delete pod"}), 500


def cleanup_pods(alive_time=datetime.timedelta(hours=12)):
    namespace = "default"

    try:
        api_response = v1.list_namespaced_pod(
            namespace, label_selector="app=lawliet-env"
        )
        pods = api_response.items
        deletion_responses = []
        for pod in pods:
            created = pod.metadata.creation_timestamp
            current = datetime.datetime.now(created.tzinfo)

            logger.debug(f"Pod: {pod.metadata.name}")
            logger.debug(f"Created: {created.isoformat('T')}")
            logger.debug(f"+alive: {(created + alive_time).isoformat('T')}")
            logger.debug(f"vs: {current.isoformat('T')}")

            if created + alive_time < datetime.datetime.now(created.tzinfo):
                deletion_responses.append(
                    delete_pod(pod.metadata.name, literal_name=True)
                )

        logger.debug(f"Cleanup deletion responses: {deletion_responses}")
        for re in deletion_responses:
            if re[1] != 200:
                return (
                    jsonify({"error": "cleanup deletion failed for at least one pod"}),
                    500,
                )
        return jsonify({"status": "success"}), 200

    except client.rest.ApiException as ex:
        logger.error(f"Exception when calling CoreV1Api->list_namespaced_pod: {ex}")
        return jsonify({"error": "failed to get pods"}), 500


def purge_pods():
    """
    Remove all pods from the system.
    """

    namespace = "default"

    try:
        api_response = v1.list_namespaced_pod(
            namespace, label_selector="app=lawliet-env"
        )
        pods = api_response.items
        deletion_responses = []
        for pod in pods:
            delete_pod(pod.metadata.name, literal_name=True)

        logger.info(f"Deleted {len(pods)} pods")
        return jsonify({"status": "success"}), 200

    except client.rest.ApiException as ex:
        logger.error(f"Exception when calling CoreV1Api->list_namespaced_pod: {ex}")
        return jsonify({"error": "failed to get pods"}), 500

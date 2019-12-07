from flask import Flask, request, jsonify
import requests
from kubernetes import client, config
from pprint import pprint
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# for local testing with LOCAL kubectl set up for the cluster
#config.load_kube_config()
#v1 = client.CoreV1Api()

# for the pod
config.load_incluster_config()
v1 = client.CoreV1Api()

def get_pod_name(name):
    return "penlite-env-%s" % name

def get_pod_spec(name, ssh_key="", container="penlite:test-vnc"):
    pod = client.V1Pod()
    pod.api_version = "v1"
    labels = {"app": "penlite-env", "app-specific": get_pod_name(name)}
    pod.metadata = client.V1ObjectMeta(name=get_pod_name(name), labels=labels)
    ports = [
            client.V1ContainerPort(container_port=22),
            client.V1ContainerPort(container_port=5900),
            client.V1ContainerPort(container_port=5901)]
    container = client.V1Container(
            name=get_pod_name(name),
            image="gcr.io/csci5253-datacenter/%s" % container,
            command=["/bin/bash"],
            args=["-c", "add-vnc-user root pass && /start.sh && echo '%s' > ~/.ssh/authorized_keys && service ssh start; /start-vnc.sh; tail -f /dev/null" % ssh_key],
            ports=ports,
            security_context=client.V1SecurityContext(capabilities=client.V1Capabilities(add=["NET_ADMIN"]))
            )
    pod.spec = client.V1PodSpec(
            containers=[container])
    return pod

def get_svc_spec(name):
    pod_name = get_pod_name(name)
    svc = client.V1Service()

    labels = {"app": "penlite-env", "app-specific": pod_name}
    svc.metadata = client.V1ObjectMeta(name=pod_name, labels=labels)

    svc.spec = client.V1ServiceSpec(
            ports=[
                {"name": "ssh", "port": 22, "targetPort": 22, "protocol": "TCP"},
                {"name": "tigervnc-base", "port": 5900, "targetPort": 5900, "protocol": "TCP"},
                {"name": "tigervnc-screen-1", "port": 5901, "targetPort": 5901, "protocol": "TCP"}
                ],
            selector={"app-specific": pod_name})

    return svc

def create_pod(name, ssh_key=""):
    logging.debug("creating:", name)
    namespace = "default"
    body = get_pod_spec(name, ssh_key=ssh_key)
    pretty = "true"
    try:
        api_response = v1.create_namespaced_pod(namespace, body, pretty=pretty)
        logging.debug("response for create pod %s: %s" % (name, api_response))
        api_response = v1.create_namespaced_service(namespace, get_svc_spec(name), pretty=pretty)
        logging.debug("response for create svc %s: %s" % (name, api_response))
        return jsonify({
            "pod_name": get_pod_name(name)
            })
    except client.rest.ApiException as e:
        logging.error("Exception when calling CoreV1Api->create_namespaced_pod: %s\n" % e)
        return "failed to create pod", 500

def delete_pod(name):
    logging.debug("deleting:", name)
    namespace = "default"
    pod_name = get_pod_name(name)
    pretty = "true"
    try:
        api_response = v1.delete_namespaced_pod(pod_name, namespace, pretty=pretty)
        logging.debug("response for delete pod %s: %s" % (name, api_response))
        api_response = v1.delete_namespaced_service(pod_name, namespace, pretty=pretty)
        logging.debug("response for delete svc %s: %s" % (name, api_response))
        return "", 200
    except client.rest.ApiException as e:
        logging.error("Exception when calling CoreV1Api->create_namespaced_pod: %s\n" % e)
        return "failed to delete pod", 500

@app.route('/container/<id>', methods=["PUT", "DELETE"])
def container(id):
    if request.method == "PUT":
        return create_pod(id, ssh_key=request.form.get("ssh_key", default=""))
    elif request.method == "DELETE":
        return delete_pod(id)

if __name__ == "__main__":
    print("starting server")
    app.run(debug=True, host="0.0.0.0", port=8081)

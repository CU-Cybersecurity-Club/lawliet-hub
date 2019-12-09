from pprint import pprint
import logging
import datetime

from flask import Flask, request, jsonify
import requests

from kubernetes import client, config


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
        logging.error("Exception when calling CoreV1Api->create: %s\n" % e)
        return "failed to create pod", 500

def delete_pod(name, literal_name=False):
    logging.debug("deleting: %s" % name)
    namespace = "default"
    if literal_name:
        pod_name = name
    else:
        pod_name = get_pod_name(name)
    pretty = "true"
    try:
        api_response = v1.delete_namespaced_pod(pod_name, namespace, pretty=pretty)
        logging.debug("response for delete pod %s: %s" % (name, api_response))
        api_response = v1.delete_namespaced_service(pod_name, namespace, pretty=pretty)
        logging.debug("response for delete svc %s: %s" % (name, api_response))
        return "", 200
    except client.rest.ApiException as e:
        logging.error("Exception when calling CoreV1Api->delete: %s\n" % e)
        return "failed to delete pod", 500

def cleanup_pods(alive_time=datetime.timedelta(hours=12)):
    namespace = "default"

    try:
        api_response = v1.list_namespaced_pod(namespace, label_selector="app=penlite-env")
        pods = api_response.items
        deletion_responses = []
        for pod in pods:
            created = pod.metadata.creation_timestamp
            logging.debug("pod: %s" % pod.metadata.name)
            logging.debug("created: %s" % pod.metadata.creation_timestamp.isoformat("T"))
            logging.debug("+alive: %s" % (pod.metadata.creation_timestamp + alive_time).isoformat("T"))
            logging.debug("vs: %s" % datetime.datetime.now(created.tzinfo).isoformat("T"))
            if created + alive_time < datetime.datetime.now(created.tzinfo):
                deletion_responses.append(delete_pod(pod.metadata.name, literal_name=True))

        logging.debug("cleanup deletion responses: %s" % deletion_responses)
        for re in deletion_responses:
            if re[1] != 200:
                return "cleanup deletion failed for at least one pod", 500
        return "", 200
    except client.rest.ApiException as e:
        logging.error("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)
        return "failed to get pods", 500

@app.route('/container/<id>', methods=["PUT", "DELETE"])
def container(id):
    if request.method == "PUT":
        return create_pod(id, ssh_key=request.form.get("ssh_key", default=""))
    elif request.method == "DELETE":
        return delete_pod(id)

@app.route('/container/cleanup', methods=["POST"])
def container_cleanup():
    if request.method == "POST":
        minutes_alive = request.form.get("minutes_alive", default="720")
        time_alive = datetime.timedelta(minutes=int(minutes_alive))
        return cleanup_pods(alive_time=time_alive)

if __name__ == "__main__":
    print("starting server")
    app.run(debug=True, host="0.0.0.0", port=8081)

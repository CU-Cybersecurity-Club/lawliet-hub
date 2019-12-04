from flask import Flask, request, jsonify
import requests
from kubernetes import client, config
from pprint import pprint

app = Flask(__name__)
config.load_kube_config()
v1 = client.CoreV1Api()

def get_pod_name(name):
    return "penlite-%s" % name

def get_pod_spec(name, container="penlite:test-vnc"):
    pod = client.V1Pod()
    pod.api_version = "v1"
    labels = {"app": "penlite", "app-specific": get_pod_name(name)}
    pod.metadata = client.V1ObjectMeta(name=get_pod_name(name), labels=labels)
    ports = [
            client.V1ContainerPort(container_port=22),
            client.V1ContainerPort(container_port=5900),
            client.V1ContainerPort(container_port=5901)]
    container = client.V1Container(
            name=get_pod_name(name),
            image="gcr.io/csci5253-datacenter/%s" % container,
            command=["/bin/bash"],
            args=["-c", "add-vnc-user root pass && /start.sh && echo 'test' > ~/.ssh/authorized_keys && service ssh start; /start-vnc.sh; tail -f /dev/null"],
            ports=ports,
            security_context=client.V1SecurityContext(capabilities=client.V1Capabilities(add=["NET_ADMIN"]))
            )
    pod.spec = client.V1PodSpec(containers=[container])
    return pod

def create_pod(name):
    namespace = "default"
    body = get_pod_spec(name)
    pretty = "true"
    try:
        api_response = v1.create_namespaced_pod(namespace, body, pretty=pretty)
        pprint(api_response)
        return jsonify({
            "pod_name": get_pod_name(name)
            })
    except client.rest.ApiException as e:
        print("Exception when calling CoreV1Api->create_namespaced_pod: %s\n" % e)
        return "failed to create pod", 500

def delete_pod(name):
    namespace = "default"
    pod_name = get_pod_name(name)
    pretty = "true"
    try:
        api_response = v1.delete_namespaced_pod(pod_name, namespace, pretty=pretty)
        pprint(api_response)
        return "", 200
    except client.rest.ApiException as e:
        print("Exception when calling CoreV1Api->create_namespaced_pod: %s\n" % e)
        return 500

@app.route('/container/<id>', methods=["PUT", "DELETE"])
def container(id):
    if request.method == "PUT":
        return create_pod(id)
    elif request.method == "DELETE":
        return delete_pod(id)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8081)

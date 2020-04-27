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
    return "lawliet-env-%s" % name

def get_pod_spec(name, ssh_key="", container="wshand/cutter:latest"):
    pod = client.V1Pod()
    pod.api_version = "v1"
    labels = {"app": "lawliet-env", "app-specific": get_pod_name(name)}
    pod.metadata = client.V1ObjectMeta(name=get_pod_name(name), labels=labels)
    ports = [
            client.V1ContainerPort(container_port=22),
            client.V1ContainerPort(container_port=6080)]
    container = client.V1Container(
            name=get_pod_name(name),
            image=container,
            image_pull_policy="Always",
            #command=["/bin/bash"],
            #args=["-c", "echo '%s' > ~/.ssh/authorized_keys && service ssh start; mkdir -p /dev/net && mknod /dev/net/tun c 10 200 && chmod 0666 /dev/net/tun; /start.sh" % ssh_key],
            ports=ports,
            security_context=client.V1SecurityContext(
                capabilities=client.V1Capabilities(add=["NET_ADMIN"]))
            )

    context = client.V1PodSecurityContext(sysctls=[
        client.V1Sysctl(name="net.ipv6.conf.all.disable_ipv6", value="0")])
    logging.debug("made context")

    pod.spec = client.V1PodSpec(
            containers=[container],
            security_context=context)
    return pod

def get_svc_spec(name):
    pod_name = get_pod_name(name)
    svc = client.V1Service()

    labels = {"app": "lawliet-env", "app-specific": pod_name}
    svc.metadata = client.V1ObjectMeta(name=pod_name, labels=labels)

    svc.spec = client.V1ServiceSpec(
            type="NodePort",
            ports=[
                {"name": "ssh", "port": 22, "targetPort": 22, "protocol": "TCP"},
                {"name": "tigervnc-screen-1", "port": 6080, "targetPort": 6080, "protocol": "TCP"}
                ],
            selector={"app-specific": pod_name})

    return svc

def construct_status_response(api_response):
    pod = api_response

    if pod.metadata is None:
        return jsonify({
            "name": name,
            "status": "metadata is None, try again"
            }), 500
    elif pod.status is None:
        return jsonify({
            "name": name,
            "status": "status is None, try again"
            }), 500
    elif pod.status.conditions is None:
        return jsonify({
            "name": name,
            "status": "status.conditions is None, try again"
            }), 500

    return jsonify({
        "name": pod.metadata.name,
        "created": pod.metadata.creation_timestamp,
        "deleted": pod.metadata.deletion_timestamp,
        "conditions": [{"message": x.message, "reason": x.reason, "status": x.status, "type": x.type} for x in pod.status.conditions]
        })


def get_pod_status(name):
    logging.debug("get pod status called for: %s" % name)
    namespace = "default"

    try:
        api_response = v1.read_namespaced_pod_status(get_pod_name(name), namespace)
        logging.info("response for get pod status: %s" % api_response)
        return construct_status_response(api_response)
    except client.rest.ApiException as e:
        if '"reason":"NotFound"' in str(e):
            return jsonify({
                "name": name,
                "status": "NotFound"
                }), 404

        logging.error("Exception when calling CoreV1Api->read: %s\n" % e)
        return jsonify({"error": "failed to get pod status"}), 500

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
        return jsonify({"error": "failed to create pod"}), 500

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
        return jsonify({"status": "success"}), 200
    except client.rest.ApiException as e:
        logging.error("Exception when calling CoreV1Api->delete: %s\n" % e)
        return jsonify({"error": "failed to delete pod"}), 500

def cleanup_pods(alive_time=datetime.timedelta(hours=12)):
    namespace = "default"

    try:
        api_response = v1.list_namespaced_pod(namespace, label_selector="app=lawliet-env")
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
                return jsonify({"error": "cleanup deletion failed for at least one pod"}), 500
        return jsonify({"status": "success"}), 200
    except client.rest.ApiException as e:
        logging.error("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)
        return jsonify({"error": "failed to get pods"}), 500


@app.route('/container/<id>', methods=["PUT", "DELETE", "GET"])
def container(id):
    if request.method == "PUT":
        return create_pod(id, ssh_key=request.form.get("ssh_key", default=""))
    elif request.method == "DELETE":
        return delete_pod(id)
    elif request.method == "GET":
        return get_pod_status(id)

@app.route('/container/cleanup', methods=["POST"])
def container_cleanup():
    if request.method == "POST":
        minutes_alive = request.form.get("minutes_alive", default="720")
        time_alive = datetime.timedelta(minutes=int(minutes_alive))
        return cleanup_pods(alive_time=time_alive)

if __name__ == "__main__":
    print("starting server")
    app.run(debug=True, host="0.0.0.0", port=8081)

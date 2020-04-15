"""
API endpoints related to accessing Kubernetes for creating pods, deleting pods,
get pod status, etc.
"""

from pods import create_pod, delete_pod, get_pod_status, cleanup_pods
from flask import Blueprint, jsonify

"""
Flask Blueprint within which to register all of the views
"""

kube_views = Blueprint("kube", __name__, url_prefix="/container")

"""
View definitions
"""


@kube_views.route("/<id>", methods=["PUT", "DELETE", "GET"])
def container(id):
    if request.method == "PUT":
        return create_pod(id, ssh_key=request.form.get("ssh_key", default=""))
    elif request.method == "DELETE":
        return delete_pod(id)
    elif request.method == "GET":
        return get_pod_status(id)


@kube_views.route("/cleanup", methods=["POST"])
def container_cleanup():
    if request.method == "POST":
        minutes_alive = request.form.get("minutes_alive", default="720")
        time_alive = datetime.timedelta(minutes=int(minutes_alive))
        return cleanup_pods(alive_time=time_alive)

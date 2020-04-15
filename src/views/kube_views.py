"""
API endpoints related to accessing Kubernetes for creating pods, deleting pods,
get pod status, etc.
"""

import datetime
import logging
import pods
from flask import Blueprint, jsonify, request
from flask.views import MethodView

logger = logging.getLogger("kubernetes")

"""
View definitions
"""


class PodManipulationAPI(MethodView):
    """
    Defines an endpoint that takes a pod id and can create, delete,
    or get the status of a pod with that id.
    """

    def get(self, id):
        """
        Retrieve a pod's status
        """
        return pods.get_pod_status(id)

    def put(self, id):
        """
        Create a new pod
        """
        data = request.get_json()
        err = None

        if not data:
            err = "Data should be JSON-formatted"

        image = data.get("image", None)
        ports = data.get("ports", None)
        if not image or not ports:
            err = "Data should be a JSON object with the keys 'image' " "and 'ports'"

        if err is not None:
            return jsonify({"err": err}), 422

        return pods.create_pod(id, image, ports, ssh_key=request.form.get("ssh_key"))

    def delete(self, id):
        """
        Delete an existing pod
        """
        return pods.delete_pod(id)


def container_cleanup():
    minutes_alive = request.form.get("minutes_alive", default="720")
    time_alive = datetime.timedelta(minutes=int(minutes_alive))
    return pods.cleanup_pods(alive_time=time_alive)


def purge_pods():
    """
    An endpoint that can be used to purge all running lab environment pods.
    """
    return pods.purge_pods()


"""
Flask Blueprint to bundle all of the views together
"""

kube_views = Blueprint("kube", __name__, url_prefix="/")

kube_views.add_url_rule(
    "/pods/<id>",
    endpoint="pod manipulation",
    view_func=PodManipulationAPI.as_view("pod manipulation"),
)
kube_views.add_url_rule(
    "/cleanup", endpoint="cleanup", view_func=container_cleanup, methods=["POST"]
)
kube_views.add_url_rule(
    "/purge", endpoint="purge", view_func=purge_pods, methods=["POST"]
)

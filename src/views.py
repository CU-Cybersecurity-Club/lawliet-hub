"""
Define all of the endpoints for the API
"""

import datetime
from pods import create_pod, delete_pod, get_pod_status, cleanup_pods


def container(id):
    if request.method == "PUT":
        return create_pod(id, ssh_key=request.form.get("ssh_key", default=""))
    elif request.method == "DELETE":
        return delete_pod(id)
    elif request.method == "GET":
        return get_pod_status(id)


def container_cleanup():
    if request.method == "POST":
        minutes_alive = request.form.get("minutes_alive", default="720")
        time_alive = datetime.timedelta(minutes=int(minutes_alive))
        return cleanup_pods(alive_time=time_alive)


def add_routes(app):
    """
    Add all of the endpoints for the API to a Flask app.
    """

    app.add_url_rule(
        "/container/<id>", "container", container, methods=["PUT", "DELETE", "GET"]
    )
    app.add_url_rule(
        "/container/cleanup", "cleanup", container_cleanup, methods=["POST"]
    )

    return app

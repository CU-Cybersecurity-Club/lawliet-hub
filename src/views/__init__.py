from .kube_views import kube_views
from .server_status import index


def add_routes(app):
    """
    Add all of the endpoints for the API to a Flask app.
    """

    app.add_url_rule("/", "index", index, methods=["GET"])
    app.register_blueprint(kube_views)

    return app

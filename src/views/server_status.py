"""
Views related to getting the status of the server itself.
"""

import datetime
import settings
from flask import jsonify


def index():
    """
    Endpoint corresponding to /. This endpoint primarily serves as a method for
    getting a heartbeat from the server and for getting a summary of the
    server's status.
    """

    # TODO: add more/better information
    response = {
        "msg": "Lawliet Hub",
        "version": settings.VERSION,
        "status": "alive",
        "time": str(datetime.datetime.now()),
    }

    return jsonify(response)

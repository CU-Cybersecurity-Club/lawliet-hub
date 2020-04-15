"""
Launch script for running the Flask server for the REST service.
"""

import settings

from views import add_routes
from flask import Flask

"""
Helper functions
"""


def create_app(name):
    """
    Construct a new Flask app to run the API server.
    """
    app = Flask(name)
    app.config["DEBUG"] = settings.DEBUG
    app.config["ENV"] = settings.FLASK_ENV
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app = add_routes(app)

    app.logger.info("Created Flask app")

    return app


"""
Main script
"""

if __name__ == "__main__":
    app = create_app("lawliet-hub")
    app.run(debug=True, host="0.0.0.0", port=8081)

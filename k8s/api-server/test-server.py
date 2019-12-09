from flask import Flask, request, jsonify
import requests
from kubernetes import client, config
from pprint import pprint
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/container/<id>', methods=["PUT", "DELETE"])
def container(id):
    if request.method == "PUT":
        ssh_key = request.args.get("ssh_key", default="")
        print("form:", request.form)
        print("json:", request.json)
        print("ssh_key:", ssh_key)

        return "", 200

if __name__ == "__main__":
    print("starting server")
    app.run(debug=True, host="0.0.0.0", port=8081)

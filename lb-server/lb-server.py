from flask import Flask, request, jsonify
import requests

from random import shuffle
import configparser

app = Flask(__name__)

servers = ["localhost:8080"]

@app.route('/container', methods=["POST"])
def create_container():
    pubkey = request.json['ssh_public_key']
    vnc = bool(request.json['is_vnc'])

    shuffle(servers)
    for server in servers:
        response = requests.post(
                "http://%s/container" % server,
                json={
                    "ssh_public_key": pubkey,
                    "is_vnc": vnc
                    },
                headers={"Content-Type": "application/json"})

        if response.status_code != 200:
            print("asked %s for a container, got code %s and content: %s" % (server, response.status_code, response.content))
            continue
        else:
            json_response = response.json()
            return jsonify({
                "server": server,
                "ssh_port": json_response["ssh_port"],
                "vnc_base_port": json_response["vnc_base_port"]
                })

    return "no space on backing servers", 503

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("lb-server.ini")
    servers = config["DEFAULT"]["DockerServers"].split(",")
    print("servers is:", servers)

    app.run(debug=True, host="0.0.0.0", port=8081)

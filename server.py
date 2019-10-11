from flask import Flask, request, jsonify
import docker
import sqlite3

# eventually move the active containers to a db in case of failure
possible_ports = set(range(10000, 20000))
active_containers = dict() # container id -> port

app = Flask(__name__)
client = docker.from_env()

def pick_port(possible, in_use):
    return list(possible - in_use)[0]

@app.route('/container', methods=["POST"])
def create_container():
    if request.method != "POST":
        return "nope"

    global available_ports
    global active_containers

    print(request.json)
    pubkey = request.json['ssh_public_key']

    port = pick_port(possible_ports, set(active_containers.values()))

    container = client.containers.run(
            'penlite:test',
            """/bin/sh -c 'echo "%s" > ~/.ssh/authorized_keys; service ssh start; /bin/bash'""" % pubkey,
            ports={'22/tcp': port},
            tty=True, # I don't know if this is necessary
            remove=True,
            detach=True
            )

    active_containers[container.id] = port

    return jsonify({
        "port": port
        })

if __name__ == "__main__":
    app.run(debug=True, port=8080)

from flask import Flask, request, jsonify
import docker
import sqlite3
import datetime
from dateutil import parser # sub for datetime.strptime for efficiency later
import pytz

app = Flask(__name__)
client = docker.from_env()

conn = sqlite3.connect("penlite.db")

last_cleanup = None

# datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
def kill_old_containers(before_datetime):
    freed_ports = []

    running = client.containers.list()
    print(running)
    print("before: ", before_datetime)
    for container in running:
        if 'penlite' not in container.attrs['Config']['Labels']:
            continue

        created = parser.parse(container.attrs['Created'])
        print("created: ", created)
        if created < before_datetime:
            print("killing container:", container.id)
            container.kill()

            freed_ports.append(container.attrs['HostConfig']['PortBindings']['22/tcp'][0]['HostPort'])

    print("freed:", freed_ports)
    conn = sqlite3.connect("penlite.db")
    cursor = conn.cursor()
    for port in freed_ports:
        cursor.execute('''DELETE FROM used_ports WHERE port = ?''', (port,))
    conn.commit()
    return

def init_db(conn):
    curs = conn.cursor()
    curs.execute('''CREATE TABLE IF NOT EXISTS used_ports (port integer)''')
    conn.commit()
    return

def pick_port(possible, in_use):
    return list(possible - in_use)[0]

def pick_port_db(conn, minport=10000, maxport=20000):
    curs = conn.cursor()
    rows = curs.execute('''SELECT port FROM used_ports''')
    rows = list(map(lambda x: int(x[0]), rows))
    print("rows: %s" % rows)

    for port in range(minport, maxport + 1):
        if port not in rows:
            curs.execute('''INSERT INTO used_ports VALUES (?)''', (port,))
            conn.commit()
            return port

@app.route('/container', methods=["POST"])
def create_container():
    if request.method != "POST":
        return "nope"

    conn = sqlite3.connect("penlite.db")
    curs = conn.cursor()

    pubkey = request.json['ssh_public_key']

    port = pick_port_db(conn)

    container = client.containers.run(
            'penlite:test',
            """/bin/sh -c '/start.sh && echo "%s" > ~/.ssh/authorized_keys && service ssh start; /bin/bash'""" % pubkey,
            ports={'22/tcp': port},
            labels=['penlite'],
            tty=True, # I don't know if this is necessary
            remove=True,
            detach=True
            )

    return jsonify({
        "port": port
        })

if __name__ == "__main__":
    init_db(conn)
    print("inited db")
    app.run(debug=True, port=8080)

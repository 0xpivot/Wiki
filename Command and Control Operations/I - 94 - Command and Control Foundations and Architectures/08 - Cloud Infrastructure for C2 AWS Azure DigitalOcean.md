---
tags: [c2, red-team, infrastructure, vapt]
difficulty: intermediate
module: "94 - Command and Control Foundations and Architectures"
topic: "94.08 Cloud Infrastructure for C2 AWS Azure DigitalOcean"
---

# Cloud Infrastructure for C2: AWS, Azure, DigitalOcean

## Introduction to Cloud-Based C2

Modern Red Team operations demand agile, resilient, and stealthy infrastructure. Relying on static, on-premises virtual private servers (VPS) with poor IP reputation is a surefire way to get caught by rudimentary threat intelligence feeds. To counter this, elite Red Teams leverage the power of public cloud providers—such as Amazon Web Services (AWS), Microsoft Azure, and DigitalOcean—to host, proxy, and conceal Command and Control (C2) traffic.

Deploying C2 infrastructure in the cloud offers massive operational advantages:
1. **Implicit Trust (IP Reputation)**: Traffic destined for AWS or Azure IPs is often whitelisted or minimally inspected by corporate firewalls, as blocking these ranges would break legitimate business services.
2. **Elasticity and Ephemerality**: Using Infrastructure as Code (IaC), Red Teams can deploy, destroy, and redeploy complete redirector networks in minutes, making IP-based blocklists obsolete.
3. **Serverless Architectures**: Leveraging API gateways and serverless functions to process C2 traffic eliminates traditional host-based artifacts and complicates blue team attribution.

## Core Cloud Providers & Their Use Cases

### DigitalOcean (The Burnable Frontend)
DigitalOcean is heavily favored for spinning up cheap, disposable Droplets (VPS) used as Tier 1 dumb or smart redirectors. Because of their low cost and API integration, they are easily automated. 
- **Use Case**: Nginx reverse proxies, socat forwarders.
- **OpSec Note**: DO IPs are frequently associated with scanning and malicious activity, so they must be shielded by domains with strong reputation or used in conjunction with CDNs.

### Amazon Web Services (AWS)
AWS is the gold standard for blending in. By using AWS API Gateway, Red Teams can create serverless endpoints that execute Lambda functions or proxy traffic back to a hidden Team Server.
- **Use Case**: Serverless redirectors, highly trusted IP ranges.
- **Feature**: AWS CloudFront can be utilized for domain fronting or CDN proxying. AWS VPC Peering allows private, unroutable communication between multiple tiers of redirectors.

### Microsoft Azure
Azure provides the ultimate camouflage for targeting enterprise networks, particularly those deeply integrated into the Microsoft ecosystem (O365, Active Directory). Traffic flowing to `*.azureedge.net` or Azure App Services is rarely blocked outright.
- **Use Case**: Enterprise evasion, Azure Functions as smart redirectors, Azure CDN abuse.

## Architecture: The Serverless C2 Matrix

Instead of traditional VMs passing traffic, modern cloud C2 relies on serverless components. Below is a conceptual architecture using AWS API Gateway as the frontline proxy.

```text
                                +-------------------+
                                |                   |
                                |  Target Network   |
                                |   (C2 Implant)    |
                                |                   |
                                +---------+---------+
                                          |
                                          | HTTPS Request
                                          | Host: 123abcxyz.execute-api.us-east-1.amazonaws.com
                                          v
+---------------------------------------------------------------------------------+
|                              Amazon Web Services (AWS)                          |
|                                                                                 |
|   +--------------------------+          +-----------------------------------+   |
|   |                          |          |                                   |   |
|   |     AWS API Gateway      |   GET    |        AWS Lambda Function        |   |
|   |   (High Reputation IP)   |=========>|   (Parses headers, formats data,  |   |
|   |  [Serverless Endpoint]   |          |    makes internal HTTP request)   |   |
|   |                          |          |                                   |   |
|   +--------------------------+          +-----------------+-----------------+   |
|                                                           |                     |
+-----------------------------------------------------------|---------------------+
                                                            |
                                                            | HTTPS
                                                            |
                                  +-------------------------v-------------------------+
                                  |                                                   |
                                  |  Hidden Team Server (DigitalOcean / Custom VPS)   |
                                  |     (Listens only to AWS Lambda IP ranges)        |
                                  |                                                   |
                                  +---------------------------------------------------+
```

## Infrastructure as Code (IaC) with Terraform

Managing multi-cloud infrastructure manually is error-prone. Red Teams use tools like **Terraform** or **Ansible** to automate deployment. Terraform allows operators to define their entire network, firewalls (Security Groups), redirectors, and DNS records in declarative code.

### Example: Deploying a DO Redirector with Terraform

```hcl
# Define the provider
terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

# Create a Droplet for Nginx Redirector
resource "digitalocean_droplet" "tier1_redirector" {
  image  = "ubuntu-22-04-x64"
  name   = "cdn-edge-node-01"
  region = "nyc3"
  size   = "s-1vcpu-1gb"
  
  ssh_keys = [data.digitalocean_ssh_key.redteam.id]
}

# Configure Firewall to only allow HTTPS from anywhere, and SSH from Team IP
resource "digitalocean_firewall" "redirector_fw" {
  name = "redirector-rules"

  droplet_ids = [digitalocean_droplet.tier1_redirector.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["203.0.113.50/32"] # Red Team VPN IP
  }
}
```
Using the `terraform apply` command, the entire redirector is provisioned in under 60 seconds. If burned, `terraform destroy` wipes the evidence cleanly.

## Real-World Attack Scenario

### MuddyWater and Cloud Infrastructure Abuse
The Iranian threat actor MuddyWater frequently utilizes legitimate cloud services to blend in with normal traffic. In several campaigns, they leveraged AWS API Gateway as a primary mechanism to hide their C2.

**Execution Flow**:
1. The adversary configured an AWS API Gateway endpoint linked to a Lambda function. The Gateway was assigned a generic AWS subdomain (`execute-api.eu-central-1.amazonaws.com`).
2. An implant was executed on the victim network and initiated outbound HTTPS beacons to the AWS endpoint.
3. The enterprise firewall inspected the SNI and IP destination. Seeing that it belonged to Amazon AWS (a critical business dependency for the target), the traffic was permitted.
4. The AWS Lambda function received the GET/POST requests, stripped away unneeded headers, and proxied the raw C2 payloads to a hidden backend server hosted in a non-extradition jurisdiction.
5. When the Blue Team finally identified the anomaly via endpoint behavioral analytics, they attempted to IP-block the destination, only to realize they would be blocking a vast swath of AWS infrastructure, forcing them to rely on complex L7 inspection instead.

## Chaining Opportunities

Cloud Infrastructure amplifies the effectiveness of all other C2 operations:
- **Redirector Integration**: Deploying Nginx or Socat directly onto EC2 or Azure VMs. (See [[07 - Redirectors Socat Iptables Nginx]])
- **CDN Synergy**: Placing Cloudflare or Fastly in front of AWS infrastructure to double-layer the obfuscation. (See [[06 - Domain Fronting and CDN Abuse]])

## Related Notes
- [[06 - Domain Fronting and CDN Abuse]]
- [[07 - Redirectors Socat Iptables Nginx]]
- [[09 - C2 Obfuscation and Jitter]]
- [[10 - C2 Network Signatures and TLS Fingerprinting]]

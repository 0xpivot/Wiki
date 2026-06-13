---
tags: [cloud, basics, enumeration, vapt]
difficulty: beginner
module: "75 - Cloud Enumeration and Reconnaissance"
topic: "75.01 OSINT for Cloud Assets Domain to Cloud IP"
---

# OSINT for Cloud Assets: Domain to Cloud IP

## 1. Introduction to Cloud OSINT

The shift to cloud computing has completely transformed external attack surface management. When organizations migrate to cloud service providers (CSPs) like AWS, Azure, or GCP, their assets are no longer confined to predictable, static IP ranges. Instead, they dynamically utilize IP addresses from massive pools owned by the CSPs. 

This dynamic nature introduces unique challenges for penetration testers. Mapping a target's domain name to a specific cloud provider's IP address—and understanding the implications of that mapping—is the crucial first step in any cloud enumeration phase.

### Why Domain to IP Mapping is Critical
- **Identifying the Attack Surface**: A single IP might represent an Application Load Balancer (ALB), an API Gateway, a CDN edge node, or an ephemeral EC2 instance.
- **Provider-Specific Tactics**: Different cloud providers have different metadata endpoints and misconfigurations.
- **Finding Orphaned Resources**: Ephemeral IP addresses lead to Subdomain Takeover vulnerabilities if DNS records are not properly managed.

## 2. Architecture and Attack Flow

```text
+---------------------+        +-------------------------+        +---------------------------+
|   Attacker / VAPT   |        |   DNS Resolution &      |        |   Cloud Infrastructure    |
|   Professional      |        |   Recon Tools           |        |   (Target Organization)   |
+---------------------+        +-------------------------+        +---------------------------+
           |                               |                                |
           | 1. Query target domains       |                                |
           |------------------------------>|                                |
           |                               |                                |
           | 2. Extract A/CNAME records    |                                |
           |<------------------------------|                                |
           |                               |                                |
           | 3. Cross-reference IPs with   |                                |
           |    CSP IP Ranges (JSON)       |                                |
           |------------------------------>|                                |
           |                               |                                |
           | 4. Identify Provider (AWS)    |                                |
           |<------------------------------|                                |
           |                               |                                |
           | 5. Analyze Cloud Service Type |                                |
           |--------------------------------------------------------------->|
           |                               |                                |
           | 6. Pivot/Exploit              |                                |
           |<---------------------------------------------------------------|
```

## 3. The "How": Detailed Methodology

### Step 1: Subdomain Enumeration
Before mapping domains to IPs, you need a comprehensive list of domains and subdomains.
Passive Sources:
- Certificate Transparency logs (`crt.sh`)
- VirusTotal
- Shodan
- Censys
- SecurityTrails

Active Sources:
- `Amass`
- `Sublist3r`
- `ffuf`
- `dnsx`

### Step 2: DNS Resolution
Resolve subdomains to their respective IP addresses and CNAME records using `dnsx` or `massdns`. CNAME records explicitly point to cloud services.

```bash
$ dnsx -l subdomains.txt -resp -a -cname -o resolved.txt
```

### Step 3: IP to ASN / Provider Mapping
Determine which CSP owns the IPs. Cloud providers publish their IP ranges publicly.

#### AWS IP Ranges
AWS publishes its IP ranges at `https://ip-ranges.amazonaws.com/ip-ranges.json`.
Example snippet:
```json
{
  "syncToken": "1628190000",
  "createDate": "2021-08-05-18-50-24",
  "prefixes": [
    {
      "ip_prefix": "3.5.140.0/22",
      "region": "ap-northeast-2",
      "service": "AMAZON",
      "network_border_group": "ap-northeast-2"
    },
    {
      "ip_prefix": "15.230.56.0/21",
      "region": "us-east-1",
      "service": "EC2",
      "network_border_group": "us-east-1"
    }
  ]
}
```

#### Azure IP Ranges
Azure publishes `ServiceTags_Public.json` weekly.
Example snippet:
```json
{
  "name": "AzureCloud.eastus",
  "id": "AzureCloud.eastus",
  "properties": {
    "changeNumber": 123,
    "region": "eastus",
    "platform": "Azure",
    "systemService": "",
    "addressPrefixes": [
      "13.68.0.0/17",
      "13.104.116.0/22"
    ]
  }
}
```

#### GCP IP Ranges
GCP publishes at `https://www.gstatic.com/ipranges/cloud.json`.
Example snippet:
```json
{
  "syncToken": "1628190000",
  "creationTime": "2021-08-05T18:50:24",
  "prefixes": [
    {
      "ipv4Prefix": "34.80.0.0/15",
      "service": "Google Cloud",
      "scope": "asia-east1"
    }
  ]
}
```

## 4. Deep Dive: Analyzing CNAMEs for Cloud Services

CNAME records are the holy grail of cloud reconnaissance.

### AWS Examples:
- `*.elasticbeanstalk.com` -> AWS Elastic Beanstalk
- `*.s3.amazonaws.com` -> Amazon S3
- `*.cloudfront.net` -> Amazon CloudFront
- `*.elb.amazonaws.com` -> AWS Elastic Load Balancer

### Azure Examples:
- `*.azurewebsites.net` -> Azure App Service
- `*.blob.core.windows.net` -> Azure Blob Storage
- `*.cloudapp.net` -> Azure Virtual Machines
- `*.trafficmanager.net` -> Azure Traffic Manager

### GCP Examples:
- `c.storage.googleapis.com` -> Google Cloud Storage
- `ghs.googlehosted.com` -> Google App Engine

## 5. Tools of the Trade

### `ipinfo.io`
The simplest method to identify an IP owner.
```bash
$ curl ipinfo.io/54.210.10.1
{
  "ip": "54.210.10.1",
  "hostname": "ec2-54-210-10-1.compute-1.amazonaws.com",
  "city": "Ashburn",
  "region": "Virginia",
  "country": "US",
  "loc": "39.0437,-77.4875",
  "org": "AS14618 Amazon.com, Inc.",
  "postal": "20147",
  "timezone": "America/New_York"
}
```

### `cloud_enum`
A multi-cloud OSINT tool that helps identify public resources.
```bash
$ python3 cloud_enum.py -k keyword
```

### Nuclei
Nuclei has specific templates for identifying cloud provider exposures and subdomain takeovers.
Example Subdomain Takeover Template Snippet:
```yaml
id: aws-bucket-takeover
info:
  name: AWS S3 Bucket Takeover
  author: pdteam
  severity: high
requests:
  - method: GET
    path:
      - "{{BaseURL}}"
    matchers-condition: and
    matchers:
      - type: word
        words:
          - "NoSuchBucket"
          - "The specified bucket does not exist"
      - type: status
        status:
          - 404
```

## 6. Subdomain Takeover in the Cloud

One of the most critical vulnerabilities discovered during the Domain to Cloud IP phase is the subdomain takeover.

### Mechanism of Action:
1. **Creation**: Admin creates an S3 bucket named `assets.example.com`.
2. **DNS Linkage**: Admin creates a CNAME record: `assets.example.com CNAME assets.example.com.s3.amazonaws.com`.
3. **Deletion**: Admin deletes the S3 bucket.
4. **The Flaw**: Admin forgets to delete the CNAME record in DNS.
5. **Exploitation**: Attacker discovers the dangling CNAME, creates an S3 bucket named `assets.example.com`, and controls the content.

## 7. Mitigation and Defense

### Continuous Attack Surface Management (CASM)
Organizations must employ automated tools to continuously monitor their external DNS records.

### Infrastructure as Code (IaC)
By managing infrastructure using Terraform or CloudFormation, organizations can ensure that when a cloud resource is destroyed, associated DNS records are also cleanly destroyed.

### Claiming Namespaces
Use mechanisms to protect against takeovers, such as Azure verification IDs for custom domains.

## 8. Chaining Opportunities
- **[[02 - Discovering Exposed Cloud Storage S3 Scanner]]**: Scanning mapped S3 buckets for misconfigurations.
- **Subdomain Takeovers**: Directly exploiting dangling DNS records.
- **SSRF**: Using known cloud IPs to craft specific SSRF payloads.

## 9. Related Notes
- [[02 - Discovering Exposed Cloud Storage S3 Scanner]]
- [[03 - Using AWS CLI for Reconnaissance]]
- [[04 - Using Azure CLI and AzureHound for Recon]]
- [[05 - Using GCP CLI gcloud for Reconnaissance]]

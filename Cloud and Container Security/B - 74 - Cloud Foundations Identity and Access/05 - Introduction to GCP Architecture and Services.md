---
tags: [cloud, basics, foundations, vapt]
difficulty: beginner
module: "74 - Cloud Foundations Identity and Access"
topic: "74.05 Introduction to GCP Architecture and Services"
---

# 74.05 Introduction to GCP Architecture and Services

## 1. Executive Summary
Google Cloud Platform (GCP) is the third major player in the public cloud ecosystem. Known for its strong focus on data analytics, machine learning, and its origin as the birthplace of Kubernetes, GCP operates with architectural concepts that differ significantly from AWS and Azure. For a VAPT professional, GCP presents a unique environment where the global network backbone, deep integration of Google Workspace identities, and the specific nuances of Cloud IAM mandate specialized methodologies. This document details the infrastructure, core services, and offensive security vectors specific to the Google Cloud Platform.

## 2. GCP Global Infrastructure and Network Backbone
One of GCP's most significant differentiators is its highly advanced global network. Unlike AWS and Azure, where traffic between regions often traverses the public internet or requires complex transit setups, GCP utilizes its massive, privately-owned global fiber network.

### 2.1 Regions and Zones
- **Regions:** Independent geographic areas that consist of zones (e.g., `us-central1`, `europe-west4`).
- **Zones:** Deployment areas for GCP resources within a region (e.g., `us-central1-a`). Zones are considered single failure domains within a region, similar to Availability Zones in AWS.

### 2.2 Global vs. Regional Resources
GCP classifies resources based on their geographic scope:
- **Global Resources:** Accessible from any region. Examples include global load balancers, VPC networks (which span all regions automatically), and specific Cloud IAM configurations.
- **Regional Resources:** Bound to a specific region but accessible across zones. Examples include subnets and App Engine applications.
- **Zonal Resources:** Bound to a specific zone. Examples include Compute Engine (GCE) VM instances and persistent disks.

*VAPT Context:* Because VPCs in GCP are global by default, a compromised instance in `asia-east1` can natively communicate with an internal database in `us-east1` if firewall rules allow it, greatly expanding the potential for lateral movement without the need for VPC peering.

## 3. GCP Resource Hierarchy
GCP uses a strict organizational hierarchy to manage policies and access control. Policies applied at a higher level are inherited by the levels below.

1. **Organization:** The root node for GCP resources, usually associated with a company's domain (e.g., `example.com`).
2. **Folders:** Organizational units within the Organization. Folders can contain projects or other folders, allowing for departmental or team-based structuring (e.g., "Engineering," "Finance").
3. **Projects:** The core trust boundary in GCP. All resources (VMs, buckets, databases) must belong to a project. Projects form the basis for billing, API enablement, and isolation.
4. **Resources:** The foundational cloud services (Compute Engine instances, Cloud Storage buckets).

## 4. ASCII Diagram: GCP Resource Hierarchy

```text
+----------------------------------------------------------------------------------+
|                            GCP RESOURCE HIERARCHY                                |
+----------------------------------------------------------------------------------+
|                                                                                  |
|                        [ Organization Node ]                                     |
|                       (e.g., example.com)                                        |
|                                |                                                 |
|          +---------------------+---------------------+                           |
|          |                                           |                           |
|          v                                           v                           |
|    [ Folder: Engineering ]                   [ Folder: Finance ]                 |
|          |                                           |                           |
|          v                                           v                           |
|    [ Project: Frontend-Dev ]                 [ Project: Payroll-App ]            |
|    (Trust & Billing Boundary)                (Trust & Billing Boundary)          |
|          |                                           |                           |
|   +------+------+                             +------+------+                    |
|   |             |                             |             |                    |
|   v             v                             v             v                    |
| [ GCE VM ]   [ GCS Bucket ]                [ Cloud SQL ] [ GKE Cluster ]         |
|                                                                                  |
+----------------------------------------------------------------------------------+
```

## 5. Core GCP Services & Security Posture

### 5.1 Compute Services
- **Google Compute Engine (GCE):** IaaS virtual machines.
  - *Pentesting focus:* OS vulnerabilities, exploiting custom metadata attributes, and SSRF attacks targeting the GCP Metadata server.
- **Google Kubernetes Engine (GKE):** The premier managed Kubernetes service. GCP's deep integration makes GKE highly robust, but misconfigurations are common.
  - *Pentesting focus:* Exploiting overly permissive RBAC roles, compromising pods to steal the attached Google Service Account credentials via Workload Identity.
- **Cloud Run & App Engine:** PaaS and serverless offerings for deploying containerized applications and code.
- **Cloud Functions:** Event-driven serverless compute (FaaS).

### 5.2 Storage Services
- **Cloud Storage (GCS):** Object storage, analogous to AWS S3.
  - *Pentesting focus:* Identifying buckets with `allUsers` or `allAuthenticatedUsers` permissions granted, leading to data exposure. (Note: `allAuthenticatedUsers` means ANY user with a Google account in the world, not just users in the organization).
- **Cloud SQL & Spanner:** Managed relational databases.
- **Bigtable & Firestore:** Managed NoSQL databases.

### 5.3 Networking Services
- **Virtual Private Cloud (VPC):** Provides networking functionality to Compute Engine instances, GKE containers, and the App Engine flexible environment.
- **Cloud Firewall:** GCP uses a global, distributed firewall system to restrict traffic to instances. Rules are applied using network tags or service accounts, rather than traditional IP-based Security Groups.
- **Cloud Armor:** Enterprise-grade DDoS defense and Web Application Firewall (WAF) services.

## 6. GCP Identity and Access Management (Cloud IAM)
Identity in GCP revolves around "Who can do what, on which resource."

### 6.1 Principals (Identities)
- **Google Accounts / Cloud Identity Users:** End users represented by an email address.
- **Google Groups:** Collections of Google Accounts.
- **Service Accounts:** Critical for machine-to-machine communication. These are special accounts used by applications or VMs, rather than people. They use RSA key pairs (Service Account Keys) for authentication outside of GCP, and metadata tokens inside GCP.

### 6.2 Roles
- **Basic (Primitive) Roles:** Owner, Editor, and Viewer. *Warning:* These are legacy roles and are incredibly broad. Using "Editor" grants extensive modification rights across the entire project. Their use is strongly discouraged in production.
- **Predefined Roles:** Granular roles created and maintained by Google (e.g., `roles/storage.objectAdmin`, `roles/compute.networkViewer`).
- **Custom Roles:** User-defined roles with highly specific, hand-picked permissions.

### 6.3 IAM Policies and Bindings
A policy is a collection of bindings. A binding binds one or more *members* (identities) to a single *role*.
- *VAPT Focus:* Pentesters heavily analyze these bindings to identify privilege escalation paths. For example, if a developer user has `roles/iam.serviceAccountUser` and `roles/compute.instanceAdmin.v1`, they can create an instance, attach a highly privileged Service Account (like a Project Owner) to it, log into the instance, and effectively become the Project Owner.

## 7. GCP Native Security & Logging Tools
- **Cloud Audit Logs:** Similar to AWS CloudTrail. It maintains Admin Activity logs, Data Access logs, and System Event logs. Data Access logs are often disabled by default to save money, creating blind spots.
- **Security Command Center (SCC):** A centralized vulnerability and threat reporting service.
- **VPC Service Controls:** A unique GCP feature that allows administrators to define security perimeters around Google-managed services (like Cloud Storage or BigQuery) to mitigate data exfiltration risks. Even if a user has valid credentials, they cannot access the API if the request originates from outside the defined network perimeter.

## 8. VAPT Perspective: Initial Attack Vectors in GCP

### 8.1 Exploiting the Metadata Server via SSRF
Like AWS, GCP instances utilize a metadata service located at `169.254.169.254`.
- **The GCP Nuance:** To prevent simple SSRF attacks, Google implemented a requirement long ago: the HTTP request MUST contain the custom header `Metadata-Flavor: Google`.
- **Bypass / Exploitation:** If a web application has a highly critical SSRF vulnerability that allows header injection, an attacker can supply the required header.
- **The Goal:** Querying `http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token` to steal the OAuth 2.0 access token of the attached Service Account.

### 8.2 Exposed Service Account Keys
Service accounts can have long-lived JSON keys generated for them so they can be used outside of GCP (e.g., in a CI/CD pipeline like GitHub Actions or Jenkins).
- *Vector:* These JSON files are frequently accidentally committed to source code repositories. An attacker finding one can immediately authenticate to GCP using `gcloud auth activate-service-account --key-file=key.json` and assume the permissions of that service account.

### 8.3 Over-Permissive IAM Bindings
As mentioned, relying on Basic roles (Editor/Owner) or misconfiguring the `iam.serviceAccountTokenCreator` role allows attackers to impersonate other identities or escalate privileges within the project.

## 9. Privilege Escalation and Lateral Movement in GCP
- **Impersonation:** If an attacker compromises a user or service account that possesses the `Service Account Token Creator` role over another service account, they can generate short-lived credentials for the target account, escalating their privileges.
- **Lateral Movement:** Attackers leverage the global VPC nature of GCP. If they compromise an edge proxy in one region, they will scan the internal VPC network to find open ports on database instances located in completely different regions.

## 10. BeyondCorp and Zero Trust
GCP heavily champions the BeyondCorp model—Google's implementation of Zero Trust. It shifts access controls from the network perimeter to individual users and devices. Context-Aware Access allows administrators to restrict access to GCP APIs based on user identity, device health, and geographic location, regardless of network boundaries.

## 11. Chaining Opportunities
- **[[02 - Cloud Shared Responsibility Model]]**: Determining the boundaries of security assessments when dealing with managed services like Google Kubernetes Engine (GKE) versus bare Compute Engine instances.
- **[[01 - Introduction to Cloud Computing IaaS PaaS SaaS]]**: Understanding how GCP's offerings map to standard cloud definitions.

## 12. Related Notes
- [[03 - Introduction to AWS Architecture and Services]]
- [[04 - Introduction to Azure Architecture and Services]]
- GCP IAM Privilege Escalation Techniques
- Exploiting Service Account JSON Keys

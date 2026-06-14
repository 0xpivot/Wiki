---
tags: [cloud, basics, foundations, vapt]
difficulty: beginner
module: "74 - Cloud Foundations Identity and Access"
topic: "74.02 Cloud Shared Responsibility Model"
---

# 74.02 Cloud Shared Responsibility Model

## 1. Executive Summary
The Cloud Shared Responsibility Model is the foundational security doctrine of cloud computing. It explicitly defines the security obligations of the Cloud Service Provider (CSP) and the customer (the consumer). A failure to understand this model is the root cause of the vast majority of cloud data breaches. For a VAPT professional, the Shared Responsibility Model acts as the ultimate guide for defining the Scope of Work (SoW) and Rules of Engagement (RoE). It dictates exactly what systems, layers, and configurations you are legally and technically permitted to test, and what remains off-limits within the provider's domain.

## 2. The Philosophy of Shared Responsibility
In traditional on-premises environments, the organization bears 100% of the responsibility for security—from locking the data center doors and powering the servers to patching the OS and securing the web application. 

When migrating to the cloud, organizations offload a significant portion of this operational burden to providers like AWS, Azure, or GCP. However, this offloading is not absolute. Security in the cloud is a **partnership**. 

The fundamental fallacy that plagues many organizations is the belief that "moving to the cloud means the cloud provider handles all the security." This assumption is catastrophic. The CSP is responsible for the security **OF** the cloud, while the customer is responsible for security **IN** the cloud. 

## 3. Detailed Breakdown: IaaS Responsibility
Infrastructure as a Service (IaaS) gives the customer the highest level of control, and consequently, the highest level of security responsibility.

### Provider Responsibilities (Security OF the Cloud)
- **Physical Security:** Securing the physical data centers, managing biometric access controls, security guards, and camera surveillance.
- **Hardware Infrastructure:** Maintaining the physical servers, storage arrays, network switches, and routers.
- **Virtualization Layer (Hypervisor):** Patching and securing the hypervisor (e.g., Xen, Nitro, KVM) to ensure strong isolation between different tenants (preventing VM escapes).

### Customer Responsibilities (Security IN the Cloud)
- **Operating System:** The customer must patch the guest OS, harden it, and manage local users (e.g., updating Windows Server or Ubuntu Linux).
- **Network Controls:** Configuring Virtual Private Clouds (VPCs), subnets, routing tables, network access control lists (NACLs), and host-based firewalls (Security Groups).
- **Application & Data:** Securing the deployed applications, managing API security, and ensuring data is encrypted at rest and in transit.
- **Identity & Access Management (IAM):** Managing who has access to the cloud console, the APIs, and the instances themselves.

## 4. Detailed Breakdown: PaaS Responsibility
Platform as a Service (PaaS) shifts more burden to the CSP. The customer no longer has access to the underlying operating system.

### Provider Responsibilities (Added from IaaS)
- **Operating System Management:** The CSP patches and secures the underlying OS.
- **Middleware and Runtime:** The CSP manages the execution environment (e.g., the Java runtime, the .NET framework, or the database engine itself in managed SQL services).
- **Network Configuration (Underlying):** The CSP manages the complex networking required to cluster and scale the platform services.

### Customer Responsibilities
- **Application Code:** The customer is solely responsible for ensuring their code is free from vulnerabilities like XSS, SQLi, and IDOR.
- **Data Governance:** Classifying data and enabling encryption features provided by the PaaS.
- **Platform Configuration:** Properly configuring the PaaS settings (e.g., setting up IP whitelisting for an Azure App Service or enabling logging on an RDS instance).
- **Identity & Access Management:** Still strictly a customer responsibility.

## 5. Detailed Breakdown: SaaS Responsibility
Software as a Service (SaaS) shifts the maximum amount of responsibility to the CSP. 

### Provider Responsibilities (Added from PaaS)
- **Application Code & Logic:** The CSP writes, maintains, and secures the application itself (e.g., Salesforce, Microsoft 365, Google Workspace).
- **Application Security:** The CSP conducts VAPT on their own code to prevent platform-wide breaches.

### Customer Responsibilities
- **Data:** You are always responsible for your data. If you upload sensitive PII to a SaaS application and share the link publicly, that is your fault, not the CSP's.
- **Endpoint Security:** The devices accessing the SaaS application must be secured by the customer.
- **Identity and Access Configuration:** Managing user accounts, enforcing Multi-Factor Authentication (MFA), and configuring RBAC within the SaaS platform.

## 6. Comprehensive ASCII Diagram of the Responsibility Matrix

```mermaid
table
| Security Layer | On-Premises | IaaS | PaaS / CaaS | SaaS |
|---|---|---|---|---|
| Data Governance & Classification | Customer | Customer | Customer | Customer |
| Client & Endpoint Protection | Customer | Customer | Customer | Customer |
| Identity & Access Management IAM | Customer | Customer | Customer | Customer |
| Application Controls Code, Logic, APIs | Customer | Customer | Customer | SHARED / CSP |
| Network Controls VPC, FW, Routing | Customer | Customer | SHARED / CSP | CSP |
| Host Infrastructure OS, Patching | Customer | Customer | CSP | CSP |
| Physical Security Compute, Storage | Customer | CSP | CSP | CSP |
| Data Center Facilities, Power | Customer | CSP | CSP | CSP |
```

## 7. The Core Customer Responsibilities Across All Models
Regardless of whether an organization uses IaaS, PaaS, or SaaS, there are three domains that **always** remain the responsibility of the customer. Attackers know this, and therefore, these areas are consistently the most targeted:

### 7.1 Identity and Access Management (The New Perimeter)
The CSP provides the tools (e.g., AWS IAM, Azure Entra ID, GCP Cloud IAM), but the customer must configure them correctly.
- Failing to enforce MFA.
- Creating overly broad policies (e.g., granting `s3:*` to a low-level application).
- Leaking static access keys.
- **VAPT Note:** Reviewing IAM policies is a massive part of any cloud penetration test. Privilege escalation almost always occurs via IAM misconfigurations.

### 7.2 Data Security and Encryption
The CSP provides the disks and the encryption engines (KMS), but the customer must click the button to enable encryption and must manage access to the decryption keys.
- The CSP is not responsible if a customer provisions an AWS S3 bucket or Azure Blob container and configures the ACLs to allow `Public Read`.
- The customer must classify their data and apply appropriate protection mechanisms.

### 7.3 Endpoint and User Device Responsibilities
If an employee's laptop is compromised with an info-stealer that extracts valid AWS session tokens, the attacker can access the cloud infrastructure. The CSP cannot protect against compromised valid credentials originating from an insecure endpoint.

## 8. Provider-Specific Nuances and Variations
While the general model holds true, different providers use different terminology and have slight nuances:
- **AWS:** Explicitly uses the "Security OF the Cloud vs. Security IN the Cloud" phrasing. AWS emphasizes that the customer is responsible for guest OS, applications, and security group configurations.
- **Azure:** Refers to it as the "Shared Responsibility Model" and places heavy emphasis on the fact that Identity and Devices are always the customer's responsibility.
- **GCP:** Also uses the shared responsibility framework but focuses heavily on "Shared Fate." GCP advocates for providing secure-by-default templates and proactive security tools to actively help customers avoid mistakes, rather than just legally absolving themselves of blame.

## 9. Implications for Penetration Testing and VAPT
The Shared Responsibility Model is the ultimate arbiter of a penetration test's scope.

### 9.1 Rules of Engagement (RoE)
- **What You CAN Test:** You can test anything that falls under the customer's responsibility. You can run vulnerability scans against the EC2 instance's OS, attempt SQL injection on the custom web application, and try to bypass IAM boundaries using compromised keys.
- **What You CANNOT Test:** You cannot test the provider's infrastructure. You cannot attempt a denial-of-service attack against the AWS API gateway endpoints. You cannot attempt to break out of a hypervisor. Testing physical security of an Azure data center is strictly forbidden.

### 9.2 The Evolution of CSP Penetration Testing Policies
Historically, CSPs required customers to fill out authorization forms days in advance before conducting a pentest. 
- Today, AWS, Azure, and GCP have updated their policies. Customers are generally permitted to conduct security assessments against their **own** infrastructure (EC2, VMs, App Services) without prior approval, provided they do not test shared infrastructure or perform DDoS attacks.
- However, testing managed services (like trying to hack the underlying infrastructure of AWS RDS or Azure SQL) remains strictly out of bounds.

## 10. Real-World Case Studies of Shared Responsibility Failures

### 10.1 The Capital One Data Breach (AWS)
In 2019, an attacker breached Capital One, stealing the data of over 100 million customers.
- **The Vector:** A Server-Side Request Forgery (SSRF) vulnerability existed in a ModSecurity Web Application Firewall (WAF) deployed on an EC2 instance. The attacker used SSRF to query the AWS Instance Metadata Service (IMDS) and stole the temporary IAM credentials associated with the WAF's underlying EC2 role. That role had excessive permissions, allowing the attacker to sync sensitive S3 buckets.
- **Responsibility Analysis:** AWS was not at fault. AWS's infrastructure functioned exactly as designed. Capital One was responsible for securing their web application (preventing SSRF) and adhering to the principle of least privilege for IAM roles. This was a failure of the customer's responsibility "IN" the cloud.

### 10.2 Ubiquitous S3 Bucket Leaks
Countless companies have suffered data exposures due to publicly accessible S3 buckets. 
- **Responsibility Analysis:** By default, all new S3 buckets are private. If an administrator actively changes the policy to `Public`, AWS executes that command. Securing the data configuration is solely a customer responsibility.

## 11. Security Tooling to Validate Responsibility
Because the burden of configuration falls to the customer, Cloud Security Posture Management (CSPM) tools are used to constantly scan the environment to ensure the customer is upholding their end of the bargain:
- Checking if encryption is enabled everywhere.
- Ensuring no security groups have port 22 open to the world.
- Validating that all IAM users have MFA enabled.

## 12. Chaining Opportunities
- **[[01 - Introduction to Cloud Computing IaaS PaaS SaaS]]**: The responsibility model dynamically shifts based on whether the target architecture is IaaS, PaaS, or SaaS.
- **[[03 - Introduction to AWS Architecture and Services]]**: To understand what you are allowed to test in AWS, you must apply the shared responsibility model to specific services like EC2, Lambda, and S3.

## 13. Related Notes
- [[04 - Introduction to Azure Architecture and Services]]
- [[05 - Introduction to GCP Architecture and Services]]
- Identity and Access Management Fundamentals
- Cloud Security Posture Management (CSPM)

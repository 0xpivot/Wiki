---
tags: [c2, red-team, infrastructure, vapt]
difficulty: intermediate
module: "94 - Command and Control Foundations and Architectures"
topic: "94.13 Automating Infrastructure Deployment Terraform Ansible"
---

# Automating Infrastructure Deployment: Terraform & Ansible

## Introduction
In professional red teaming and advanced adversary simulation, infrastructure is inherently ephemeral. Domains get burned, IP addresses are blacklisted by threat intelligence feeds, and redirectors are inevitably discovered and blocked by vigilant blue teams. Manually configuring servers, setting up intricate firewall rules, installing dependencies, deploying certificates, and tuning complex proxy configurations is not only incredibly time-consuming but highly prone to human error—errors that lead to catastrophic OPSEC failures and operational compromise.

To combat this, modern threat emulation teams adopt DevOps and Site Reliability Engineering (SRE) practices, specifically focusing on Infrastructure as Code (IaC) and Configuration Management. By utilizing industry-standard tools like Terraform and Ansible, operators can define their entire attack infrastructure in code, enabling them to deploy complex, multi-tier C2 architectures in minutes. This ensures absolute consistency, operational repeatability, version control of infrastructure, and the ability to rapidly recover and redeploy when infrastructure is burned during an engagement. A single typo in an Nginx configuration file can burn an entire operation; automation removes that variable entirely.

## The Role of Infrastructure as Code (IaC)

IaC involves managing and provisioning computing infrastructure through machine-readable definition files and APIs, rather than physical hardware configuration or interactive, manual configuration tools (like clicking through a cloud provider's web console).

### Terraform: Provisioning the Foundation
Terraform, developed by HashiCorp, is an open-source tool used for building, changing, and versioning infrastructure safely and efficiently. In a red team context, Terraform is responsible for the "heavy lifting" of cloud resource creation.

*   **Cloud Agnostic & Provider Architecture:** Terraform uses a provider architecture, allowing operators to deploy infrastructure across AWS, Azure, Google Cloud, DigitalOcean, Linode, and even on-premise virtualization platforms using the exact same declarative language (HashiCorp Configuration Language - HCL). This allows operators to easily shift infrastructure across different cloud providers to evade provider-specific blocking.
*   **Resource Management:** Terraform code defines the exact specifications for virtual machines (droplets/EC2 instances), DNS records (Route53, Cloudflare), security groups (firewall rules), VPC networking, and load balancers.
*   **State Management and Idempotency:** Terraform maintains a state file, meticulously tracking the current configuration of the deployed resources. This allows for declarative updates and, crucially, clean, automated teardown (`terraform destroy`) when an operation concludes or when infrastructure needs to be purged rapidly to avoid attribution.
*   **Variable Management:** Sensitive data such as API keys, domain names, and cloud regions are stored in variable files (`terraform.tfvars`), keeping the core logic clean and highly reusable across different engagements.

**Example Terraform Snippet (AWS EC2 Redirector & DNS):**
```hcl
# Define the security group restricting access
resource "aws_security_group" "redirector_sg" {
  name        = "rt-redirector-sg"
  description = "Allow inbound HTTP/HTTPS and restricted SSH"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Open to internet (filtered by Nginx later)
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["203.0.113.50/32"] # Restrict SSH to operator IP only
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Provision the EC2 Instance
resource "aws_instance" "http_redirector" {
  ami           = "ami-0c55b159cbfafe1f0" # Ubuntu 22.04 LTS
  instance_type = "t3.micro"
  key_name      = aws_key_pair.redteam_key.key_name
  
  vpc_security_group_ids = [aws_security_group.redirector_sg.id]

  tags = {
    Name = "rt-http-redirector-01"
    Role = "Redirector"
  }
}

# Automatically configure Route53 DNS
resource "aws_route53_record" "redirector_dns" {
  zone_id = aws_route53_zone.primary.zone_id
  name    = "update.malicious-domain.com"
  type    = "A"
  ttl     = "300"
  records = [aws_instance.http_redirector.public_ip]
}
```

### Ansible: Configuration and Orchestration
While Terraform provisions the raw servers and networking, Ansible (developed by Red Hat) is used to configure the software running on those servers. Ansible is agentless, operating over standard SSH, making it ideal for dynamically configuring newly provisioned Linux redirectors without needing pre-installed agents.

*   **Playbooks and Roles:** Ansible uses YAML-based playbooks to define the desired state of a system. Complex tasks are broken down into reusable "Roles" (e.g., a role for hardening SSH, a role for configuring Nginx).
*   **Software Installation:** Playbooks automate the installation of Nginx, Let's Encrypt (`certbot`), C2 frameworks, Docker, and necessary dependencies.
*   **Dynamic Configuration Management:** Ansible excels at templating configuration files using Jinja2. It can dynamically generate complex Nginx `default.conf` files containing specific mod_rewrite rules, proxy passes to the backend team server, and tailored SSL/TLS settings based on variables passed during the Terraform execution phase.
*   **Security Hardening:** Playbooks automatically lock down the SSH configuration (disabling password auth, changing default ports), set up UFW (Uncomplicated Firewall) rules limiting access to only specific IP ranges, and disable unnecessary services, drastically reducing the attack surface of the C2 infrastructure itself.
*   **Threat Intel Ingestion:** Advanced playbooks can curl known bad IP lists (e.g., Tor exit nodes, security vendor ASNs) and automatically populate `iptables` or UFW to silently drop traffic from these sources, shielding the infrastructure from active scanning.

**Example Ansible Playbook Snippet (Nginx Configuration and Hardening):**
```yaml
---
- name: Configure and Harden Nginx Redirector
  hosts: redirectors
  become: yes
  vars:
    team_server_ip: "10.0.0.50"
    domain_name: "update.malicious-domain.com"
    
  tasks:
    - name: Ensure Nginx is installed and up to date
      apt:
        name: nginx
        state: latest
        update_cache: yes

    - name: Deploy dynamic Nginx proxy configuration
      template:
        src: templates/nginx_c2_proxy.j2
        dest: /etc/nginx/sites-available/default
      notify: Reload Nginx

    - name: Secure SSH configuration (Disable Root Password Auth)
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?PermitRootLogin'
        line: 'PermitRootLogin prohibit-password'
      notify: Restart SSH

    - name: Ensure UFW is running and denies all incoming by default
      ufw:
        state: enabled
        policy: deny

    - name: Allow incoming HTTPS traffic through UFW
      ufw:
        rule: allow
        port: '443'
        proto: tcp

  handlers:
    - name: Reload Nginx
      service:
        name: nginx
        state: reloaded

    - name: Restart SSH
      service:
        name: sshd
        state: restarted
```

## The Automation Workflow (CI/CD for Attack Infra)

A standard, mature automated deployment workflow mirrors modern CI/CD pipelines:
1.  **Code & Define:** The operator writes or modifies Terraform HCL and Ansible YAML in a local Git repository, defining the required VMs, DNS, and software configuration. All OPSEC rules are codified here.
2.  **Provision (Terraform):** `terraform apply` is executed. Terraform communicates with the cloud provider APIs to spin up the servers, configure firewalls, and set DNS records.
3.  **Dynamic Inventory Generation:** Terraform outputs the public IP addresses of the newly created servers. These IPs are dynamically formatted and fed into an Ansible inventory file. This is crucial as cloud IPs are ephemeral.
4.  **Configure (Ansible):** `ansible-playbook` is executed against the new dynamic inventory. Ansible connects via SSH, hardens the OS, installs software, deploys certificates, configures complex proxy rules, and starts the services.
5.  **Validation:** Automated scripts verify the infrastructure is routing traffic correctly and returning expected profiles before the infrastructure is marked "live."
6.  **Operate:** The C2 infrastructure is fully functional, secure, and ready to receive beacons.
7.  **Destroy/Burn:** When infrastructure is compromised, `terraform destroy -auto-approve` completely eradicates the infrastructure from the cloud provider, leaving zero forensic trace, allowing the operator to instantly spin up replacement nodes.

## ASCII Workflow Diagram

```text
+---------------------+        +-----------------------+        +-----------------------+
|                     |        |                       |        |                       |
|  Red Team Operator  |        |  Cloud Provider APIs  |        |  Provisioned Assets   |
|  (Git / Terminal)   |        |  (AWS, Azure, DO)     |        |  (Redirectors/C2)     |
|                     |        |                       |        |                       |
+---------+-----------+        +----------+------------+        +----------+------------+
          |                               |                                |
          | 1. `terraform apply`          |                                |
          |------------------------------>|                                |
          |                               |                                |
          | 2. Create VMs, SecGroups, DNS |                                |
          |<------------------------------|                                |
          |                               |                                |
          | 3. VMs Created, IPs Returned  |                                |
          |<------------------------------|                                |
          |                               |                                |
          | 4. Generate Dynamic Inventory |                                |
          |    (Local Process)            |                                |
          |                               |                                |
          | 5. `ansible-playbook -i ...`  |                                |
          |--------------------------------------------------------------->|
          |                               |                                |
          | 6. Harden OS, Install Nginx, Deploy Certs, Set Proxy Rules     |
          |<---------------------------------------------------------------|
          |                               |                                |
          | 7. Infrastructure Ready & Validated!                           |
```

## Real-World Attack Scenario

**Operation Phoenix**

A red team was conducting a high-stakes, long-term simulation against a defense contractor. The blue team was highly skilled, proactive, and actively hunting network anomalies.
1.  **Initial Setup:** The red team used their centralized IaC repository to spin up a complex multi-tier architecture, including a team server, three distinct redirectors across different cloud providers, and automated payload generation via CI/CD, all in under 15 minutes.
2.  **Detection:** During week two, the blue team identified a subtle behavioral anomaly in a compromised host and successfully traced the HTTPS connection back to the primary redirector domain (`cloud-sync-telemetry.com`). They immediately blocked the domain, sinkholed the DNS, and blocked the IP at the perimeter firewall. They believed they had severed the C2 channel.
3.  **Failover:** The red team's persistent beacon on the host, unable to reach the primary redirector, automatically went to sleep and prepared to attempt connection to its secondary failover domain in 24 hours.
4.  **Rapid Recovery:** Instead of panicking or manually configuring new servers, the red team operator opened their code editor. They updated the `terraform.tfvars` variables file with a newly procured backup domain (`azure-update-services.net`) and changed the target cloud provider region to avoid IP neighborhood blacklists.
5.  **Execution:** They ran `terraform destroy -auto-approve` to completely wipe the burned, compromised infrastructure, removing any forensic evidence the blue team could analyze from the cloud side.
6.  **Redeployment:** They then ran their single pipeline script, which executed `terraform apply` followed immediately by the Ansible playbook execution.
7.  **Outcome:** Within 8 minutes, an entirely new redirector node was spun up in a different cloud provider, with a new IP address, freshly generated Let's Encrypt certificates, and the exact same complex Nginx filtering rules. When the beacon woke up and attempted its secondary connection, the new infrastructure was fully operational. The red team regained control seamlessly, demonstrating the incredible resilience and power of "burnable," code-defined infrastructure. The blue team was left analyzing dead IP addresses.

## Chaining Opportunities

Automation is the critical glue that holds advanced infrastructure together:
*   Automated deployment is absolutely essential for rapidly building, scaling, and managing the complex topologies discussed in [[11 - Multi-Tier C2 Architectures]]. Manual deployment at that scale is impossible and prone to catastrophic failure.
*   Ansible playbooks ensure that the strict, exact configurations required by [[12 - C2 OPSEC Best Practices]] (like JARM evasion, header filtering, rigorous IP blacklists) are applied consistently every single time, preventing manual misconfigurations that could expose the team server.
*   Automation scripts can be designed to automatically download, compile, modify, and securely configure the advanced tools and team servers discussed in [[14 - Popular Open Source Frameworks Metasploit Empire Covenant]], providing a turn-key, secure attack platform in minutes.
*   The principles of IaC also extend to payload generation pipelines. Advanced teams use CI/CD runners to automatically compile, obfuscate, and sign payloads on demand.

## Advanced Infrastructure as Code Techniques

To truly master infrastructure deployment, Red Teams must move beyond basic provisioning and explore advanced IaC capabilities that enhance resilience and OPSEC.

### 1. Terraform State Management and Security
The Terraform state file (`terraform.tfstate`) is a highly sensitive asset. It contains plain-text details of the entire deployed infrastructure, including IP addresses, cloud provider resource IDs, and potentially sensitive variables.
*   **Remote State Storage:** Never store state files locally or commit them to Git. Utilize remote state backends like AWS S3 or HashiCorp Consul.
*   **State Encryption:** Ensure the remote state bucket is encrypted at rest and access is strictly controlled via IAM policies.
*   **State Locking:** Implement state locking (e.g., using DynamoDB with S3) to prevent multiple operators from concurrently modifying the infrastructure, which can lead to corruption or inconsistent states during a fast-paced engagement.

### 2. Immutable Infrastructure
A core principle derived from SRE is immutable infrastructure. Once a redirector or team server is deployed and configured, it should never be manually modified via SSH.
*   **No SSH Access:** In highly mature setups, SSH access to redirectors is entirely disabled after the initial Ansible configuration. If a change is required (e.g., updating a Nginx proxy rule or adding an IP to a blacklist), the change is made in the Ansible code, the old redirector is destroyed via Terraform, and a new one is provisioned.
*   **Benefits:** This ensures absolute consistency, eliminates configuration drift, and ensures that the infrastructure defined in code exactly matches reality. It also prevents attackers (or Blue Teams) from gaining persistence on the infrastructure itself.

### 3. CI/CD Integration for Payload Generation
Automation should extend to payload compilation. Advanced teams integrate their IaC pipelines with CI/CD tools (like GitLab CI, GitHub Actions, or Jenkins).
*   **Automated Compilation:** When an operator commits a change to a C2 profile or payload source code, the CI/CD pipeline automatically compiles the new payload, obfuscates it, signs it (if necessary), and securely delivers it to the team server.
*   **Dynamic Variable Substitution:** The CI/CD pipeline can dynamically inject the newly provisioned redirector domains and IPs from the Terraform output directly into the payload compilation process, ensuring the payload is always configured with the latest, live infrastructure details without manual intervention.

## Managing Complex Topologies

As engagements scale, managing multiple discrete infrastructures becomes necessary. Red Teams often utilize Terraform Workspaces or terragrunt to manage different environments.
*   **Development/Testing:** An environment used for testing new C2 profiles, Ansible roles, and payload execution techniques.
*   **Staging:** An environment that closely mirrors the target's infrastructure for final validation before deployment.
*   **Production (Live Op):** The heavily locked down, actively monitored infrastructure used for the actual engagement.
Using automation allows a team to spin up, test, and tear down these distinct environments effortlessly, ensuring high confidence in their tools before encountering active defenses.

## Related Notes
*   [[11 - Multi-Tier C2 Architectures]]
*   [[12 - C2 OPSEC Best Practices]]
*   [[14 - Popular Open Source Frameworks Metasploit Empire Covenant]]
*   [[90 - Red Team Infrastructure Setup]]
*   [[96 - Cloud Infrastructure for Red Teams]]
*   [[98 - CI/CD Pipelines for Offensive Operations]]
*   [[104 - Ansible for Red Team Operations]]

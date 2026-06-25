---
course: DevSecOps
topic: Integrating Automated Security Testing into a CI CD Pipeline
tags: [devsecops]
---

## Setting Up Firewall Access Control Lists

When integrating automated security testing into a CI/CD pipeline, one of the critical aspects is ensuring that the environment is properly segmented and secured. This includes setting up firewall access control lists (ACLs) to restrict access between different components of the pipeline.

### What Are Firewall ACLs?

Firewall access control lists are rules that define which traffic is allowed or denied based on criteria such as source IP address, destination IP address, port numbers, and protocols. These rules help in controlling the flow of traffic within a network and can be used to enforce security policies.

### Why Use Firewall ACLs?

Using firewall ACLs helps in isolating different parts of the pipeline, such as test environments and build servers. By restricting access, you reduce the attack surface and limit the potential damage in case of a breach. This is particularly important in a CI/CD pipeline where automated processes can be exploited to spread malware or exfiltrate sensitive data.

### How to Set Up Firewall ACLs

To set up firewall ACLs, you need to define rules that specify which traffic is allowed and which is denied. Here’s an example of how to configure firewall ACLs using iptables on a Linux system:

```bash
# Allow traffic from test environment to build server
iptables -A INPUT -s <test_environment_ip> -d <build_server_ip> -j ACCEPT

# Allow traffic from build server to test environment
iptables -A OUTPUT -s <build_server_ip> -d <test_environment_ip> -j ACCEPT

# Deny all other traffic
iptables -A INPUT -j DROP
iptables -A OUTPUT -j DROP
```

### Real-World Example

In the context of a CI/CD pipeline, consider a scenario where a test environment was compromised due to lax firewall rules. A recent breach at a major tech company involved attackers gaining access to a test environment and then moving laterally to the build server. Properly configured firewall ACLs could have prevented this lateral movement.

### How to Prevent / Defend

**Detection:**
- Monitor firewall logs for unauthorized access attempts.
- Use intrusion detection systems (IDS) to alert on suspicious activity.

**Prevention:**
- Implement strict firewall ACLs to limit access between different components of the pipeline.
- Regularly review and update firewall rules to reflect changes in the environment.

**Secure Configuration:**
```bash
# Secure configuration example
iptables -A INPUT -s <trusted_source_ip> -d <build_server_ip> -j ACCEPT
iptables -A OUTPUT -s <build_server_ip> -d <trusted_destination_ip> -j ACCEPT
iptables -A INPUT -j DROP
iptables -A OUTPUT -j DROP
```

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Hardening the Pipeline/09-Restricting Access to Jobs|Restricting Access to Jobs]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Hardening the Pipeline/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Hardening the Pipeline/11-System Hardening|System Hardening]]

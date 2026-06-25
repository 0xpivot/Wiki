---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management

Secrets management is a critical aspect of modern software development and operations, particularly within the DevSecOps paradigm. In today’s complex IT environments, applications often require access to sensitive data such as passwords, API keys, and certificates. Managing these secrets securely is essential to prevent unauthorized access and potential data breaches. This chapter delves into the capabilities of HashiCorp Vault, a leading secrets management tool, focusing on its dynamic secrets feature and how it enhances security.

### Centralized Secret Storage and Access Control

Centralized secret storage is a foundational principle of secrets management. Instead of distributing secrets across various systems and configurations, a centralized repository ensures that secrets are stored in a secure location. This approach simplifies management and reduces the risk of exposure.

**Access Control:**
Access control is crucial to ensure that only authorized entities can retrieve secrets. This is typically achieved through role-based access control (RBAC) mechanisms, where permissions are granted based on roles rather than individual identities. For example, a developer might have read-only access to certain secrets, while an administrator might have full access.

#### Example: Vault Configuration

```yaml
# Example Vault Policy
path "secret/data/*" {
  capabilities = ["read"]
}

path "secret/data/admin/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
```

In this example, the policy grants read access to all secrets under `secret/data/*` and full access to secrets under `secret/data/admin/*`.

### Human and Application Access

Once secrets are stored centrally, both humans and applications can access them securely. Applications typically use APIs to fetch secrets, while humans might use command-line interfaces or web-based UIs provided by the secrets management tool.

#### Example: Application Accessing Secrets

```python
import hvac

client = hvac.Client(url='http://127.0.0.1:8200', token='my-root-token')
secret = client.secrets.kv.v2.read_secret_version(path='my-secret-path')

print(secret['data']['data'])
```

This Python script uses the HashiCorp Vault API to read a secret from the `my-secret-path`. The `token` used here should be securely managed and rotated regularly.

### Post-Access Security Concerns

While centralized storage and access control significantly enhance security, there are still risks associated with how applications handle secrets once they are retrieved. One major concern is the accidental exposure of secrets through logging.

#### Real-World Example: Logging Vulnerability

Consider a scenario where a junior developer adds debug logging to an application:

```python
import hvac

client = hvac.Client(url='http://127.0.0.1:8200', token='my-root-token')
secret = client.secrets.kv.v2.read_secret_version(path='my-secret-path')

print(f"Retrieved secret: {secret['data']['data']}")
```

If this code is deployed, the secret will be logged, potentially exposing it to anyone with access to the logs.

### Log Collection and Visualization

To mitigate this risk, organizations often implement log collection and visualization tools. These tools aggregate logs from various sources and provide a unified view for monitoring and analysis.

#### Example: ELK Stack

The ELK stack (Elasticsearch, Logstash, Kibana) is a popular choice for log management. Logs are collected by Logstash, indexed by Elasticsearch, and visualized in Kibana.

```json
{
  "type": "syslog",
  "host": "localhost",
  "port": 514,
  "codec": "plain",
  "tags": [ "syslog" ]
}
```

This configuration snippet for Logstash collects syslog messages from `localhost` and tags them appropriately.

### Dynamic Secrets Feature

Dynamic secrets address the issue of secret exposure by providing short-lived credentials that expire after a set period. This ensures that even if a secret is exposed, it is only valid for a limited time.

#### How Dynamic Secrets Work

When an application requests a secret, Vault generates a new, short-lived credential. This credential is valid only for a specified duration, after which it expires automatically.

#### Example: Dynamic Database Credentials

```json
{
  "lease_id": "db-creds/my-role/1234567890",
  "lease_duration": 3600,
  "renewable": true,
  "data": {
    "username": "generated-user",
    "password": "generated-password"
  }
}
```

In this example, Vault generates a database user and password that are valid for one hour (`lease_duration`). After this period, the credentials expire.

### Implementation and Usage

To implement dynamic secrets, you need to configure Vault with the appropriate secrets engine and policies.

#### Example: Configuring Dynamic Database Credentials

```bash
vault secrets enable database
vault write database/config/my-postgresql \
  plugin_name=postgresql-database-plugin \
  connection_url="postgresql://{{username}}:{{password}}@localhost:5432/postgres?sslmode=disable" \
  allowed_roles="readonly" \
  username="admin" \
  password="adminpassword"

vault write database/roles/readonly \
  db_name=my-postgresql \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
                       GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"
```

This configuration sets up a PostgreSQL database connection and defines a role (`readonly`) that generates short-lived credentials.

### Pitfalls and Common Mistakes

Despite the benefits of dynamic secrets, there are several pitfalls to be aware of:

1. **Credential Rotation:** Ensure that credentials are rotated frequently to minimize exposure.
2. **Policy Enforcement:** Strictly enforce access policies to prevent unauthorized access.
3. **Monitoring:** Continuously monitor logs and audit trails to detect any unauthorized access attempts.

### How to Prevent / Defend

#### Detection

Implement continuous monitoring and alerting for any suspicious activities related to secret retrieval and usage.

#### Prevention

1. **Secure Access Policies:** Enforce strict RBAC policies to limit access to secrets.
2. **Regular Audits:** Conduct regular audits to ensure compliance with security policies.
3. **Training:** Educate developers about the importance of secure coding practices and the risks associated with improper handling of secrets.

#### Secure Coding Fixes

Compare the insecure and secure versions of code to highlight best practices.

**Insecure Code:**

```python
import hvac

client = hvac.Client(url='http://127.0.0.1:8200', token='my-root-token')
secret = client.secrets.kv.v2.read_secret_version(path='my-secret-path')

print(f"Retrieved secret: {secret['data']['data']}")
```

**Secure Code:**

```python
import hvac

client = hvac.Client(url='http://127.0.0.1:8200', token='my-root-token')
secret = client.secrets.kv.v2.read_secret_version(path='my-secret-path')

# Use the secret immediately and avoid logging it
use_secret(secret['data']['data'])
```

### Conclusion

Dynamic secrets are a powerful feature of HashiCorp Vault that significantly enhances the security of secret management. By generating short-lived credentials, Vault ensures that even if a secret is exposed, it is only valid for a limited time. Proper implementation and usage of dynamic secrets, along with robust access control and monitoring, can greatly reduce the risk of unauthorized access and data breaches.

### Hands-On Labs

For practical experience with Vault and dynamic secrets, consider the following labs:

- **PortSwigger Web Security Academy:** Offers interactive labs on web security, including sections on secrets management.
- **HashiCorp Learn:** Provides official tutorials and labs for learning Vault and other HashiCorp products.
- **CloudGoat:** Focuses on cloud security and includes scenarios involving secrets management in cloud environments.

By engaging with these labs, you can gain hands-on experience and deepen your understanding of secrets management and dynamic secrets.

---
<!-- nav -->
[[01-Introduction to Secrets Management and Vault|Introduction to Secrets Management and Vault]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/08-Vault Capabilities Vault Deep Dive Part 1/00-Overview|Overview]] | [[03-Secrets Management and Revocation|Secrets Management and Revocation]]

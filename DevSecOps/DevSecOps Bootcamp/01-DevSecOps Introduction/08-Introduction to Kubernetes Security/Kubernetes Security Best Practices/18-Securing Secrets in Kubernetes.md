---
course: DevSecOps
topic: Introduction to Kubernetes Security
tags: [devsecops]
---

## Securing Secrets in Kubernetes

### Managing Encryption Keys

One of the critical aspects of securing a Kubernetes cluster is managing encryption keys. These keys are essential for encrypting sensitive data such as secrets, but they also introduce a new challenge: how to securely store and manage these keys themselves.

#### What Are Encryption Keys?

Encryption keys are strings of bits used to encrypt and decrypt data. In the context of Kubernetes, these keys are used to protect sensitive information such as passwords, tokens, and certificates. Without proper management, these keys can become a significant security risk if they fall into the wrong hands.

#### Why Manage Encryption Keys Securely?

Managing encryption keys securely is crucial because if an attacker gains access to these keys, they can decrypt sensitive data, leading to potential data breaches and unauthorized access to critical systems.

#### How to Manage Encryption Keys

There are several methods to manage encryption keys securely:

1. **Third-Party Key Management Services**: Tools like AWS Key Management Service (KMS) can be used to manage encryption keys. AWS KMS provides a centralized service to create, manage, and control access to cryptographic keys.

2. **HashiCorp Vault**: Another popular tool is HashiCorp Vault, which provides a secure place to store and manage secrets. Vault can handle encryption keys and other sensitive data, ensuring they are protected and accessible only to authorized users.

#### Example: Using AWS KMS

Here’s an example of how to use AWS KMS to manage encryption keys:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  password: <base64-encoded-password>
```

To encrypt the `password` using AWS KMS, you would first generate a key in AWS KMS and then use the AWS CLI to encrypt the data:

```sh
aws kms encrypt --key-id <your-key-id> --plaintext fileb://<path-to-your-file>
```

The encrypted data can then be stored in the Kubernetes secret.

#### Example: Using HashiCorp Vault

Vault can be configured to store and manage secrets securely. Here’s an example of how to store a secret in Vault:

```sh
vault kv put secret/my-secret password=<your-password>
```

Vault can also be integrated with Kubernetes to automatically inject secrets into pods.

### Securing Secrets in Kubernetes

Another critical aspect of Kubernetes security is securing secrets. Secrets are used to store sensitive data such as passwords, tokens, and certificates. These secrets are stored in a key-value store called etcd.

#### What Is etcd?

etcd is a distributed key-value store used by Kubernetes to store configuration data and metadata about the cluster. It is a crucial component of Kubernetes, responsible for maintaining the state of the cluster.

#### Why Secure etcd?

etcd stores all the configuration data and metadata of the Kubernetes cluster, including secrets. If an attacker gains access to etcd, they can bypass the API server and make direct changes to the cluster, leading to unauthorized access and potential data breaches.

#### How to Secure etcd

There are several ways to secure etcd:

1. **Encryption at Rest**: Enable encryption at rest for etcd to ensure that data is protected even if the storage is compromised.

2. **Access Control**: Implement strict access controls to limit who can access etcd. This includes using TLS for secure communication and setting up role-based access control (RBAC).

3. **Backup and Recovery**: Regularly back up etcd data and test recovery procedures to ensure that data can be restored in case of a compromise.

#### Example: Enabling Encryption at Rest

To enable encryption at rest for etcd, you need to configure etcd with encryption settings. Here’s an example of how to do this:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: etcd-config
  namespace: kube-system
data:
  etcd.conf: |
    [member]
    ETCD_DATA_DIR="/var/lib/etcd"
    ETCD_NAME="default"
    ETCD_LISTEN_PEER_URLS="https://localhost:2380"
    ETCD_LISTEN_CLIENT_URLS="https://localhost:2379"
    ETCD_CERT_FILE="/etc/kubernetes/pki/etcd/server.crt"
    ETCD_KEY_FILE="/etc/kubernetes/pki/etcd/server.key"
    ETCD_TRUSTED_CA_FILE="/etc/kubernetes/pki/etcd/ca.crt"
    ETCD_CLIENT_CERT_AUTH="true"
    ETCD_PEER_CERT_FILE="/etc/kubernetes/pki/etcd/peer.crt"
    ETCD_PEER_KEY_FILE="/etc/kubernetes/pki/etcd/peer.key"
    ETCD_PEER_TRUSTED_CA_FILE="/etc/kubernetes/pki/etcd/ca.crt"
    ETCD_PEER_CLIENT_CERT_AUTH="true"
    ETCD_PEER_TLS_ENABLED="true"
    ETCD_DATA_DIR_ENCRYPTION_KEY="your-encryption-key"
```

This configuration enables encryption at rest for etcd.

#### Example: Setting Up Access Control

To set up access control for etcd, you can use RBAC to define roles and permissions. Here’s an example of how to do this:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: etcd-admin
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: etcd-admin-binding
subjects:
- kind: User
  name: admin-user
roleRef:
  kind: ClusterRole
  name: etcd-admin
  apiGroup: rbac.authorization.k8s.io
```

This configuration sets up a cluster role and binding to allow the `admin-user` to manage secrets in etcd.

### Real-World Examples and Breaches

#### Recent CVEs and Breaches

Several recent CVEs and breaches highlight the importance of securing secrets and etcd in Kubernetes:

1. **CVE-2021-25741**: This vulnerability in Kubernetes allowed attackers to bypass authentication and gain unauthorized access to the cluster. By exploiting this vulnerability, attackers could potentially access etcd and modify sensitive data.

2. **Cloudflare Data Breach (2019)**: In this breach, an attacker gained access to Cloudflare’s internal systems, including their Kubernetes clusters. The attacker was able to access etcd and steal sensitive data, including customer information.

These examples demonstrate the critical nature of securing secrets and etcd in Kubernetes.

### How to Prevent / Defend

#### Detection

To detect unauthorized access to etcd, you can implement monitoring and logging:

1. **Monitoring**: Set up monitoring to detect unusual activity in etcd, such as unexpected changes or access patterns.

2. **Logging**: Enable detailed logging for etcd to capture all access and modification events. This can help in identifying and investigating suspicious activities.

#### Prevention

To prevent unauthorized access to etcd, you can implement the following measures:

1. **Encryption at Rest**: Ensure that etcd data is encrypted at rest to protect against physical theft or unauthorized access.

2. **Access Control**: Implement strict access controls to limit who can access etcd. Use TLS for secure communication and set up RBAC to define roles and permissions.

3. **Regular Backups**: Regularly back up etcd data and test recovery procedures to ensure that data can be restored in case of a compromise.

#### Secure Coding Fixes

Here’s an example of how to securely store and manage secrets in Kubernetes:

**Vulnerable Code:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  password: <base64-encoded-password>
```

**Secure Code:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  password: <encrypted-password>
```

In the secure code, the password is encrypted using a key management service like AWS KMS or HashiCorp Vault.

### Conclusion

Securing secrets and etcd in Kubernetes is crucial for protecting sensitive data and preventing unauthorized access. By implementing encryption at rest, strict access controls, and regular backups, you can significantly reduce the risk of data breaches and unauthorized access. Additionally, monitoring and logging can help detect and investigate suspicious activities, ensuring the security of your Kubernetes cluster.

### Practice Labs

For hands-on experience with Kubernetes security, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A project for learning about secrets management in Kubernetes.
- **kube-hunter**: A tool for finding security issues in Kubernetes clusters.

These labs provide practical experience in securing Kubernetes clusters and can help you master the concepts covered in this chapter.

---
<!-- nav -->
[[17-Running Applications with Non-Root Users in Kubernetes|Running Applications with Non-Root Users in Kubernetes]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/08-Introduction to Kubernetes Security/Kubernetes Security Best Practices/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/08-Introduction to Kubernetes Security/Kubernetes Security Best Practices/19-Practice Questions & Answers|Practice Questions & Answers]]

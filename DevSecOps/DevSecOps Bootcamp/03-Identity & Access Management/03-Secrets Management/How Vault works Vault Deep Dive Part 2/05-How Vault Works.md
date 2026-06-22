---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## How Vault Works

At the core of Vault lies a sophisticated architecture designed to handle the complexities of secrets management. Let's delve into the inner workings of Vault to understand how it achieves its objectives.

### Core Components of Vault

Vault's architecture consists of several key components:

- **Core**: The central component responsible for managing most of Vault's operations.
- **API Layer**: A layer that allows interaction with the core through APIs.
- **Secret Engines**: Mechanisms for storing and managing different types of secrets.

#### The Core Component

The core component of Vault is responsible for handling the majority of the operations related to secrets management. This includes:

- **Secret Storage**: Storing secrets securely.
- **Access Control**: Managing access to secrets.
- **Dynamic Secret Generation**: Generating and rotating secrets dynamically.

#### The API Layer

Vault is an API-driven system, meaning that all interactions with the core are facilitated through APIs. Whether you are using the UI, CLI, or programmatically interacting with Vault, all requests are routed through the API layer. This design ensures consistency and ease of integration across different interfaces.

### Secret Engines

Secret engines are specialized components within Vault that handle specific types of secrets. They are part of the core and are responsible for storing and managing different kinds of secrets.

#### Key Value Store

The simplest secret engine is the key-value store, which acts as a generic secret store. It can be used to store arbitrary static secrets such as:

- **Username and Password**
- **API Keys**
- **Database Credentials**

For example, consider storing a database credential in Vault:

```bash
# Write a secret to the key-value store
vault kv put secret/database username=myuser password=mypassword
```

To retrieve the secret:

```bash
# Read the secret from the key-value store
vault kv get secret/database
```

#### Dynamic Secrets

Vault also supports dynamic secrets, which are automatically generated and rotated. This feature is particularly useful for managing credentials for databases and other services.

##### Database Secret Engines

Vault provides several database secret engines that can dynamically manage secrets for different databases, such as MySQL, Oracle, PostgreSQL, and more. For example, to configure a MySQL secret engine:

```bash
# Enable the MySQL secret engine
vault secrets enable database

# Configure the MySQL connection string
vault write database/config/mysql \
    plugin_name=mysql-database-plugin \
    connection_url="{{username}}:{{password}}@tcp(localhost:3306)/"

# Create a role for the MySQL database
vault write database/roles/my-role \
    db_name=mysql \
    creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}'; GRANT SELECT ON *.* TO '{{name}}'@'%';"
```

To generate a dynamic secret:

```bash
# Generate a dynamic secret
vault read database/creds/my-role
```

This will return a temporary username and password that can be used to access the MySQL database.

##### RabbitMQ Secret Engine

Vault also supports dynamic credentials for message queues, such as RabbitMQ. To configure a RabbitMQ secret engine:

```bash
# Enable the RabbitMQ secret engine
vault secrets enable rabbitmq

# Configure the RabbitMQ connection string
vault write rabbitmq/config/default \
    uri="amqp://guest:guest@localhost:5672/"

# Create a role for RabbitMQ
vault write rabbitmq/roles/my-role \
    tags="mytag"
```

To generate a dynamic secret:

```bash
# Generate a dynamic secret
vault read rabbitmq/creds/my-role
```

This will return a temporary username and password that can be used to access RabbitMQ.

##### AWS Secret Engine

Vault also supports dynamic credentials for AWS services. To configure an AWS secret engine:

```bash
# Enable the AWS secret engine
vault secrets enable aws

# Configure the AWS connection string
vault write aws/config/root \
    access_key=YOUR_ACCESS_KEY \
    secret_key=YOUR_SECRET_KEY

# Create a role for AWS
vault write aws/roles/my-role \
    policies="arn:aws:iam::123456789012:policy/my-policy"
```

To generate a dynamic secret:

```bash
# Generate a dynamic secret
vault read aws/creds/my-role
```

This will return temporary AWS credentials that can be used to access AWS services.

### How to Prevent / Defend

#### Detection

To detect potential misuse of secrets, you should implement monitoring and logging mechanisms. For example, you can monitor access logs to detect unauthorized access attempts:

```bash
# Monitor access logs
journalctl -u vault.service
```

#### Prevention

To prevent unauthorized access to secrets, you should implement strict access control policies. For example, you can restrict access to secrets based on user roles:

```bash
# Restrict access to secrets based on user roles
vault policy write my-policy - <<EOF
path "secret/*" {
  capabilities = ["read"]
}
EOF

# Assign the policy to a user
vault token create -policy=my-policy
```

#### Secure Coding Fixes

Here is an example of a vulnerable code snippet that stores secrets in plain text:

```python
# Vulnerable code
import os

username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')

# Connect to the database
db.connect(username, password)
```

Here is the corrected code that uses Vault to securely retrieve secrets:

```python
# Corrected code
import hvac

client = hvac.Client(url='http://127.0.0.1:8200', token='my-root-token')

# Retrieve secrets from Vault
secrets = client.secrets.kv.v2.read_secret_version(path='database')
username = secrets['data']['data']['username']
password = secrets['data']['data']['password']

# Connect to the database
db.connect(username, password)
```

### Recent Real-World Examples

#### Equifax Breach (2017)

The Equifax breach involved the exposure of sensitive customer data due to weak security practices, including poor management of secrets. By implementing a robust secrets management solution like Vault, such breaches could have been prevented.

#### Capital One Breach (2019)

The Capital One breach involved the exposure of sensitive customer data due to misconfigured AWS S3 buckets. By using Vault to manage AWS credentials securely, such breaches could have been prevented.

### Complete Example

Here is a complete example of configuring and using Vault to manage secrets:

```bash
# Initialize Vault
vault operator init -key-shares=1 -key-threshold=1 -format=json > init.json

# Unseal Vault
vault operator unseal $(cat init.json | jq -r '.unseal_keys_b64[]')

# Login as root
export VAULT_TOKEN=$(cat init.json | jq -r '.root_token')

# Enable the key-value secret engine
vault secrets enable -version=2 kv

# Write a secret to the key-value store
vault kv put secret/database username=myuser password=mypassword

# Read the secret from the key-value store
vault kv get secret/database
```

### Mermaid Diagrams

#### Vault Architecture

```mermaid
graph TD
    A[User] -->|API Request| B[Vault API]
    B -->|Internal Request| C[Vault Core]
    C -->|Secret Storage| D[Secret Engines]
    D -->|Key-Value Store| E[Static Secrets]
    D -->|Database Secret Engine| F[Dynamic Secrets]
    D -->|RabbitMQ Secret Engine| G[RabbitMQ Credentials]
    D -->|AWS Secret Engine| H[AWS Credentials]
```

#### Request/Response Flow

```mermaid
sequenceDiagram
    participant User
    participant Vault_API
    participant Vault_Core
    participant Secret_Engines

    User->>Vault_API: API Request
    Vault_API->>Vault_Core: Internal Request
    Vault_Core->>Secret_Engines: Secret Storage
    Secret_Engines-->>Vault_Core: Response
    Vault_Core-->>Vault_API: Response
    Vault_API-->>User: Response
```

### Hands-On Labs

To gain practical experience with Vault, you can use the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs for learning web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

By following these labs, you can gain hands-on experience with Vault and other secrets management tools.

### Conclusion

Vault is a powerful secrets management tool that provides robust features for securely handling sensitive information. By understanding how Vault works and implementing best practices, you can significantly reduce the risk of exposure and misuse of secrets.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/How Vault works Vault Deep Dive Part 2/04-Introduction to Secrets Management|Introduction to Secrets Management]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/How Vault works Vault Deep Dive Part 2/00-Overview|Overview]] | [[06-Secrets Management with HashiCorp Vault Part 1|Secrets Management with HashiCorp Vault Part 1]]

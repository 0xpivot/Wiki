---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Secrets in Kubernetes

In Kubernetes, secrets are used to store sensitive information such as passwords, API keys, and other confidential data securely. This ensures that sensitive data is not exposed in plain text within the cluster. Instead, the values are encoded using Base64 encoding, which provides a level of obfuscation but does not provide strong encryption. The primary goal of using secrets is to manage sensitive data in a secure manner, ensuring that it is not easily accessible to unauthorized users.

### Why Use Secrets?

Using secrets in Kubernetes is crucial because it helps in maintaining the security of sensitive data. Storing sensitive information in plain text within configuration files or environment variables can lead to accidental exposure. By using secrets, you can ensure that sensitive data is stored securely and accessed only by authorized components.

### How Secrets Work

When you create a secret in Kubernetes, the sensitive data is encoded using Base64 encoding. This encoding process converts the plain text into a string of characters that are not easily readable. However, it is important to note that Base64 encoding is not a form of encryption; it merely obfuscates the data. Therefore, it is essential to handle secrets with care and ensure that they are not exposed in plain text.

#### Creating a Secret

To create a secret in Kubernetes, you need to follow these steps:

1. **Encode the Sensitive Data**: Before creating the secret, you need to encode the sensitive data using Base64 encoding. This can be done using the `echo` command in the terminal.

2. **Create the Secret Configuration File**: Once the data is encoded, you can create a configuration file (usually in YAML format) that defines the secret.

3. **Apply the Secret Configuration**: Finally, you apply the secret configuration to the Kubernetes cluster using the `kubectl apply` command.

Let's walk through these steps in detail.

### Encoding Sensitive Data Using Base64

The first step in creating a secret is to encode the sensitive data using Base64 encoding. This can be done using the `echo` command in the terminal. Here’s how you can do it:

```sh
echo -n "username" | base64
```

The `-n` option in the `echo` command is very important. It prevents `echo` from appending a newline character at the end of the input string. Without this option, the output will include an extra newline character, which can cause issues when decoding the data later.

For example, if you run the above command, the output will be:

```
dXNlcm5hbWU=
```

This is the Base64 encoded representation of the string "username".

Similarly, you can encode the password:

```sh
echo -n "password" | base64
```

The output will be:

```
cGFzc3dvcmQ=
```

### Creating the Secret Configuration File

Once you have the encoded values, you can create a secret configuration file. This file is usually in YAML format and defines the secret along with its metadata.

Here is an example of a secret configuration file (`mongo-secret.yaml`):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mongo-secret
type: Opaque
data:
  username: dXNlcm5hbWU=  # Base64 encoded username
  password: cGFzc3dwcmQ=  # Base64 encoded password
```

In this configuration file:

- `apiVersion: v1` specifies the API version.
- `kind: Secret` indicates that this is a secret resource.
- `metadata.name: mongo-secret` sets the name of the secret.
- `type: Opaque` specifies the type of secret. `Opaque` is the default type and is used for arbitrary data.
- `data` contains the key-value pairs of the secret. Each value is the Base64 encoded string of the corresponding sensitive data.

### Applying the Secret Configuration

After creating the secret configuration file, you can apply it to the Kubernetes cluster using the `kubectl apply` command:

```sh
kubectl apply -f mongo-secret.yaml
```

This command creates the secret in the cluster. You can verify the creation of the secret using the following command:

```sh
kubectl get secrets
```

This will list all the secrets in the current namespace, including the one you just created.

### Order of Creation Matters

It is important to note that the order of creation matters when dealing with secrets and deployments. If a deployment references a secret that does not exist yet, Kubernetes will return an error and the deployment will fail to start.

Therefore, you should always create the secret before creating the deployment that references it. Here is a sequence of commands to illustrate this:

1. Create the secret:

    ```sh
    kubectl apply -f mongo-secret.yaml
    ```

2. Create the deployment:

    ```sh
    kubectl apply -f deployment.yaml
    ```

### Example Deployment Configuration

Here is an example of a deployment configuration (`deployment.yaml`) that references the secret:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:latest
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            secretKeyRef:
              name: mongo-secret
              key: username
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mongo-secret
              key: password
```

In this deployment configuration:

- `apiVersion: apps/v1` specifies the API version.
- `kind: Deployment` indicates that this is a deployment resource.
- `metadata.name: mongodb-deployment` sets the name of the deployment.
- `spec.replicas: 1` specifies the number of replicas.
- `spec.template.spec.containers` defines the container specifications.
- `env` defines the environment variables for the container.
- `valueFrom.secretKeyRef` references the secret and the specific key within the secret.

### Pitfalls and Best Practices

While using secrets in Kubernetes is a good practice, there are some pitfalls and best practices to keep in mind:

1. **Do Not Store Plain Text Secrets**: Always encode sensitive data using Base64 encoding before storing it in a secret.
2. **Use Strong Passwords**: Ensure that the passwords used are strong and complex.
3. **Limit Access to Secrets**: Only grant access to secrets to the necessary components and users.
4. **Regularly Rotate Secrets**: Regularly rotate secrets to minimize the risk of exposure.
5. **Monitor Secret Usage**: Monitor the usage of secrets to detect any unauthorized access.

### Real-World Examples

There have been several real-world examples where mismanagement of secrets led to security breaches. One notable example is the 2019 breach of the Docker Hub, where an attacker gained access to Docker's internal systems due to the exposure of sensitive credentials.

### How to Prevent / Defend

To prevent and defend against potential vulnerabilities related to secrets in Kubernetes, follow these steps:

1. **Securely Encode Secrets**: Always encode sensitive data using Base64 encoding before storing it in a secret.
2. **Use Strong Authentication Mechanisms**: Implement strong authentication mechanisms to limit access to secrets.
3. **Regularly Audit Secrets**: Regularly audit the usage of secrets to detect any unauthorized access.
4. **Implement RBAC Policies**: Implement Role-Based Access Control (RBAC) policies to restrict access to secrets.
5. **Use Encryption at Rest**: Consider using encryption at rest for sensitive data stored in secrets.

### Secure Code Fix

Here is an example of a vulnerable configuration and the corresponding secure configuration:

**Vulnerable Configuration**:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mongo-secret
type: Opaque
data:
  username: username  # Plain text username
  password: password  # Plain text password
```

**Secure Configuration**:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mongo-secret
type: Opaque
data:
  username: dXNlcm5hbWU=  # Base64 encoded username
  password: cGFzc3dwcmQ=  # Base64 encoded password
```

### Conclusion

Using secrets in Kubernetes is a crucial aspect of managing sensitive data securely. By following the steps outlined in this chapter, you can ensure that sensitive data is stored and accessed securely within your Kubernetes cluster. Remember to always encode sensitive data using Base64 encoding, limit access to secrets, and regularly audit their usage to maintain the security of your cluster.

### Practice Labs

To gain hands-on experience with deploying MongoDB and MongoExpress in Kubernetes, you can use the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security concepts.
- **OWASP WrongSecrets**: A set of challenges to learn about secrets management in Kubernetes.

These labs will help you understand and practice the concepts covered in this chapter.

---
<!-- nav -->
[[05-Introduction to MongoDB and MongoExpress Deployment in Kubernetes|Introduction to MongoDB and MongoExpress Deployment in Kubernetes]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/15-Deploying MongoDB and MongoExpress in Kubernetes/00-Overview|Overview]] | [[07-Deploying MongoDB and MongoExpress in Kubernetes|Deploying MongoDB and MongoExpress in Kubernetes]]

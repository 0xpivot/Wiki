---
course: DevSecOps
topic: EKS Blueprints
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Why does the access token expire in Kubernetes when using AWS EKS?**

The access token expires in Kubernetes when using AWS EKS because the token is temporary and has a limited lifespan. When you assume a role to access the EKS cluster, the token generated for that role is only valid for a certain period. Once the token expires, you must re-assume the role to obtain a new token, which allows you to regain access to the cluster. This mechanism ensures that access to the cluster remains secure by limiting the duration of active sessions.

**Q2. How would you handle access token expiration when working with Kubernetes and AWS EKS?**

Handling access token expiration involves automating the process of refreshing the token. You can achieve this by setting up a script or a CI/CD pipeline that periodically assumes the necessary IAM role and updates the kubeconfig file. Here’s a basic example of how you might refresh the token:

```bash
#!/bin/bash

# Assume the IAM role
aws sts assume-role --role-arn arn:aws:iam::123456789012:role/MyRole --role-session-name MySession > /tmp/credentials.json

# Extract credentials from the JSON output
export AWS_ACCESS_KEY_ID=$(cat /tmp/credentials.json | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(cat /tmp/credentials.json | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(cat /tmp/credentials.json | jq -r '.Credentials.SessionToken')

# Update kubeconfig
aws eks update-kubeconfig --name my-cluster --region us-west-2
```

This script assumes the role, extracts the credentials, and updates the kubeconfig file, ensuring that you can continue to interact with the EKS cluster without manual intervention.

**Q3. What recent real-world examples illustrate the importance of handling access token expiration correctly?**

One notable example is the incident involving a misconfigured S3 bucket that exposed sensitive data, including access tokens. In 2021, a breach at a major cloud service provider led to the exposure of access tokens due to improper handling and expiration policies. The breach occurred because the tokens were not properly rotated and expired, leading to unauthorized access to resources. Properly managing and rotating access tokens can prevent such breaches.

**Q4. Explain how the `kubeconfig` file interacts with AWS EKS to manage access tokens.**

The `kubeconfig` file is used by `kubectl` to store information about how to communicate with a Kubernetes cluster. When using AWS EKS, the `kubeconfig` file includes details specific to EKS, such as the cluster endpoint and the authentication method. For EKS, the authentication method typically involves an IAM Authenticator that validates the user's credentials against AWS.

When you assume an IAM role to access the EKS cluster, the `kubeconfig` file is updated to include the necessary credentials. These credentials are used by the IAM Authenticator to validate requests to the EKS API server. If the token in the `kubeconfig` file expires, the IAM Authenticator will fail to authenticate the user, resulting in unauthorized access errors. To resolve this, you must refresh the token and update the `kubeconfig` file accordingly.

**Q5. How would you automate the process of refreshing access tokens for a Kubernetes cluster in AWS EKS?**

Automating the process of refreshing access tokens for a Kubernetes cluster in AWS EKS can be achieved by integrating the token refresh logic into a CI/CD pipeline or a scheduled task. Here’s an example using a Jenkins pipeline:

```groovy
pipeline {
    agent any
    stages {
        stage('Refresh Token') {
            steps {
                script {
                    // Assume the IAM role
                    sh 'aws sts assume-role --role-arn arn:aws:iam::123456789012:role/MyRole --role-session-name MySession > /tmp/credentials.json'
                    
                    // Extract credentials from the JSON output
                    sh 'export AWS_ACCESS_KEY_ID=$(cat /tmp/credentials.json | jq -r \'.Credentials.AccessKeyId\')'
                    sh 'export AWS_SECRET_ACCESS_KEY=$(cat /tmp/credentials.json | jq -r \'.Credentials.SecretAccessKey\')'
                    sh 'export AWS_SESSION_TOKEN=$(cat /tmp/credentials.json | jq -r \'.Credentials.SessionToken\')'
                    
                    // Update kubeconfig
                    sh 'aws eks update-kubeconfig --name my-cluster --region us-west-2'
                }
            }
        }
    }
}
```

In this Jenkins pipeline, the `assume-role` command is run to refresh the token, and the `kubeconfig` file is updated to reflect the new credentials. This ensures that the pipeline can continue to interact with the EKS cluster without manual intervention.

---
<!-- nav -->
[[02-Understanding Temporary Access Tokens in EKS Blueprints|Understanding Temporary Access Tokens in EKS Blueprints]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/02-EKS Blueprints/03-Access Token Expiration/00-Overview|Overview]]

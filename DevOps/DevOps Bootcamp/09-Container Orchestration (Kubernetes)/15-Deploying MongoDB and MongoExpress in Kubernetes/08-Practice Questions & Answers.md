---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of creating an internal service for MongoDB in a Kubernetes cluster.**

The purpose of creating an internal service for MongoDB in a Kubernetes cluster is to provide a stable network identity for the MongoDB pods. This service allows other components within the same cluster to communicate with the MongoDB pods without needing to know their specific IP addresses, which can change over time due to pod restarts or scaling operations. By using a service, the application (such as MongoExpress) can consistently connect to the database using a fixed DNS name and port, ensuring reliable communication within the cluster.

**Q2. How would you configure the `MongoDB` deployment to use environment variables for the root username and password?**

To configure the `MongoDB` deployment to use environment variables for the root username and password, you would modify the deployment configuration file as follows:

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
        image: mongo
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: mongo-root-username
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: mongo-root-password
```

Here, `valueFrom.secretKeyRef` is used to reference the values stored in a Kubernetes secret named `mongodb-secret`.

**Q3. Why is it important to use a secret for storing sensitive information like database credentials in Kubernetes?**

Using a secret in Kubernetes for storing sensitive information like database credentials is crucial for several reasons:
1. **Security**: Secrets are encrypted at rest and in transit, providing an additional layer of security compared to storing credentials in plain text within configuration files.
2. **Isolation**: Secrets are stored separately from the application configuration files, reducing the risk of accidental exposure via version control systems or unauthorized access.
3. **Flexibility**: Secrets can be easily rotated or updated without changing the application configuration, enhancing security management practices.
4. **Compliance**: Using secrets aligns with best practices and compliance standards for handling sensitive data.

**Q4. How would you create a config map to store the MongoDB server address for use by the MongoExpress deployment?**

To create a config map to store the MongoDB server address for use by the MongoExpress deployment, you would follow these steps:

1. Create a config map file (`mongo-configmap.yaml`):

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mongo-configmap
data:
  MONGODB_SERVER: "mongodb-service"
```

2. Apply the config map to the cluster:

```bash
kubectl apply -f mongo-configmap.yaml
```

3. Reference the config map in the MongoExpress deployment:

```yaml
env:
- name: MONGODB_SERVER
  valueFrom:
    configMapKeyRef:
      name: mongo-configmap
      key: MONGODB_SERVER
```

This ensures that the MongoDB server address is centrally managed and can be easily updated across multiple deployments.

**Q5. Explain the role of an external service in allowing external access to the MongoExpress application.**

An external service in Kubernetes is used to expose an application to external networks. For the MongoExpress application, an external service is necessary to allow users to access the application from outside the Kubernetes cluster. This is achieved by configuring the service with a `type: LoadBalancer`, which assigns an external IP address to the service. Users can then access the application by navigating to the assigned external IP address and port in their browser.

For example, the configuration for an external service for MongoExpress might look like this:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mongoexpress-service
spec:
  type: LoadBalancer
  ports:
  - port: 8081
    targetPort: 8081
    nodePort: 30000
  selector:
    app: mongoexpress
```

This configuration creates a load balancer that forwards traffic from the external IP address and port to the internal pods running the MongoExpress application.

**Q6. How would you troubleshoot a scenario where the MongoExpress application fails to connect to the MongoDB database?**

To troubleshoot a scenario where the MongoExpress application fails to connect to the MongoDB database, you can follow these steps:

1. **Check the Logs**: Examine the logs of both the MongoExpress and MongoDB pods to identify any errors or warnings that may indicate the cause of the failure.

   ```bash
   kubectl logs <mongoexpress-pod-name>
   kubectl logs <mongodb-pod-name>
   ```

2. **Verify Connectivity**: Ensure that the MongoExpress pod can reach the MongoDB service. Use `kubectl exec` to run a network diagnostic tool such as `curl` or `ping` from the MongoExpress pod to the MongoDB service.

   ```bash
   kubectl exec -it <mongoexpress-pod-name> -- curl http://mongodb-service:27017
   ```

3. **Check Configuration**: Verify that the environment variables for the MongoDB server address, username, and password are correctly set in the MongoExpress deployment configuration.

4. **Inspect Services and Pods**: Confirm that the services and pods are running correctly and that the selectors and labels match between the services and deployments.

   ```bash
   kubectl get svc
   kubectl get pods
   ```

5. **Review Secrets and Config Maps**: Ensure that the secrets and config maps containing sensitive information are correctly referenced and that the values are properly encoded and accessible.

By systematically checking each component, you can identify and resolve the issue preventing the MongoExpress application from connecting to the MongoDB database.

---
<!-- nav -->
[[07-Deploying MongoDB and MongoExpress in Kubernetes|Deploying MongoDB and MongoExpress in Kubernetes]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/15-Deploying MongoDB and MongoExpress in Kubernetes/00-Overview|Overview]]

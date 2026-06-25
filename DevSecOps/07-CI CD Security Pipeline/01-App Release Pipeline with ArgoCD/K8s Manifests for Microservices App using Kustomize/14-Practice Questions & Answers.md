---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain how Kustomize helps in managing Kubernetes manifests for a microservices application.**

Kustomize is a tool that helps manage and organize Kubernetes manifests by allowing users to create reusable configurations and customize them for different environments. Here’s how Kustomize helps:

1. **Layered Configuration**: Kustomize allows you to build layers of configuration. You can have a base layer that contains the core Kubernetes manifest files, and then additional layers (overlays) that modify or extend the base configuration for specific environments such as development or production.

2. **Environment Customization**: Different overlays can be created for different environments. For instance, a `dev` overlay might include settings for local testing, while a `prod` overlay might include settings for a production environment. This ensures that the same base configuration can be customized for different purposes without duplicating code.

3. **Parameterization**: Kustomize supports parameterization, allowing you to define variables in a `kustomization.yaml` file and reference them in your manifests. This makes it easy to update values like image tags, resource limits, or environment-specific settings without modifying the underlying manifests.

4. **Reusability**: By separating concerns into base and overlay configurations, Kustomize promotes reusability. Common configurations can be reused across multiple applications or environments, reducing redundancy and improving maintainability.

5. **GitOps Integration**: Kustomize integrates well with GitOps workflows. Changes to the configuration can be version-controlled in a Git repository, and tools like Argo CD can automatically detect and apply these changes to the Kubernetes cluster.

**Q2. How does the use of Kustomize simplify the process of updating image tags in a microservices application?**

Using Kustomize simplifies the process of updating image tags in a microservices application by providing a centralized and parameterized approach to managing these updates. Here’s how it works:

1. **Centralized Management**: Instead of hardcoding image tags in each Kubernetes manifest file, you can define a placeholder for the image name and tag in the base manifest. Then, in the `kustomization.yaml` file, you can specify the actual image name and tag.

2. **Parameterization**: Kustomize allows you to define parameters in the `kustomization.yaml` file. These parameters can be referenced in the manifests using the `${PARAM_NAME}` syntax. When you update the parameter in the `kustomization.yaml` file, all references to that parameter in the manifests will be updated accordingly.

3. **Automation**: In a CI/CD pipeline, you can automate the process of updating the image tags. For example, after building a new Docker image, the pipeline can update the `kustomization.yaml` file with the new image tag. Then, a tool like Argo CD can automatically detect these changes and apply them to the Kubernetes cluster.

Here’s an example of how this might look in practice:

```yaml
# base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  template:
    spec:
      containers:
      - name: my-service
        image: ${IMAGE_NAME}:${IMAGE_TAG}
```

```yaml
# kustomization.yaml
resources:
- deployment.yaml
images:
- name: IMAGE_NAME
  newName: gcr.io/my-project/my-service
  newTag: latest
```

In this example, the `deployment.yaml` file uses placeholders for the image name and tag. The `kustomization.yaml` file specifies the actual values for these placeholders. When you update the `newTag` value in the `kustomization.yaml` file, the image tag in the `deployment.yaml` file will be updated accordingly.

**Q3. Describe how the Ingress component is used to expose the frontend service in a Kubernetes cluster running on AWS EKS.**

The Ingress component is used to expose the frontend service in a Kubernetes cluster running on AWS EKS by creating an external load balancer that routes traffic to the frontend service. Here’s how it works:

1. **Ingress Definition**: An Ingress resource is defined in the Kubernetes manifest files. This resource specifies the rules for routing external traffic to the appropriate backend services within the cluster.

2. **Annotations for AWS Load Balancer**: In the Ingress definition, you can use annotations to specify that the Ingress should be backed by an AWS Application Load Balancer. For example:

   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: frontend-ingress
     annotations:
       kubernetes.io/ingress.class: "alb"
       alb.ingress.kubernetes.io/scheme: "internet-facing"
   spec:
     rules:
     - host: frontend.example.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: frontend-service
               port:
                 number: 80
   ```

3. **Load Balancer Creation**: When the Ingress resource is applied to the cluster, the AWS Application Load Balancer is automatically created and configured to route traffic to the frontend service. The load balancer is created with an internet-facing scheme, meaning it is publicly accessible.

4. **Traffic Routing**: The load balancer forwards incoming traffic to the frontend service based on the rules defined in the Ingress resource. The frontend service is typically an internal Kubernetes service that is not directly exposed to the internet.

5. **DNS Configuration**: To access the frontend service, you can use the DNS name of the load balancer. This DNS name can be mapped to a custom domain name using DNS records.

By using the Ingress component in this way, you can easily expose the frontend service to the internet while keeping the internal services private. This setup provides a scalable and manageable way to handle external traffic in a Kubernetes cluster running on AWS EKS.

**Q4. How does Argo CD detect and apply changes made to the GitOps repository containing Kustomize configurations?**

Argo CD detects and applies changes made to the GitOps repository containing Kustomize configurations through a continuous synchronization process. Here’s how it works:

1. **Repository Sync**: Argo CD continuously monitors the GitOps repository for changes. When changes are detected, Argo CD fetches the latest version of the repository and compares it with the current state of the cluster.

2. **Resource Comparison**: Argo CD compares the desired state of the cluster (as defined in the GitOps repository) with the actual state of the cluster. This comparison identifies any differences between the two states.

3. **Sync Operation**: If differences are found, Argo CD performs a sync operation to bring the actual state of the cluster in line with the desired state. This involves applying the necessary changes to the cluster, such as deploying new resources, updating existing resources, or removing obsolete resources.

4. **Kustomize Integration**: When using Kustomize, Argo CD can automatically handle the layered configuration and parameterization provided by Kustomize. Argo CD can detect changes in the `kustomization.yaml` files and apply the corresponding changes to the cluster.

5. **Automatic Updates**: In a typical GitOps workflow, changes to the GitOps repository are pushed via a CI/CD pipeline. Once the changes are pushed, Argo CD automatically detects these changes and applies them to the cluster. This ensures that the cluster is always in sync with the desired state defined in the GitOps repository.

6. **Health Checks**: After applying the changes, Argo CD performs health checks to ensure that the new state of the cluster is stable and functional. If any issues are detected, Argo CD can roll back the changes or notify the operators to take corrective action.

By automating this process, Argo CD ensures that the cluster remains in a consistent and desired state, reducing the risk of manual errors and improving the overall reliability of the system.

**Q5. What are the benefits of using overlays in Kustomize for managing different environments in a microservices application?**

Using overlays in Kustomize for managing different environments in a microservices application offers several benefits:

1. **Environment-Specific Customizations**: Overlays allow you to define environment-specific customizations without modifying the base configuration. For example, you can have a `dev` overlay that includes settings for local testing and a `prod` overlay that includes settings for a production environment.

2. **Reduced Redundancy**: By separating concerns into base and overlay configurations, you can avoid duplicating code. The base configuration contains the core Kubernetes manifest files, while the overlays contain the environment-specific modifications. This reduces redundancy and improves maintainability.

3. **Easy Scaling**: Overlays make it easy to scale your application to multiple environments. You can create new overlays for additional environments without affecting the base configuration. This allows you to manage different environments consistently and efficiently.

4. **Parameterization**: Overlays support parameterization, allowing you to define variables in the `kustomization.yaml` file and reference them in your manifests. This makes it easy to update values like image tags, resource limits, or environment-specific settings without modifying the underlying manifests.

5. **Consistent Configuration Management**: Overlays provide a consistent way to manage configurations across different environments. This ensures that the same base configuration can be customized for different purposes without duplicating code.

Here’s an example of how overlays might be used in practice:

```yaml
# base/kustomization.yaml
resources:
- deployment.yaml
- service.yaml
```

```yaml
# overlays/dev/kustomization.yaml
resources:
- ../../base
patchesStrategicMerge:
- dev-patch.yaml
```

```yaml
# overlays/prod/kustomization.yaml
resources:
- ../../base
patchesStrategicMerge:
- prod-patch.yaml
```

In this example, the `base` directory contains the core Kubernetes manifest files, while the `overlays` directory contains environment-specific overlays. The `dev` and `prod` overlays include patches that modify the base configuration for their respective environments.

**Q6. How can you use Kustomize to manage secrets and sensitive data in a microservices application?**

Using Kustomize to manage secrets and sensitive data in a microservices application requires careful handling to ensure security and compliance. Here’s how you can do it:

1. **External Secret Management**: Store sensitive data, such as passwords, API keys, and certificates, in an external secret management solution like HashiCorp Vault, AWS Secrets Manager, or Kubernetes Secrets. This keeps sensitive data out of your GitOps repository and ensures that it is properly secured.

2. **Parameterization**: Use Kustomize to parameterize sensitive data in your manifests. Define placeholders for sensitive data in the base configuration and specify the actual values in the `kustomization.yaml` file. For example:

   ```yaml
   # base/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my-service
   spec:
     template:
       spec:
         containers:
         - name: my-service
           env:
           - name: DATABASE_PASSWORD
             valueFrom:
               secretKeyRef:
                 name: db-secret
                 key: password
   ```

   ```yaml
   # overlays/dev/kustomization.yaml
   resources:
   - ../../base
   patchesStrategicMerge:
   - dev-patch.yaml
   ```

   ```yaml
   # overlays/prod/kustomization.yaml
   resources:
   - ../../base
   patchesStrategicMerge:
   - prod-patch.yaml
   ```

3. **Secret References**: Use Kubernetes Secrets to store sensitive data and reference them in your manifests. This ensures that sensitive data is stored securely and can be managed independently of your application configuration.

4. **Environment-Specific Secrets**: Use overlays to manage environment-specific secrets. For example, you can have a `dev` overlay that references a development secret and a `prod` overlay that references a production secret.

5. **CI/CD Integration**: Integrate your CI/CD pipeline with your secret management solution to automatically inject secrets into your manifests during the build and deployment process. This ensures that sensitive data is handled securely and consistently across different environments.

By following these best practices, you can use Kustomize to manage secrets and sensitive data in a secure and efficient manner, ensuring that your microservices application remains compliant and secure.

**Q7. How can you use Kustomize to manage resource requests and limits for a microservices application?**

Using Kustomize to manage resource requests and limits for a microservices application allows you to define and customize resource constraints for different environments. Here’s how you can do it:

1. **Base Configuration**: Define the default resource requests and limits in the base configuration. For example:

   ```yaml
   # base/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my-service
   spec:
     template:
       spec:
         containers:
         - name: my-service
           resources:
             requests:
               cpu: 100m
               memory: 128Mi
             limits:
               cpu: 200m
               memory: 256Mi
   ```

2. **Overlay Customization**: Use overlays to customize resource requests and limits for different environments. For example:

   ```yaml
   # overlays/dev/kustomization.yaml
   resources:
   - ../../base
   patchesStrategicMerge:
   - dev-patch.yaml
   ```

   ```yaml
   # overlays/prod/kustomization.yaml
   resources:
   - ../../base
   patchesStrategicMerge:
   - prod-patch.yaml
   ```

3. **Patch Files**: Create patch files to modify the resource requests and limits in the overlays. For example:

   ```yaml
   # overlays/dev/dev-patch.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my-service
   spec:
     template:
       spec:
         containers:
         - name: my-service
           resources:
             requests:
               cpu: 50m
               memory: 64Mi
             limits:
               cpu: 100m
               memory: 128Mi
   ```

   ```yaml
   # overlays/prod/prod-patch.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my
     spec:
       template:
         spec:
           containers:
           - name: my-service
             resources:
               requests:
                 cpu: 200m
                 memory: 256Mi
               limits:
                 cpu: 400m
                 memory: 512Mi
   ```

4. **Parameterization**: Use Kustomize parameters to define resource requests and limits in the `kustomization.yaml` file. For example:

   ```yaml
   # overlays/dev/kustomization.yaml
   resources:
   - ../../base
   params:
   - name: CPU_REQUEST
     value: 50m
   - name: MEMORY_REQUEST
     value: 64Mi
   - name: CPU_LIMIT
     value: 100m
   - name: MEMORY_LIMIT
     value: 128Mi
   ```

   ```yaml
   # overlays/prod/kustomization.yaml
   resources:
   - ../../base
   params:
   - name: CPU_REQUEST
     value: 200m
   - name: MEMORY_REQUEST
     value: 256Mi
   - name: CPU_LIMIT
     value: 400m
   - name: MEMORY_LIMIT
     value: 1024Mi
   ```

5. **Manifest References**: Reference the Kustomize parameters in the base manifest. For example:

   ```yaml
   # base/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my-service
   spec:
     template:
       spec:
         containers:
         - name: my-service
           resources:
             requests:
               cpu: ${CPU_REQUEST}
               memory: ${MEMORY_REQUEST}
             limits:
               cpu: ${CPU_LIMIT}
               memory: ${MEMORY_LIMIT}
   ```

By using Kustomize in this way, you can easily manage resource requests and limits for different environments, ensuring that your microservices application is optimized for performance and resource utilization.

**Q8. How can you use Kustomize to manage environment-specific configurations for a microservices application?**

Using Kustomize to manage environment-specific configurations for a microservices application allows you to define and customize settings for different environments. Here’s how you can do it:

1. **Base Configuration**: Define the default configurations in the base configuration. For example:

   ```yaml
   # base/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my-service
   spec:
     template:
       spec:
         containers:
         - name: my-service
           env:
           - name: ENVIRONMENT
             value: "default"
           - name: DATABASE_URL
             value: "localhost:5432"
   ```

2. **Overlay Customization**: Use overlays to customize configurations for different environments. For example:

   ```yaml
   # overlays/dev/kustomization.yaml
   resources:
   - ../../base
   patchesStrategicMerge:
   - dev-patch.yaml
   ```

   ```yaml
   # overlays/prod/kustomization.yaml
   resources:
   - ../../base
   patchesStrategicMerge:
   - prod-patch.yaml
   ```

3. **Patch Files**: Create patch files to modify the configurations in the overlays. For example:

   ```yaml
   # overlays/dev/dev-patch.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my-service
   spec:
     template:
       spec:
         containers:
         - name: my-service
           env:
           - name: ENVIRONMENT
             value: "development"
           - name: DATABASE_URL
             value: "dev-database.example.com:5432"
   ```

   ```yaml
   # overlays/prod/prod-patch.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my-service
   spec:
     template:
       spec:
         containers:
         - name: my-service
           env:
           - name: ENVIRONMENT
             value: "production"
           - name: DATABASE_URL
             value: "prod-database.example.com:5432"
   ```

4. **Parameterization**: Use Kustomize parameters to define configurations in the `kustomization.yaml` file. For example:

   ```yaml
   # overlays/dev/kustomization.yaml
   resources:
   - ../../base
   params:
   - name: ENVIRONMENT
     value: "development"
   - name: DATABASE_URL
     value: "dev-database.example.com:5432"
   ```

   ```yaml
   # overlays/prod/kustomization.yaml
   resources:
   - ../../base
   params:
   - name: ENVIRONMENT
     value: "production"
   - name: DATABASE_URL
     value: "prod-database.example.com:5432"
   ```

5. **Manifest References**: Reference the Kustomize parameters in the base manifest. For example:

   ```yaml
   # base/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my-service
   spec:
     template:
       spec:
         containers:
         - name: my-service
           env:
           - name: ENVIRONMENT
             value: ${ENVIRONMENT}
           - name: DATABASE_URL
             value: ${DATABASE_URL}
   ```

By using Kustomize in this way, you can easily manage environment-specific configurations for different environments, ensuring that your microservices application is properly configured for each environment.

**Q9. How can you use Kustomize to manage different versions of microservices in a GitOps repository?**

Using Kustomize to manage different versions of microservices in a GitOps repository allows you to define and customize the versions for different environments. Here’s how you can do it:

1. **Base Configuration**: Define the default image versions in the base configuration. For example:

   ```yaml
   # base/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my-service
   spec:
     template:
       spec:
         containers:
         - name: my-service
           image: my-service:latest
   ```

2. **Overlay Customization**: Use overlays to customize image versions for different environments. For example:

   ```yaml
   # overlays/dev/kustomization.yaml
   resources:
   - ../../base
   images:
   - name: my-service
     newName: my-service
     newTag: 1.0.0
   ```

   ```yaml
   # overlays/prod/kustomization.yaml
   resources:
   - ../../base
   images:
   - name: my-service
     newName: my-service
     newTag: 2.0.0
   ```

3. **Parameterization**: Use Kustomize parameters to define image versions in the `kustomization.yaml` file. For example:

   ```yaml
   # overlays/dev/kustomization.yaml
   resources:
   - ../../base
   params:
   - name: IMAGE_VERSION
     value: 1.0.0
   ```

   ```yaml
   # overlays/prod/kustomization.yaml
   resources:
   - ../../base
   params:
   - name: IMAGE_VERSION
     value: 2.0.0
   ```

4. **Manifest References**: Reference the Kustomize parameters in the base manifest. For example:

   ```yaml
   # base/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my-service
   spec:
     template:
       spec:
         containers:
         - name: my-service
           image: my-service:${IMAGE_VERSION}
   ```

By using Kustomize in this way, you can easily manage different versions of microservices for different environments, ensuring that your microservices application is properly versioned and updated.

**Q10. How can you use Kustomize to manage different namespaces for a microservices application?**

Using Kustomize to manage different namespaces for a microservices application allows you to define and customize namespaces for different environments. Here’s how you can do it:

1. **Base Configuration**: Define the default namespace in the base configuration. For example:

   ```yaml
   # base/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my-service
     namespace: default
   spec:
     template:
       spec:
         containers:
         - name: my-service
           image: my-service:latest
   ```

2. **Overlay Customization**: Use overlays to customize namespaces for different environments. For example:

   ```yaml
   # overlays/dev/kustomization.yaml
   resources:
   - ../../base
   namespace: dev
   ```

   ```yaml
   # overlays/prod/kustomization.yaml
   resources:
   - ../../base
   namespace: prod
   ```

3. **Parameterization**: Use Kustomize parameters to define namespaces in the `kustomization.yaml` file. For example:

   ```yaml
   # overlays/dev/kustomization.yaml
   resources:
   - ../../base
   params:
   - name: NAMESPACE
     value: dev
   ```

   ```yaml
   # overlays/prod/kustomization.yaml
   resources:
   - ../../base
   params:
   - name: NAMESPACE
     value: prod
   ```

4. **Manifest References**: Reference the Kustomize parameters in the base manifest. For example:

   ```yaml
   # base/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my-service
     namespace: ${NAMESPACE}
   spec:
     template:
       spec:
         containers:
         - name: my-service
           image: my-service:latest
   ```

By using Kustomize in this way, you can easily manage different namespaces for a microservices application, ensuring that your microservices are properly isolated and organized.

---
<!-- nav -->
[[13-Setting Up the Project Structure|Setting Up the Project Structure]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/K8s Manifests for Microservices App using Kustomize/00-Overview|Overview]]

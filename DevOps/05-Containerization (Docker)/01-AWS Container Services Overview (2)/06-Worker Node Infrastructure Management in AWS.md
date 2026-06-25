---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Worker Node Infrastructure Management in AWS

When deploying containerized applications using ECS or EKS, one of the critical aspects is managing the worker nodes where the containers will run. AWS offers several options for worker node infrastructure management, each with its own level of complexity and automation.

### Self-Managed EC2 Instances

The first option is to use completely self-managed EC2 instances. In this scenario, you are responsible for provisioning, configuring, and maintaining the EC2 instances that will host your containers. This approach offers maximum control but requires significant effort and expertise to manage effectively.

#### Pros and Cons

**Pros:**
- Full control over the infrastructure.
- Customizable configurations to meet specific requirements.

**Cons:**
- High operational overhead.
- Requires deep knowledge of AWS and Kubernetes/ECS.

### Semi-Managed EC2 Instances via Node Groups

The second option is to use semi-managed EC2 instances through node groups. Node groups are a collection of EC2 instances that are managed as a unit. This approach simplifies the management of worker nodes by abstracting away some of the complexities involved in provisioning and maintaining individual instances.

#### How Node Groups Work

Node groups are particularly useful when working with EKS clusters. They allow you to group worker nodes into logical units, making it easier to manage and scale your cluster. Here’s a step-by-step overview of how node groups work:

1. **Create a Node Group**: Define the specifications for your node group, such as instance type, number of instances, and AMI.
2. **Provision Instances**: AWS provisions the specified number of EC2 instances based on the node group configuration.
3. **Join the Cluster**: The instances join the EKS cluster and become part of the worker node pool.
4. **Manage Nodes**: You can manage the node group as a whole, performing operations like scaling, updating, and monitoring.

#### Example Configuration

Here’s an example of how to create a node group using the AWS CLI:

```bash
aws eks create-nodegroup \
    --cluster-name my-cluster \
    --nodegroup-name my-node-group \
    --subnets subnet-12345678 subnet-87654321 \
    --instance-types t3.medium \
    --min-size 2 \
    --max-size 4 \
    --desired-size 3
```

This command creates a node group named `my-node-group` with 2 to 4 instances of type `t3.medium`, joining the `my-cluster` EKS cluster.

#### Auto-Scaling Considerations

While node groups simplify the management of worker nodes, they still require manual configuration for auto-scaling. Auto-scaling ensures that your cluster can dynamically adjust the number of worker nodes based on the workload.

To enable auto-scaling, you need to configure both Kubernetes and AWS:

1. **Kubernetes Autoscaler**: Set up a Horizontal Pod Autoscaler (HPA) to automatically scale the number of pods based on CPU or memory usage.
2. **AWS Autoscaling Group**: Configure an autoscaling group for the node group to automatically scale the number of EC2 instances.

#### Example Configuration

Here’s an example of how to set up an HPA in Kubernetes:

```yaml
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-autoscaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```

And here’s an example of how to configure an autoscaling group for the node group:

```bash
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name my-node-group-asg \
    --launch-template LaunchTemplateName=my-launch-template,Version=1 \
    --min-size 2 \
    --max-size 4 \
    --desired-capacity 3 \
    --vpc-zone-identifier subnet-12345678,subnet-87654321
```

### Fully Managed Worker Nodes with Fargate

The third option is to use fully managed worker nodes with Fargate. Fargate is a serverless compute engine for containers that allows you to run containers without having to manage the underlying infrastructure.

#### How Fargate Works

Fargate abstracts away the need to provision, configure, and maintain EC2 instances. Instead, you define tasks and services, and Fargate manages the execution environment for you. This approach significantly reduces the operational overhead associated with managing worker nodes.

#### Example Configuration

Here’s an example of how to run a task using Fargate in ECS:

```json
{
  "family": "my-task",
  "containerDefinitions": [
    {
      "name": "my-container",
      "image": "my-docker-image:latest",
      "cpu": 256,
      "memory": 512,
      "essential": true
    }
  ],
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512"
}
```

And here’s an example of how to run a pod using Fargate in EKS:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: my-job
spec:
  template:
    spec:
      containers:
      - name: my-container
        image: my-docker-image:latest
        resources:
          limits:
            cpu: "256m"
            memory: "512Mi"
          requests:
            cpu: "256m"
            memory: "512Mi"
      restartPolicy: Never
  backoffLimit: 4
```

### Combining EC2 and Fargate

You can also combine EC2 and Fargate within the same EKS cluster. This hybrid approach allows you to leverage the benefits of both managed and unmanaged worker nodes, depending on your specific needs.

#### Example Configuration

Here’s an example of how to create an EKS cluster with both EC2 and Fargate:

```bash
aws eks create-cluster \
    --name my-cluster \
    --role-arn arn:aws:iam::123456789012:role/eksClusterRole \
    --resources-vpc-config subnetIds=subnet-12345678,subnet-87654321 \
    --enabled-cluster-log-types ALL \
    --tags key=value
```

Then, create a node group and a Fargate profile:

```bash
aws eks create-nodegroup \
    --cluster-name my-cluster \
    --nodegroup-name my-node-group \
    --subnets subnet-12345678 subnet-87654321 \
    --instance-types t3.medium \
    --min-size 2 \
    --max-size  4 \
    --desired-size 3

aws eks create-fargate-profile \
    --cluster-name my-cluster \
    --profile-name my-fargate-profile \
    --pod-execution-role-arn arn:aws:iam::123456789012:role/fargatePodExecutionRole \
    --selectors namespace=my-namespace
```

### Comparison with ECS

Whether you use ECS or EKS, the principles of worker node infrastructure management remain similar. Both services offer options for self-managed, semi-managed, and fully managed worker nodes, allowing you to choose the level of control and automation that best suits your needs.

#### Example Configuration

Here’s an example of how to create a task definition in ECS:

```json
{
  "family": "my-task",
  "containerDefinitions": [
    {
      "name": "my-container",
      "image": "my-docker-image:latest",
      "cpu": 256,
      "memory": 512,
      "essential": true
    }
  ],
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["EC2", "FARGATE"],
  "cpu": "256",
  "memory": "512"
}
```

And here’s an example of how to create a service in ECS:

```json
{
  "cluster": "my-cluster",
  "serviceName": "my-service",
  "taskDefinition": "my-task:1",
  "desiredCount": 2,
  "launchType": "FARGATE",
  "networkConfiguration": {
    "awsvpcConfiguration": {
      "subnets": ["subnet-12345678", "subnet-87654321"],
      "securityGroups": ["sg-12345678"],
      "assignPublicIp": "ENABLED"
    }
  },
  "platformVersion": "LATEST"
}
```

### Common Pitfalls and Best Practices

#### Pitfall: Over-Provisioning Resources

One common pitfall is over-provisioning resources, which can lead to unnecessary costs and inefficiencies. To avoid this, ensure that your resource requests and limits are accurately defined based on actual usage patterns.

#### Best Practice: Monitoring and Logging

Monitoring and logging are crucial for maintaining the health and performance of your containerized applications. Use tools like Amazon CloudWatch, Prometheus, and Grafana to monitor your cluster and applications.

#### Example Configuration

Here’s an example of how to set up CloudWatch logging for an ECS task:

```json
{
  "family": "my-task",
  "containerDefinitions": [
    {
      "name": "my-container",
      "image": "my-docker-image:latest",
      "cpu": 256,
      "memory": 512,
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/my-task",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["EC2", "FARGATE"],
  "cpu": "256",
  "memory": "512"
}
```

### How to Prevent / Defend

#### Detection

Regularly monitor your cluster and applications for anomalies and potential issues. Use tools like AWS CloudTrail, Amazon GuardDuty, and Kubernetes audit logs to detect unauthorized access and suspicious activities.

#### Prevention

Implement proper security measures to protect your cluster and applications. Use IAM roles and policies to restrict access, enable encryption for sensitive data, and regularly update your software and dependencies.

#### Secure-Coding Fixes

Here’s an example of how to securely configure an IAM role for an ECS task:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

And here’s an example of how to securely configure an IAM role for an EKS pod:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: my-namespace
  name: my-pod-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: my-namespace
  name: my-pod-rolebinding
subjects:
- kind: ServiceAccount
  name: my-pod-sa
roleRef:
  kind: Role
  name: my-pod-role
  apiGroup: rbac.authorization.k8s.io
```

### Conclusion

Managing worker node infrastructure in AWS is a critical aspect of deploying and maintaining containerized applications. By understanding the different options available—self-managed EC2 instances, semi-managed EC2 instances via node groups, and fully managed worker nodes with Fargate—you can choose the approach that best meets your needs and preferences. Whether you use ECS or EKS, the principles remain the same, and by following best practices and implementing proper security measures, you can ensure the health and performance of your containerized applications.

### Practice Labs

For hands-on experience with AWS container services, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes sections on container security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for security training.
- **WebGoat**: An interactive web application security training tool.
- **CloudGoat**: A series of labs designed to help you learn AWS security best practices.
- **flaws.cloud**: A cloud-native security training platform.
- **flaws2.cloud**: Another cloud-native security training platform.
- **AWS Official Workshops**: Provides comprehensive guides and labs for various AWS services.
- **Pacu**: A Python framework for AWS security assessments.
- **Kubernetes Goat**: A series of labs designed to help you learn Kubernetes security best practices.
- **OWASP WrongSecrets**: A series of challenges to test your knowledge of secure coding practices.
- **kube-hunter**: A tool for hunting vulnerabilities in Kubernetes clusters.

These labs provide practical experience and reinforce the concepts covered in this chapter.

---
<!-- nav -->
[[06-Introduction to Container Orchestration|Introduction to Container Orchestration]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/01-AWS Container Services Overview (2)/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/01-AWS Container Services Overview (2)/08-Practice Questions & Answers|Practice Questions & Answers]]

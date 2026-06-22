---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Deploying Applications in Kubernetes

In the context of modern DevOps practices, deploying applications to a Kubernetes cluster is a fundamental task. This process involves several steps, including setting up a Continuous Integration and Continuous Deployment (CI/CD) pipeline, building Docker images, and deploying these images to a Kubernetes cluster. This chapter will cover the entire process, starting from the basics of setting up a CI/CD pipeline to deploying a Node.js application in Kubernetes using Prometheus client libraries for monitoring.

### Setting Up a CI/CD Pipeline

A CI/CD pipeline automates the process of building, testing, and deploying applications. This ensures that changes are integrated frequently and reliably. A typical CI/CD pipeline includes the following stages:

1. **Source Control**: Code is stored in a version control system like Git.
2. **Build**: The code is compiled and built into a deployable artifact.
3. **Test**: Automated tests are run to ensure the code works as expected.
4. **Deploy**: The artifact is deployed to a staging or production environment.
5. **Monitor**: The deployed application is monitored for performance and errors.

#### Example: GitHub Actions

GitHub Actions is a popular CI/CD platform that integrates seamlessly with GitHub repositories. Here’s an example of a simple GitHub Actions workflow for a Node.js application:

```yaml
name: Node.js CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [14.x, 16.x]

    steps:
    - uses: actions/checkout@v3
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
    - run: npm ci
    - run: npm test
```

This workflow triggers on pushes to the `main` branch and runs tests for different Node.js versions.

### Building Docker Images

Once the application is tested and ready, it needs to be packaged into a Docker image. Docker simplifies the deployment process by providing a consistent environment across different systems.

#### Example: Dockerfile for a Node.js Application

Here’s a sample `Dockerfile` for a Node.js application:

```dockerfile
# Use the official Node.js runtime as a parent image
FROM node:16-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Command to run the app
CMD ["npm", "start"]
```

To build the Docker image, run the following command:

```bash
docker build -t my-node-app .
```

After building the image, it can be pushed to a Docker registry such as Docker Hub:

```bash
docker tag my-node-app username/my-node-app
docker push username/my-node-app
```

### Deploying to Kubernetes

Once the Docker image is available in a registry, it can be deployed to a Kubernetes cluster. This involves creating Kubernetes manifests for deployment and services.

#### Example: Kubernetes Manifests

Here’s an example of a `deployment.yaml` and `service.yaml` for a Node.js application:

**deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: node-app-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: node-app
  template:
    metadata:
      labels:
        app: node-app
    spec:
      containers:
      - name: node-app
        image: username/my-node-app
        ports:
        - containerPort: 3000
```

**service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: node-app-service
spec:
  selector:
    app: node-app
  ports:
    - protocol: TCP
      port: 3000
      targetPort: 3000
  type: LoadBalancer
```

To apply these manifests, run:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### Exposing Metrics with Prometheus Client Libraries

Prometheus is a powerful open-source monitoring system and time series database. To expose metrics from a Node.js application, you can use the Prometheus client library.

#### Installing the Prometheus Client Library

First, install the Prometheus client library for Node.js:

```bash
npm install prom-client
```

#### Example: Using Prometheus Client Library

Here’s an example of how to use the Prometheus client library in a Node.js application:

```javascript
const express = require('express');
const { register } = require('prom-client');

const app = express();

// Register a counter metric
const requests = new register.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
});

app.get('/', (req, res) => {
  requests.inc();
  res.send('Hello World!');
});

// Serve the metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});
```

### Configuring Prometheus to Scrape Metrics

To configure Prometheus to scrape metrics from your Node.js application, you need to update the Prometheus configuration file (`prometheus.yml`):

```yaml
scrape_configs:
  - job_name: 'node-app'
    static_configs:
      - targets: ['<your-node-app-service-ip>:3000']
```

Restart Prometheus to apply the changes:

```bash
sudo systemctl restart prometheus
```

### Monitoring with Grafana

Grafana is a visualization tool that can be used to create dashboards based on the metrics collected by Prometheus. Here’s how to set up Grafana:

1. **Install Grafana**: You can install Grafana using Docker or a package manager.
2. **Configure Data Source**: Add Prometheus as a data source in Grafana.
3. **Create Dashboards**: Create dashboards to visualize the metrics.

#### Example: Grafana Dashboard

Here’s an example of a simple Grafana dashboard for monitoring HTTP requests:

```json
{
  "annotations": {},
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": 1,
  "iteration": 1577836800092,
  "links": [],
  "panels": [
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {}
        },
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "hiddenSeries": false,
      "id": 2,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 2,
      "nullPointMode": "connected",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.5.4",
      "pointradius": 5,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "http_requests_total",
          "interval": "",
          "legendFormat": "",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeShift": null,
      "title": "HTTP Requests",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": false
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    }
  ],
  "schemaVersion": 26,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {
    "refresh_intervals": [
      "5s",
      "10s",
      "30s",
      "1m",
      "5m",
      "15m",
      "30m",
      "1h",
      "2h",
      "1d"
    ],
    "time_options": [
      "5m",
      "15m",
      "1h",
      "6h",
      "12h",
      "24h",
      "2d",
      "7d",
      "30d"
    ]
  },
  "timezone": "",
  "title": "Node App Metrics",
  "uid": "QIYjXKZ7k",
  "version": 1
}
```

### How to Prevent / Defend

#### Detection

To detect potential issues with your application, you can set up alerts in Prometheus. For example, you can alert if the number of HTTP requests exceeds a certain threshold.

#### Prevention

1. **Secure Configuration**: Ensure that sensitive information is not exposed in your application. Use environment variables and secrets management tools.
2. **Regular Updates**: Keep your dependencies and libraries up to date to avoid known vulnerabilities.
3. **Monitoring and Logging**: Implement comprehensive logging and monitoring to detect and respond to issues quickly.

#### Secure Coding Fixes

Here’s an example of a vulnerable code snippet and its secure version:

**Vulnerable Code**

```javascript
app.get('/secret', (req, res) => {
  res.send(process.env.SECRET_KEY);
});
```

**Secure Code**

```javascript
app.get('/secret', (req, res) => {
  if (req.isAuthenticated()) {
    res.send(process.env.SECRET_KEY);
  } else {
    res.status(401).send('Unauthorized');
  }
});
```

### Conclusion

Deploying a Node.js application to a Kubernetes cluster and exposing metrics with Prometheus client libraries is a crucial part of modern DevOps practices. By following the steps outlined in this chapter, you can ensure that your application is deployed reliably and monitored effectively. Additionally, by implementing secure coding practices and regular updates, you can prevent potential security issues.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for security training.
- **WebGoat**: An interactive web application security training tool.

These labs provide practical experience in deploying and securing applications in a Kubernetes environment.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/10-Exposing Metrics with Prometheus Client Libraries/00-Overview|Overview]] | [[02-Introduction to Exposing Metrics with Prometheus Client Libraries|Introduction to Exposing Metrics with Prometheus Client Libraries]]

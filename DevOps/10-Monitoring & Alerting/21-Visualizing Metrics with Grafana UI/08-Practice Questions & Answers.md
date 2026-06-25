---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. What is the role of Grafana in the Prometheus stack, and how is it accessed?**

Grafana serves as a data visualization tool that allows users to observe and analyze metrics collected by Prometheus. To access Grafana, you typically perform port forwarding to the Grafana service running in the cluster. For instance, you can use `kubectl port-forward` to map the Grafana service running on port 80 to a local port, such as 8080. Once forwarded, you can access Grafana via a web browser at `http://localhost:8080`. The default login credentials are usually provided by the Helm chart used to deploy the Prometheus stack, such as `admin` for the username and `prom` for the password.

**Q2. Explain the structure of a dashboard in Grafana.**

In Grafana, a dashboard is a collection of visualizations (panels) grouped into rows. The hierarchy of components is as follows:

- **Folders**: Dashboards are organized into folders. Folders can contain multiple dashboards.
- **Dashboards**: A dashboard consists of multiple rows.
- **Rows**: Each row contains one or more panels.
- **Panels**: Panels display data in various formats, such as graphs, tables, or single-value displays.

This structure allows users to organize and present data in a logical and intuitive manner, making it easier to monitor and analyze system performance.

**Q3. How can you identify the cause of a CPU spike using Grafana dashboards?**

To identify the cause of a CPU spike, follow these steps:

1. **Observe the Spike**: Use the general CPU usage dashboard to identify the spike in CPU usage.
2. **Drill Down**: Switch to a more detailed dashboard, such as the "Compute Resources Node with Pod Breakdown," to see which pods are contributing to the spike.
3. **Select Timeframe**: Use the timeframe selector to zoom in on the period when the spike occurred.
4. **Analyze Data**: Examine the CPU usage per pod and node to determine which pod or application is causing the spike.

For example, if you notice a spike in the general CPU dashboard, you can switch to the detailed dashboard to see that the `frontend` pod is consuming significantly more CPU resources during the spike period.

**Q4. What is PromQL, and how is it used in Grafana?**

PromQL (Prometheus Query Language) is a query language used to retrieve and manipulate time series data stored in Prometheus. In Grafana, PromQL is used to fetch data from Prometheus and visualize it in various forms, such as graphs, tables, or single-value displays.

When editing a panel in Grafana, you can see the PromQL query that retrieves the required data. For example, a query to fetch total CPU usage per pod might look like this:

```promql
sum(rate(container_cpu_usage_seconds_total{container_label_name!="POD"}[1m])) by (pod)
```

This query calculates the rate of CPU usage over the past minute and groups the results by pod. Understanding basic PromQL syntax helps in creating custom dashboards and alerts.

**Q5. How can you configure Grafana to visualize data from multiple data sources?**

To configure Grafana to visualize data from multiple data sources, follow these steps:

1. **Add Data Sources**: Go to the Grafana settings and navigate to the "Data Sources" section. Here, you can add new data sources, such as Prometheus, MySQL, PostgreSQL, Elasticsearch, and others.
2. **Configure Data Source**: For each data source, provide the necessary connection details, such as the URL, authentication credentials, and any additional configuration parameters.
3. **Create Dashboards**: When creating or editing a dashboard, you can select the appropriate data source for each panel. This allows you to visualize data from different sources within the same dashboard.

For example, you might configure Grafana to visualize CPU usage data from Prometheus and log data from Elasticsearch in the same dashboard. This flexibility enables comprehensive monitoring and analysis across multiple systems and data sources.

**Q6. How can you simulate a CPU spike in a Kubernetes cluster for testing purposes?**

To simulate a CPU spike in a Kubernetes cluster, you can use a simple script to send a large number of requests to an application endpoint. Here’s an example using a `busybox` pod:

1. **Deploy Busybox Pod**: Deploy a pod with the `busybox` image.
    ```sh
    kubectl run -i --tty curl-test --image=busybox --restart=Never -- sh
    ```

2. **Write Script**: Inside the pod, write a script to send requests to the application endpoint.
    ```sh
    cat > test.sh <<EOF
    for i in \$(seq 1 10000); do
      curl -o /dev/null http://<application-endpoint>
    done
    EOF
    chmod +x test.sh
    ```

3. **Execute Script**: Run the script to generate the load.
    ```sh
    ./test.sh
    ```

By sending a large number of requests, you can observe a CPU spike in the Grafana dashboard, helping you test and validate your monitoring setup.

**Q7. What are some best practices for using Grafana in a multi-team environment?**

In a multi-team environment, some best practices for using Grafana include:

1. **User Management**: Configure user roles and permissions to control access to dashboards and data sources. Use Grafana’s built-in user management features to assign roles and permissions.
2. **Team Dashboards**: Create separate folders for different teams to organize dashboards. This ensures that each team can focus on the metrics relevant to their responsibilities.
3. **Data Sources**: Ensure that all necessary data sources are configured and accessible to the relevant teams. This includes setting up connections to Prometheus, logging services, and other data sources.
4. **Documentation**: Maintain documentation for dashboards and data sources to ensure that all team members understand the purpose and usage of each dashboard.
5. **Regular Updates**: Regularly update and refine dashboards based on feedback and changing requirements. This ensures that the dashboards remain relevant and useful for all teams.

By following these practices, you can effectively leverage Grafana to support monitoring and analysis across multiple teams in a Kubernetes cluster.

---
<!-- nav -->
[[07-Introduction to Visualizing Metrics with Grafana UI|Introduction to Visualizing Metrics with Grafana UI]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/21-Visualizing Metrics with Grafana UI/00-Overview|Overview]]

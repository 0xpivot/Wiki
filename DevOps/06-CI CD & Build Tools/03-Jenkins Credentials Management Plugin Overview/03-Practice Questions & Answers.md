---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the difference between system and global credentials in Jenkins.**

The primary difference between system and global credentials in Jenkins lies in their accessibility:

- **System Credentials**: These are only accessible to the Jenkins server itself and are not visible or usable by Jenkins jobs or pipelines. They are typically used for administrative tasks such as configuring Jenkins to communicate with other services. System credentials are stored in the global domain but are not accessible to build jobs or pipeline jobs.

- **Global Credentials**: These are accessible everywhere within Jenkins, including both Jenkins administrators and all build jobs and pipeline jobs. Global credentials can be referenced in any job or pipeline, making them versatile for tasks that require authentication across multiple services.

**Q2. How can you create a new global credential in Jenkins?**

To create a new global credential in Jenkins, follow these steps:

1. Navigate to the Jenkins dashboard.
2. Go to `Credentials` under the `Manage Jenkins` section.
3. Click on `Global credentials (unrestricted)` or `Global credentials (restricted)` depending on your setup.
4. Click on `Add Credentials`.
5. Select the type of credential you want to create (e.g., Username with password).
6. Fill in the required fields such as `Username`, `Password`, and `ID`.
7. Click `OK` to save the new global credential.

Here’s an example of creating a global username and password credential:

```plaintext
1. Go to Manage Jenkins > Manage Credentials > Global credentials (unrestricted)
2. Click Add Credentials
3. Select Username with password
4. Enter the username and password
5. Set an ID (e.g., my-global-cred)
6. Click OK
```

**Q3. What is the purpose of the multi-branch pipeline scope for credentials?**

The multi-branch pipeline scope for credentials allows you to create credentials that are specific to a particular project or branch within a multi-branch pipeline. This scope ensures that credentials are only accessible within the context of that specific pipeline, providing better isolation and security compared to global or system credentials.

This feature is particularly useful in environments where multiple teams or projects share the same Jenkins instance. By scoping credentials to a specific pipeline, you can ensure that sensitive information remains isolated and is not accessible to other projects or teams.

**Q4. How would you exploit a misconfigured Jenkins Credentials Management Plugin to gain unauthorized access?**

A misconfigured Jenkins Credentials Management Plugin could potentially expose sensitive credentials, leading to unauthorized access. Here’s how an attacker might exploit such a misconfiguration:

1. **Identify Misconfigured Credentials**: An attacker might look for credentials that are improperly scoped (e.g., a system credential that should be private but is accessible globally).

2. **Access Jenkins UI**: If the attacker has access to the Jenkins UI, they can navigate to the `Manage Jenkins` > `Manage Credentials` section to view and potentially download credentials.

3. **Exploit Weak Permissions**: If the permissions are weak, the attacker might be able to modify or delete credentials, causing disruptions or gaining further access.

4. **Use Stolen Credentials**: Once the attacker has obtained the credentials, they can use them to authenticate to other systems or services that Jenkins interacts with, such as databases, cloud services, or version control systems.

To prevent such attacks, ensure that credentials are properly scoped, and limit access to the Jenkins UI and API to trusted users.

**Q5. Describe a recent real-world example where mismanagement of Jenkins credentials led to a security breach.**

One notable example is the incident involving the Jenkins credentials management plugin in 2020, where a vulnerability in the Jenkins credentials management plugin (CVE-2020-14140) allowed attackers to bypass authentication and gain unauthorized access to Jenkins instances.

In this case, the vulnerability was due to a flaw in the Jenkins credentials management plugin that allowed attackers to bypass authentication checks when accessing certain resources. This led to unauthorized access to Jenkins instances, potentially exposing sensitive credentials and allowing attackers to perform malicious actions.

To mitigate such risks, it is crucial to keep Jenkins and its plugins up-to-date with the latest security patches and to implement proper credential management practices, including proper scoping and access controls.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/03-Jenkins Credentials Management Plugin Overview/03-Jenkins Credentials Management Plugin Overview|Jenkins Credentials Management Plugin Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/03-Jenkins Credentials Management Plugin Overview/00-Overview|Overview]]

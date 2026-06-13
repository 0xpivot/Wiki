---
tags: [vapt, subdomain-takeover, dns, cname, cloud, intermediate]
difficulty: intermediate
module: "34 - Subdomain Takeover"
topic: "34.02 CNAME to Unclaimed External Service (GitHub Pages, Heroku, S3)"
---

# 34.02 CNAME to Unclaimed External Service (GitHub Pages, Heroku, S3)

## 1. Introduction to Cloud-Based Routing Flaws

The most prevalent vector for subdomain takeover involves a Canonical Name (CNAME) record pointing to an external Platform as a Service (PaaS), Software as a Service (SaaS), or Infrastructure as a Service (IaaS) provider where the associated resource does not exist. 

To exploit this vulnerability reliably, a penetration tester must deeply understand the underlying routing architecture of multi-tenant cloud environments. In a multi-tenant architecture, millions of customers share the same fleet of load balancers and edge routers. The cloud provider cannot possibly allocate a dedicated, static IP address for every single customer application—it would rapidly exhaust the IPv4 space and incur massive operational overhead.

Instead, they rely on **Virtual Hosting**, a concept where a single IP address hosts thousands of different web applications. The crucial mechanism that makes Virtual Hosting work is the HTTP `Host` header.

## 2. The Mechanics of Multi-Tenant Routing

When an organization wants to host a blog on GitHub Pages under the domain `blog.company.com`, they must complete two steps:
1.  **On the Cloud Provider (GitHub):** They configure their repository settings to accept `blog.company.com` as a Custom Domain.
2.  **On the DNS Provider:** They create a CNAME record pointing `blog.company.com` to `company.github.io`.

When a visitor attempts to access the blog, the DNS resolution ultimately yields the IP addresses of GitHub's edge load balancers. The visitor's browser connects to one of these IPs and sends an HTTP request:

```http
GET / HTTP/1.1
Host: blog.company.com
User-Agent: Mozilla/5.0...
```

GitHub's load balancer inspects the `Host` header (`blog.company.com`). It queries its internal database: *"Which user repository has registered 'blog.company.com'?"* It finds the mapping, fetches the static files from the `company` organization's repository, and serves the content.

**The Vulnerability:** If the company deletes their GitHub repository, the internal mapping at GitHub is destroyed. However, if they forget to delete the CNAME record from their DNS provider, the DNS still points to GitHub. 

If an attacker identifies this, they can simply create their own GitHub repository and add `blog.company.com` as their Custom Domain. Now, when the GitHub load balancer sees `Host: blog.company.com`, it queries its database, finds the *attacker's* mapping, and serves the attacker's malicious content.

## 3. ASCII Architecture Diagram: Multi-Tenant Host Header Routing

```text
========================================================================================
                      CLOUD MULTI-TENANT HOST HEADER ROUTING
========================================================================================

                          [ HTTP REQUEST ]
                          GET / HTTP/1.1
                          Host: sub.target.com
                                  |
                                  v
+--------------------------------------------------------------------------------------+
|                           CLOUD PROVIDER EDGE ROUTER                                 |
|                       (e.g., AWS, Heroku, GitHub, Azure)                             |
|                                                                                      |
|  [ INCOMING REQUEST HOST HEADER ] ========> [ ROUTING TABLE DATABASE LOOKUP ]        |
+--------------------------------------------------------------------------------------+
                                  |
            +---------------------+---------------------+
            |                     |                     |
     [MATCH FOUND]         [MATCH FOUND]         [NO MATCH FOUND]
  (Tenant A's Config)   (Attacker's Config)      (Dangling/Orphaned)
            |                     |                     |
            v                     v                     v
   +-----------------+   +-----------------+   +-----------------+
   |  INTERNAL APP   |   |  INTERNAL APP   |   | ERROR HANDLER   |
   |   CONTAINER     |   |   CONTAINER     |   |                 |
   | (Legitimate)    |   |  (Malicious!)   |   | Returns 404     |
   |                 |   |                 |   | "Site Not Found"|
   +-----------------+   +-----------------+   +-----------------+
                                                     ^
                                                     |
               An attacker sees this error, registers the domain in 
               the cloud provider, and shifts the routing to the
               "Malicious Container" pathway.
```

## 4. Deep Dive Case Studies

Different cloud providers implement custom domain binding in different ways. Understanding these nuances is critical for successful exploitation.

### 4.1 Amazon S3 (Simple Storage Service)

AWS S3 is heavily used for hosting static websites. 
*   **The Signature:** A dangling S3 CNAME typically returns a `404 Not Found` with an XML response body containing `<Code>NoSuchBucket</Code>`.
*   **Exploitation Nuance:** For S3 static site hosting to work with custom domains, the S3 bucket name **must exactly match** the full CNAME. If the dangling domain is `assets.company.com` pointing to `s3-website-us-east-1.amazonaws.com`, the attacker *must* create an S3 bucket named precisely `assets.company.com`. 
*   **The Catch:** S3 bucket names are globally unique across all AWS accounts. If another user has already registered a bucket named `assets.company.com` but hasn't configured it to serve web traffic, the attacker cannot claim it, resulting in a failed takeover attempt (a false positive for the penetration tester).

### 4.2 GitHub Pages

GitHub Pages allows users to host static sites directly from repositories.
*   **The Signature:** A dangling GitHub Pages CNAME returns a `404` page with the title `Site not found` and the text `There isn't a GitHub Pages site here.`
*   **Exploitation Nuance:** Historically, claiming a GitHub Pages domain was trivial—just add the domain to a repo's `CNAME` file. However, due to widespread abuse, GitHub introduced **Domain Verification**. To claim a domain today, the user often must prove ownership by adding a specific TXT record to the domain's DNS. 
*   **Bypassing Mitigations:** If the target organization had *previously* verified the apex domain (`company.com`) but left a dangling subdomain (`blog.company.com`), GitHub might still allow the takeover if the attacker targets the exact repository structure or if organizational verification policies are misconfigured. It is highly dependent on the target's internal GitHub Organization settings.

### 4.3 Heroku

Heroku is a popular PaaS for deploying Node.js, Python, Ruby, and Java applications.
*   **The Signature:** `404 Not Found` with the text `No such app` or the classic Heroku error page.
*   **Exploitation Nuance:** Heroku routes traffic via a sophisticated mesh network. Dangling records often look like `sub.target.com IN CNAME secure.domain.herokudns.com`.
*   **The Catch:** Similar to GitHub, Heroku has tightened its security. They now issue randomized `.herokudns.com` targets (e.g., `whispering-willow-12345.herokudns.com`). However, many legacy setups still use the old routing methods. If an attacker can successfully add the custom domain via the Heroku CLI (`heroku domains:add sub.target.com -a attacker-app`), the mesh network will instantly begin routing traffic to the attacker's dynos.

### 4.4 Microsoft Azure Cloud Services

Azure presents unique challenges and massive attack surfaces.
*   **Examples:** Traffic Manager (`.trafficmanager.net`), Azure App Services (`.azurewebsites.net`), and Blob Storage.
*   **Exploitation Nuance:** Azure App Services has historically been highly vulnerable. If `app.company.com` points to `company-app.azurewebsites.net` and the App Service is deleted, an attacker can create a new App Service named `company-app`. Azure will allow the custom domain binding without necessarily requiring a TXT record verification *if* the CNAME already points to the Azure infrastructure, which it does in a dangling scenario. This makes Azure takeovers exceptionally critical and reliable.

## 5. Identifying the External Provider

To successfully exploit a CNAME takeover, you must first identify which cloud service the CNAME is pointing to. This is generally done by observing the endpoint domain.

| Target CNAME Target | Associated Cloud Service |
| :--- | :--- |
| `*.s3.amazonaws.com` | Amazon Web Services S3 |
| `*.github.io` | GitHub Pages |
| `*.herokuapp.com` / `*.herokudns.com` | Heroku |
| `*.azurewebsites.net` | Microsoft Azure App Services |
| `*.myshopify.com` | Shopify |
| `*.zendesk.com` | Zendesk |
| `*.readme.io` | Readme.io |
| `*.unbouncepages.com` | Unbounce |
| `*.fastly.net` | Fastly CDN |

*Note: The list of vulnerable services is constantly evolving. Security researchers maintain comprehensive lists online (e.g., "Can I take over XYZ").*

## 6. Chaining Opportunities

*   **[[08 - Phishing and Social Engineering]]:** Utilizing the hijacked domain to send out highly credible phishing emails, as the SPF/DKIM records of the apex domain may implicitly trust the subdomain.
*   **[[09 - SSL/TLS Certificate Exploitation]]:** Provisioning legitimate Let's Encrypt certificates for the hijacked domain to bolster the illusion of legitimacy in targeted attacks.
*   **[[01 - What is Subdomain Takeover]]:** Refer back for the fundamental impacts like session hijacking and CORS bypasses.

## 7. Related Notes
*   [[03 - Fingerprinting Vulnerable Services]]
*   [[12 - DNS Reconnaissance]]
*   [[15 - Cloud Security Misconfigurations]]

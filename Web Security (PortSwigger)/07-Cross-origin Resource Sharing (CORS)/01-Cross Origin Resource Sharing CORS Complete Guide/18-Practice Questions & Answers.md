---
course: Web Security
topic: Cross-origin Resource Sharing (CORS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the Same Origin Policy (SOP) and its purpose in web security.**

The Same Origin Policy (SOP) is a security mechanism enforced by web browsers to prevent unauthorized access to resources. It ensures that a web application running in one origin (defined by the scheme, hostname, and port) cannot access resources from another origin without explicit permission. The primary purpose of SOP is to prevent malicious scripts from accessing sensitive data, such as cookies or other session information, from different domains. This helps mitigate attacks like Cross-Site Scripting (XSS).

**Q2. Describe the different ways to exploit Cross-Origin Resource Sharing (CORS) vulnerabilities.**

Exploiting CORS vulnerabilities typically involves manipulating the `Access-Control-Allow-Origin` and `Access-Control-Allow-Credentials` headers. Here are a few methods:

1. **Dynamic Generation Vulnerabilities**: If the server reflects the `Origin` header back in the `Access-Control-Allow-Origin` header without proper validation, an attacker can set the `Origin` header to any value and gain unauthorized access.
   
   Example payload:
   ```javascript
   var xhr = new XMLHttpRequest();
   xhr.open('GET', 'https://vulnerable-site.com/api/data', true);
   xhr.setRequestHeader('Origin', 'http://attacker.com');
   xhr.withCredentials = true;
   xhr.onreadystatechange = function() {
       if (xhr.readyState === 4 && xhr.status === 200) {
           console.log(xhr.responseText);
       }
   };
   xhr.send();
   ```

2. **Null Origin Exploitation**: If the server whitelists the null origin (`null`), an attacker can exploit this by running the script in a sandboxed iframe, making the request appear to come from the null origin.
   
   Example payload:
   ```html
   <iframe src="javascript:var xhr=new XMLHttpRequest();xhr.open('GET','https://vulnerable-site.com/api/data',true);xhr.withCredentials=true;xhr.onload=function(){console.log(xhr.responseText);};xhr.send();" sandbox="allow-same-origin"></iframe>
   ```

3. **Wildcard Character Misuse**: If the server uses a wildcard (`*`) in the `Access-Control-Allow-Origin` header and allows credentials, an attacker can access authenticated resources from any origin.

**Q3. How can you prevent CORS vulnerabilities in web applications?**

To prevent CORS vulnerabilities, follow these best practices:

1. **Whitelist Trusted Origins**: Only allow specific origins to access your resources. Avoid using wildcard characters (`*`) unless absolutely necessary.

2. **Avoid Whitelisting Null Origin**: Never explicitly whitelist the null origin (`null`). This can lead to unauthorized access via sandboxed iframes.

3. **Use Secure Headers**: Ensure that the `Access-Control-Allow-Credentials` header is set to `true` only when necessary and only for trusted origins.

4. **Regular Audits**: Regularly audit your CORS configurations to ensure they remain secure and aligned with current best practices.

5. **Automated Scanning Tools**: Use automated scanning tools to detect potential CORS misconfigurations. These tools can help identify vulnerabilities that might be overlooked during manual reviews.

**Q4. Discuss recent real-world examples of CORS vulnerabilities and their impacts.**

One notable example is CVE-2019-9580, where a CORS misconfiguration in a web application allowed attackers to gain remote code execution. The vulnerability stemmed from the application whitelisting the null origin, which allowed attackers to bypass the Same Origin Policy and access sensitive data.

Another example is the 2016 vulnerability in the IntelliJ IDEA IDE, where the IDE’s web server allowed any origin to access its resources. This led to a scenario where an attacker could exploit this misconfiguration to steal SSH credentials and eventually gain remote code execution, earning the security researcher a $50,000 bounty.

These examples highlight the importance of proper CORS configuration and the potential severe impacts of misconfigurations.

**Q5. How would you test for CORS vulnerabilities from a black box perspective?**

Testing for CORS vulnerabilities from a black box perspective involves the following steps:

1. **Map the Application**: Identify all accessible endpoints and observe if they return any CORS-related headers.

2. **Test Dynamic Generation**: Intercept requests and modify the `Origin` header to random values to check if the server reflects the `Origin` header back in the `Access-Control-Allow-Origin` header.

3. **Test Regex Implementations**: Modify the `Origin` header to test if the server uses regex patterns to validate origins. Try appending or prepending strings to known trusted domains to see if the server accepts them.

4. **Check Null Origin**: Set the `Origin` header to `null` and see if the server accepts it.

5. **Review Credentials Header**: Check if the `Access-Control-Allow-Credentials` header is set to `true`. If so, the vulnerability is more severe as it allows access to authenticated resources.

By systematically testing these aspects, you can identify potential CORS vulnerabilities in the application.

---
<!-- nav -->
[[Web Security (PortSwigger)/07-Cross-origin Resource Sharing (CORS)/01-Cross Origin Resource Sharing CORS Complete Guide/17-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/07-Cross-origin Resource Sharing (CORS)/01-Cross Origin Resource Sharing CORS Complete Guide/00-Overview|Overview]] | [[19-Summary|Summary]]

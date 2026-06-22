---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a cross-site scripting (XSS) vulnerability is and how it differs from SQL injection.**

Cross-site scripting (XSS) is a client-side vulnerability where an attacker injects malicious scripts into a webpage that gets executed in the victim's browser. Unlike SQL injection, which targets the server-side database to manipulate or extract data, XSS exploits the client-side code to perform actions on behalf of the victim or steal sensitive information. The primary difference lies in the target: XSS affects the user's interaction with the application, while SQL injection targets the backend database.

**Q2. Describe the three main types of XSS vulnerabilities and provide an example for each.**

1. **Reflected XSS**: The attacker injects a script into a request that is immediately reflected back in the response. For example, if a search box reflects the input directly in the response, an attacker could inject a script like `<script>alert('XSS')</script>` into the search query, causing it to execute in the victim's browser.

2. **Stored XSS**: The attacker injects a script into the application's persistent storage (like a database), which is then served to victims. For instance, if a forum allows users to post comments without proper sanitization, an attacker could post a comment with a script like `<script>alert(document.cookie)</script>`, which would execute whenever someone reads the comment.

3. **DOM-based XSS**: This occurs when the client-side JavaScript modifies the DOM based on untrusted input. For example, if a JavaScript function reads a URL parameter and writes it to the DOM without validation, an attacker could craft a URL like `http://example.com/?q=<script>alert('XSS')</script>` to execute the script in the victim's browser.

**Q3. How can an attacker exploit a reflected XSS vulnerability? Provide a step-by-step explanation.**

1. **Identify Vulnerable Parameters**: The attacker identifies parameters in the application that reflect user input in the response, such as a search query or a URL parameter.
   
2. **Craft Malicious Payload**: The attacker crafts a payload that includes a script, such as `<script>alert(document.cookie)</script>`.
   
3. **Inject Payload**: The attacker injects the payload into the vulnerable parameter. For example, if the search query is vulnerable, the attacker might construct a URL like `http://example.com/search?q=<script>alert(document.cookie)</script>`.
   
4. **Trick Victim**: The attacker tricks the victim into clicking on the crafted URL, often through phishing emails or social engineering tactics.
   
5. **Exploit**: When the victim clicks the link, the script is executed in their browser, potentially stealing cookies or performing other malicious actions.

**Q4. Discuss recent real-world examples of XSS vulnerabilities and their impacts.**

1. **Magento XSS to RCE**: In 2020, a critical vulnerability was discovered in Magento, a popular e-commerce platform. The vulnerability involved a stored XSS that could be chained with other flaws to achieve remote code execution (RCE). Attackers could exploit this to take control of the server, leading to severe data breaches and financial losses.

2. **MySpace XSS Worm**: In 2005, MySpace suffered from a stored XSS vulnerability that led to the creation of the "Samy" worm. This worm spread rapidly across the social network, adding the attacker as a friend to thousands of users and copying the malicious script to their profiles. This incident highlighted the potential for XSS to cause widespread disruption and forced MySpace to temporarily shut down to clean the infection.

**Q5. How can developers prevent XSS vulnerabilities in their applications?**

1. **Output Encoding**: Encode any user-supplied data before displaying it on the page. Use context-specific encoding (HTML, JavaScript, etc.) to ensure that the data is treated as plain text rather than executable code.

2. **Input Validation**: Validate and sanitize all user inputs to ensure they meet expected formats. Use allow lists (whitelisting) wherever possible to restrict input to safe values.

3. **Content Security Policy (CSP)**: Implement CSP to define the sources of trusted content and restrict the execution of scripts from untrusted origins. This helps mitigate the impact of XSS attacks by limiting the sources from which scripts can be loaded.

4. **HTTP-only Cookies**: Set the `HttpOnly` flag on cookies to prevent them from being accessed via JavaScript, reducing the risk of session hijacking through XSS.

5. **Use Libraries and Frameworks**: Utilize well-established libraries and frameworks that handle XSS protection internally. These tools often include built-in mechanisms to escape and sanitize user inputs effectively.

**Q6. How can you bypass common defenses against XSS, such as input filters?**

1. **Character Encoding**: Use character encoding to bypass simple filters. For example, instead of using `<script>`, use `%3Cscript%3E`.

2. **Event Handlers**: Exploit event handlers that are not filtered, such as `onmouseover`, `onerror`, or `onload`. For example, `<img src=x onerror="alert('XSS')">`.

3. **UTF-16 Encoding**: Use UTF-16 encoding to bypass filters that block ASCII characters. For example, `\u003Cscript\u003Ealert('XSS')\u003C/script\u003E`.

4. **Whitespaces**: Add whitespaces or tabs to break up keywords that are blocked by filters. For example, `Java\u0009Script`.

5. **Brute Force**: Use a brute force approach to test various tags and event handlers until you find one that is not filtered. Tools like Burp Suite can automate this process.

**Q7. What are the potential impacts of an XSS vulnerability, and how can they be mitigated?**

1. **Stealing Sensitive Data**: XSS can be used to steal cookies, session tokens, and other sensitive data. Mitigation involves using HTTP-only flags on cookies and ensuring proper input validation and encoding.

2. **Defacement**: Attackers can alter the appearance of a website, causing reputational damage. Proper content security policies (CSP) and input validation can help prevent this.

3. **Phishing Attacks**: XSS can be used to trick users into entering credentials on fake login pages. Educating users and implementing robust authentication mechanisms can reduce the risk.

4. **Session Hijacking**: By stealing session tokens, attackers can impersonate users. Using secure session management practices and HTTP-only cookies can mitigate this risk.

5. **Remote Code Execution**: In some cases, XSS can be chained with other vulnerabilities to achieve RCE. Regular security audits and updates can help prevent such complex attacks.

**Q8. How would you test an application for DOM-based XSS vulnerabilities?**

1. **Review Client-Side JavaScript**: Analyze the JavaScript code to identify points where user input is used to modify the DOM. Look for functions like `document.write`, `innerHTML`, and `setAttribute`.

2. **Inject Unique Strings**: Inject unique strings into the application and monitor where they are reflected in the DOM. Use the browser’s developer tools to trace the flow of data from input to DOM modification.

3. **Test Event Handlers**: Test various event handlers to see if they can be exploited. For example, `<img src=x onerror="alert('XSS')">` can be used to test if the `onerror` event handler is vulnerable.

4. **Use Automated Tools**: Utilize automated tools like Burp Suite or OWASP ZAP to scan for DOM-based XSS vulnerabilities. These tools can help identify potential issues that might be missed during manual testing.

5. **Validate Context**: Ensure that the context in which the input is reflected is properly encoded. For example, if the input is used in a script context, ensure it is properly escaped to prevent execution.

By following these steps, you can effectively test an application for DOM-based XSS vulnerabilities and take necessary measures to mitigate the risks.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/01-Cross Site Scripting XSS Complete Guide/12-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/01-Cross Site Scripting XSS Complete Guide/00-Overview|Overview]]

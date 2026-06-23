---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Understanding DOM-Based Open Redirection

DOM-based open redirection is a specific type of vulnerability where an attacker can manipulate the URL to redirect the user to a different site controlled by the attacker. This can be used for phishing attacks, where the attacker tricks the user into visiting a malicious site that mimics a legitimate one.

### How Does DOM-Based Open Redirection Work?

In a typical scenario, a web application might use JavaScript to read URL parameters and perform actions based on those parameters. If the parameter is not properly validated, an attacker can inject a URL that will cause the browser to redirect to a different site.

#### Example Scenario

Consider a web application that reads a `redirect` parameter from the URL and uses it to set the location of the page:

```javascript
var urlParams = new URLSearchParams(window.location.search);
var redirectUrl = urlParams.get('redirect');
if (redirectUrl) {
    window.location.href = redirectUrl;
}
```

If an attacker can inject a URL into the `redirect` parameter, they can cause the browser to redirect to a malicious site.

### Real-World Example: CVE-2020-14882

CVE-2020-14882 is a real-world example of a DOM-based open redirection vulnerability found in the popular web analytics service Matomo (formerly Piwik). The vulnerability allowed an attacker to inject a URL into the `redirect` parameter, causing the browser to redirect to a malicious site. This demonstrates the importance of validating and sanitizing URL parameters in client-side code.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/04-Lab 4 DOM based open redirection/05-Lab Setup and Environment|Lab Setup and Environment]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/04-Lab 4 DOM based open redirection/00-Overview|Overview]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/04-Lab 4 DOM based open redirection/07-Understanding DOM-Based Vulnerabilities|Understanding DOM-Based Vulnerabilities]]

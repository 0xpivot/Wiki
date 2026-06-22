---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Technical Details Behind CSRF Vulnerabilities

### What is CSRF?

CSRF occurs when an attacker tricks a victim into performing an action on a web application where the victim is already authenticated. The attacker does this by crafting a malicious request that the victim's browser will send to the web application.

#### How CSRF Works

1. **Authentication**: The victim is authenticated with the web application.
2. **Malicious Request**: The attacker crafts a request that performs an action on the web application.
3. **Victim Execution**: The victim unknowingly executes the malicious request, often through social engineering techniques like phishing emails or malicious websites.

### Potential Impact of Exploiting CSRF Vulnerabilities

The impact of a successful CSRF attack can vary widely depending on the nature of the web application and the actions that can be performed. Some potential impacts include:

- **Financial Loss**: Transferring funds from a bank account.
- **Data Manipulation**: Changing user settings or posting unauthorized content.
- **Account Takeover**: Resetting passwords or changing email addresses.

### Example Scenario

Consider a banking application where a user is logged in and can transfer money to another account. An attacker could craft a malicious link that, when clicked, transfers money from the victim's account to the attacker's account.

```html
<a href="https://bank.example.com/transfer?to=attacker&amount=1000">Click here</a>
```

If the victim clicks this link, the browser will send the request to the bank's server, and the transfer will occur.

---
<!-- nav -->
[[14-Session Management and Cookies|Session Management and Cookies]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/01-Cross Site Request Forgery CSRF Complete Guide/00-Overview|Overview]] | [[16-Understanding Cross-Site Request Forgery (CSRF)|Understanding Cross-Site Request Forgery (CSRF)]]

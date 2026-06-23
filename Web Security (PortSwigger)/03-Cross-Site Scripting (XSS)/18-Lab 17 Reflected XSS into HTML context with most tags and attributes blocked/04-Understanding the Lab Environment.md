---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Understanding the Lab Environment

The lab environment is set up to simulate a web application where certain HTML tags and attributes are filtered out. However, some tags like `<body>` and custom tags are allowed. This setup helps us understand the nuances of filtering mechanisms and how attackers can bypass them.

### Allowed Tags and Attributes

- **Body Tag**: `<body>` is allowed, which means we can inject content inside this tag.
- **Custom Tags**: Custom tags are allowed, which can be used to inject arbitrary content.

### Testing the Environment

To start, we need to understand what is allowed and what is blocked. We can do this by sending different payloads and observing the responses.

#### Example Payloads

```plaintext
<body onload=alert(1)>
<customtag onload=alert(1)>
```

### Observing Responses

When we send these payloads, we observe the following:

- **200 OK Response**: Indicates that the payload was accepted and processed.
- **Custom Error Message**: Indicates that the payload was rejected due to filtering.

By analyzing these responses, we can determine which tags and attributes are allowed.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/18-Lab 17 Reflected XSS into HTML context with most tags and attributes blocked/03-How to Prevent  Defend Against XSS|How to Prevent  Defend Against XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/18-Lab 17 Reflected XSS into HTML context with most tags and attributes blocked/00-Overview|Overview]] | [[05-Understanding the Payload Injection|Understanding the Payload Injection]]

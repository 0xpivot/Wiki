---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Common Pitfalls and Mistakes

### Incorrect Tag Usage

One common mistake is using standard HTML tags instead of custom ones. This will likely be blocked by the server, preventing the attack from working.

### Lack of Proper Validation

Another pitfall is failing to validate user inputs properly. Always ensure that user inputs are sanitized and validated before embedding them into the HTML response.

### Overlooking Custom Tags

Some developers might overlook the possibility of custom tags being used in an attack. It's crucial to ensure that all user inputs are treated as untrusted and properly escaped.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/19-Lab 18 Reflected XSS into HTML context with all tags blocked except custom ones/04-Common Pitfalls and Detection|Common Pitfalls and Detection]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/19-Lab 18 Reflected XSS into HTML context with all tags blocked except custom ones/00-Overview|Overview]] | [[06-Crafting the Exploit|Crafting the Exploit]]

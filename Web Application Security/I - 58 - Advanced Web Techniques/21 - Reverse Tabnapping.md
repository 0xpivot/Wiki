---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.21 Reverse Tabnapping"
---

# Reverse Tabnapping

## Introduction
Reverse Tabnapping is an advanced web exploitation technique that leverages the default behavior of web browsers when handling links opened in new tabs or windows. This attack allows a malicious page opened from a victim's trusted page to rewrite the location of the original tab, redirecting the user to a phishing site or initiating malicious downloads. The vulnerability arises from the `window.opener` property, which provides a reference to the window that opened the current one. 

When a user clicks on a link with `target="_blank"`, the browser opens the linked document in a new tab. If the linked document is malicious, it can access the `window.opener` object to interact with the original page, even across different origins (though restricted by the Same-Origin Policy for most properties, `location` can still be changed).

## Technical Deep Dive

### The `window.opener` API
The `window.opener` property returns a reference to the window that opened the window in which the script is running. If the window was not opened by a script (or a link with `target="_blank"` without `rel="noopener noreferrer"`), `window.opener` is `null`.

When a link like `<a href="https://malicious.example.com" target="_blank">Click here</a>` is clicked, the new tab (`https://malicious.example.com`) gets full access to `window.opener`.

Although the Same-Origin Policy (SOP) prevents the malicious page from reading the DOM or sensitive variables of the original page (if they are on different domains), it does NOT prevent the malicious page from setting `window.opener.location`. This means the malicious page can navigate the original tab to any URL.

### Attack Mechanics
1. **The Vector:** The victim visits a legitimate forum, social media site, or web application that allows user-generated links but fails to implement proper `rel` attributes.
2. **The Lure:** The attacker posts a link: `<a href="https://attacker.com/funny-cats" target="_blank">Funny Cats</a>`.
3. **Execution:** The victim clicks the link. A new tab opens showing funny cats.
4. **The Payload:** In the background of the funny cats page, JavaScript executes: `if (window.opener) { window.opener.location = "https://legit-looking-phishing.com/login"; }`
5. **The Trap:** The original tab, which the victim trusted, is now displaying a phishing login page. When the victim switches back to the original tab, they might assume their session expired and enter their credentials.

### ASCII Diagram: Attack Flow

```text
+----------------------+                       +----------------------+
| Legitimate Site      |                       | Attacker Site        |
| (trusted.com)        |                       | (malicious.com)      |
|                      |                       |                      |
| <a target="_blank"   |---(1) User Clicks ---->                      |
| href="malicious.com">|                       | <script>             |
| Link                 |                       |  window.opener       |
+----------------------+                       |  .location =         |
           ^                                   |  'phishing.com';     |
           |                                   | </script>            |
           |                                   +----------------------+
           |
     (2) Redirects
           |
           v
+----------------------+
| Phishing Site        |
| (phishing.com)       |
|                      |
| Please log in again  |
| to continue...       |
+----------------------+
```

### Remediation and Defense

To mitigate Reverse Tabnapping, developers must ensure that any link opening in a new tab does not pass the `window.opener` reference unless explicitly required and trusted.

#### The `rel` Attribute
The most effective defense is adding the `rel` attribute with specific values to the anchor tags.

- `noopener`: Prevents the new page from accessing the `window.opener` object. The `window.opener` will be `null`.
- `noreferrer`: Also prevents the browser from sending the `Referer` HTTP header, which provides additional privacy, and implicitly implies `noopener` in most modern browsers.

**Example of secure implementation:**
`<a href="https://external.example.com" target="_blank" rel="noopener noreferrer">External Link</a>`

#### Browser Default Changes
Modern browsers (Safari 12.1+, Firefox 79+, Chromium 88+) have changed the default behavior. Now, `target="_blank"` implicitly implies `rel="noopener"`. However, relying solely on modern browser defaults is insufficient for robust security, as users on older browsers remain vulnerable. Furthermore, if the application explicitly sets `rel="opener"` (which some applications might do to maintain legacy functionality), the vulnerability is reintroduced.

### Real-World Exploitation Scenarios
1. **Oauth Flow Hijacking:** An application might use `target="_blank"` for a social login flow but fail to secure it. While the Oauth provider is typically secure, an attacker could potentially chain this if there's an open redirect or XSS on the provider.
2. **Spear Phishing in Enterprise Apps:** An attacker submits a ticket to an IT helpdesk containing a malicious link. The IT worker clicks it, gets redirected in the original tab, and subsequently logs into what they think is their internal Okta/SSO portal.

### Testing for Reverse Tabnapping
When performing a VAPT engagement, identifying this vulnerability involves checking how external links are handled.

1. **Manual Inspection:** Right-click and inspect external links on the target application. Look for `target="_blank"` without `rel="noopener noreferrer"`.
2. **Automated Scanning:** Use tools like Burp Suite, which has active and passive scanning checks for this vulnerability. Custom Nuclei templates can also easily detect the absence of `noopener`.
3. **Exploitation Verification:** Create a simple HTML page to test the vulnerability.

**Payload Example:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Malicious Page</title>
</head>
<body>
    <h1>You have been Tabnapped!</h1>
    <script>
        if (window.opener) {
            window.opener.location = "https://example.com/phishing";
        }
    </script>
</body>
</html>
```
Host this page and input its URL into the vulnerable application. Click the link and observe the original tab.

### Variations and Bypasses
While standard Reverse Tabnapping relies on `target="_blank"`, attackers can also exploit `window.open()` in JavaScript.

```javascript
window.open("https://malicious.com", "_blank");
```
If this is executed without specifying `noopener` in the window features string, the opened window will have access to `window.opener`.

**Secure `window.open`:**
```javascript
window.open("https://malicious.com", "_blank", "noopener,noreferrer");
```

### Impact Assessment
The impact of Reverse Tabnapping is primarily social engineering and phishing, making it a High severity issue depending on the context. If the original page handles highly sensitive actions or requires re-authentication frequently, the likelihood of a successful phishing attack increases drastically.

### Historical Context
Reverse Tabnapping gained prominence around 2010 when Aza Raskin highlighted the risk. Initially, it was a novel way to bypass the user's focus on the address bar of the current tab, as the original tab changes context while the user is distracted by the new tab. The introduction of `rel="noopener"` provided a definitive fix, but adoption was slow across the web development community.

## Chaining Opportunities
- **Cross-Site Scripting (XSS):** If you find Stored XSS but it has restrictions (like WAF blocks on execution), you can inject a basic anchor tag to execute Reverse Tabnapping.
- **Open Redirects:** An open redirect on a trusted domain can be used to bypass domain blacklists in link filters, leading the user to the tabnapping payload.
- **SSRF:** While rare, if an SSRF endpoint renders returned content, it might be possible to inject tabnapping payloads into the rendered output.

## Related Notes
- [[04 - Cross-Site Scripting (XSS)]]
- [[12 - Open Redirects]]
- [[23 - Cross-Window Messaging Attacks]]

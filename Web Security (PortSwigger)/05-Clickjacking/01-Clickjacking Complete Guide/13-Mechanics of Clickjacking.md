---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Mechanics of Clickjacking

To fully comprehend clickjacking, it is essential to delve into the underlying mechanics of how this attack works. Clickjacking leverages the principles of CSS and HTML to create a deceptive layer that overlays legitimate content, tricking users into performing unintended actions.

### How Clickjacking Works

1. **Overlay Creation**: The attacker creates an invisible or nearly invisible overlay using CSS techniques such as `position`, `z-index`, and `opacity`. This overlay is positioned over the target element, such as a button or link, in the victim's web application.
   
2. **User Interaction**: When the user clicks on what they believe to be a legitimate element, they are actually clicking on the attacker's overlay. The attacker's overlay then triggers the intended action, such as logging out, changing settings, or executing a harmful script.

3. **Exploitation**: The attacker can use this technique to perform various malicious actions, such as stealing cookies, manipulating data, or gaining unauthorized access.

### Example Scenario

Consider a scenario where an attacker wants to trick a user into clicking a button that logs them out of their account. The attacker creates an invisible overlay over the logout button and positions it precisely over the button. When the user clicks what they think is a different button, they inadvertently trigger the logout action.

```html
<!-- Attacker's HTML -->
<div style="position:absolute; left:0; top:0; width:100%; height:100%; z-index:1000; opacity:0;">
  <button onclick="document.location.href='https://victim.com/logout';">Logout</button>
</div>

<!-- Victim's HTML -->
<button id="realButton">Click Me</button>
```

In this example, the attacker's overlay is positioned over the victim's button, making it appear as though the user is clicking on the real button. However, the actual click triggers the logout action.

### Real-World Examples

Several real-world examples illustrate the impact of clickjacking attacks:

- **CVE-2010-0188**: A clickjacking vulnerability was discovered in Adobe Reader and Acrobat, allowing attackers to trick users into installing malicious software.
- **CVE-2010-3337**: A clickjacking vulnerability in Microsoft Office allowed attackers to trick users into opening malicious files.

These examples highlight the potential severity of clickjacking attacks and the importance of implementing robust defenses.

---
<!-- nav -->
[[12-Hands-On Labs|Hands-On Labs]] | [[Web Security (PortSwigger)/05-Clickjacking/01-Clickjacking Complete Guide/00-Overview|Overview]] | [[14-Prevention Techniques for Clickjacking|Prevention Techniques for Clickjacking]]

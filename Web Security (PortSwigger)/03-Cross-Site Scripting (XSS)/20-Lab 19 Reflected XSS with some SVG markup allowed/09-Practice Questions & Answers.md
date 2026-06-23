---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the primary objective of the lab titled "Reflected XSS with some SVG markup allowed"?**

The primary objective of the lab is to exploit a reflected cross-site scripting (XSS) vulnerability that allows certain SVG tags and events. The goal is to perform an XSS attack that calls the `alert` function.

**Q2. How do you identify potential input fields vulnerable to reflected XSS?**

To identify potential input fields vulnerable to reflected XSS, you should look for any input fields where user-supplied data is echoed back in the response. For example, a search field where the search term is displayed in the page after submission. You can test this by entering a unique string and checking if it appears in the response.

**Q3. Why did the initial attempt to exploit the XSS vulnerability with a `<script>` tag fail?**

The initial attempt to exploit the XSS vulnerability with a `<script>` tag failed because the application has a filter or firewall that blocks common tags such as `<script>`. This indicates that the backend code is validating and sanitizing inputs to prevent common XSS attacks.

**Q4. How can you use Burp Suite Intruder to find allowed tags for performing an XSS attack?**

You can use Burp Suite Intruder to find allowed tags for performing an XSS attack by following these steps:

1. Send the request containing the input field to Intruder.
2. Set the payload position to replace the tag (e.g., `<script>`).
3. Use a list of tags from an XSS cheat sheet (such as the one provided by PortSwigger) as your payload list.
4. Run the attack and observe the responses. Tags that result in a successful response (e.g., HTTP 200 status code) instead of an error (e.g., HTTP 400 status code) are likely allowed.

Here’s an example payload list setup in Burp Suite Intruder:

```plaintext
<script>
<style>
<svg>
<image>
<title>
```

**Q5. Explain how you exploited the XSS vulnerability using SVG tags.**

To exploit the XSS vulnerability using SVG tags, follow these steps:

1. Identify that the application allows certain SVG tags and events.
2. Use an SVG tag that triggers a JavaScript event, such as `<svg onload="alert(1)">`.
3. Insert this payload into the input field and submit it.
4. The SVG tag will render in the browser, triggering the `onload` event, which executes the JavaScript code inside the `alert` function.

For example, the payload:

```html
<svg onload="alert(1)">
```

When submitted, will cause the browser to display an alert box with the number `1`, indicating a successful XSS attack.

**Q6. How can you ensure that your XSS attack is stealthy and avoids detection by security mechanisms?**

To ensure that your XSS attack is stealthy and avoids detection by security mechanisms, consider the following strategies:

1. **Use less common tags**: Instead of using common tags like `<script>`, use less common tags like `<svg>` or `<style>` that might not be blocked by the application's filters.
2. **Obfuscate the payload**: Encode the payload using techniques like Base64 encoding or HTML entity encoding to make it harder for simple pattern-matching filters to detect.
3. **Test with benign payloads**: Before launching a full attack, test with benign payloads that don’t trigger alerts or actions to ensure the payload structure is correctly interpreted by the application.

For example, an obfuscated payload might look like:

```html
<svg onload="eval(atob('YWxlcnQoMSk='))">
```

This uses Base64 encoding to hide the actual JavaScript code (`alert(1)`).

**Q7. Discuss a recent real-world example where SVG-based XSS was exploited.**

A notable example of SVG-based XSS exploitation occurred in the context of web applications that allowed users to upload images. In some cases, attackers could inject malicious SVG content within an image file, leading to XSS vulnerabilities.

For instance, in 2021, a vulnerability was discovered in a popular blogging platform where users could upload SVG files that contained embedded scripts. When other users viewed the blog posts containing these SVG images, the scripts would execute in their browsers, potentially stealing cookies or other sensitive information.

This type of attack highlights the importance of proper input validation and sanitization, especially when dealing with user-submitted content that could contain executable code.

---
<!-- nav -->
[[08-Understanding Reflected XSS|Understanding Reflected XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/20-Lab 19 Reflected XSS with some SVG markup allowed/00-Overview|Overview]]

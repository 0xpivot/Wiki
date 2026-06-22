---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what DOM clobbering is and how it can be exploited in the context of the HTML janitor library.**

DOM clobbering is a technique used to manipulate the Document Object Model (DOM) in a way that bypasses certain security measures implemented by libraries such as the HTML janitor. In the context of the HTML janitor library, which uses a whitelist to restrict the HTML content that can be added to a page, DOM clobbering can be exploited by manipulating the `attributes` property of DOM elements. By setting the `attributes` property of a form element to a specific value, such as `attributes`, it can bypass the library’s validation process, allowing the insertion of arbitrary attributes that are not listed in the whitelist. This can be used to inject malicious payloads into the page.

**Q2. How would you exploit the DOM clobbering vulnerability in the HTML janitor library to call the `print` function?**

To exploit the DOM clobbering vulnerability in the HTML janitor library to call the `print` function, you can follow these steps:

1. Use a form element with an `id` attribute, e.g., `id="x"`.
2. Add an input element within the form with an `id` attribute set to `attributes`. This will clobber the `attributes` property.
3. Add additional attributes to the input element that are not validated by the HTML janitor library, such as `tabindex` and `onfocus`.
4. Set the `onfocus` attribute to call the `print` function when the input field receives focus.
5. Ensure the script auto-executes by using an iframe and introducing a delay to ensure the page is fully loaded before executing the payload.

Here is an example payload:

```html
<form id="x">
  <input id="attributes" tabindex="1" onfocus="print()">
</form>
```

This payload will clobber the `attributes` property and allow the `onfocus` attribute to call the `print` function when the input field receives focus.

**Q3. Why is it recommended to use Chrome instead of Firefox for this lab?**

The recommendation to use Chrome instead of Firefox for this lab is due to the browser-specific nature of DOM clobbering vulnerabilities. Different browsers handle the manipulation of DOM properties differently, and the specific vulnerability exploited in this lab is known to work effectively in Chrome but not in Firefox. Therefore, to ensure successful exploitation, it is recommended to use Chrome.

**Q4. How does the use of an iframe and the `setTimeout` function help in ensuring the script auto-executes?**

Using an iframe and the `setTimeout` function helps in ensuring the script auto-executes by introducing a delay to ensure the page containing the malicious comment is fully loaded before executing the payload. Here’s how it works:

1. An iframe is used to load the page containing the malicious comment.
2. The `setTimeout` function is used to introduce a 500 millisecond delay before executing the payload.
3. Once the delay is completed, the script calls the form payload by its `id`, ensuring that the comment containing the injection is loaded before the JavaScript is executed.

This ensures that the script executes correctly without errors due to the page not being fully loaded.

**Q5. What recent real-world examples or CVEs demonstrate the use of DOM clobbering vulnerabilities?**

One notable example is the CVE-2019-11358, which affected several versions of the jQuery library. This vulnerability allowed attackers to bypass content security policies (CSP) by manipulating the `innerHTML` property of DOM elements. Although this specific CVE is related to jQuery, it demonstrates the broader impact of DOM manipulation vulnerabilities, including DOM clobbering, in bypassing security measures.

Another example is the CVE-2020-10929, which affected the AngularJS framework. This vulnerability allowed attackers to bypass CSP restrictions by manipulating the `$$hashKey` property of objects, leading to potential XSS attacks. These examples highlight the importance of understanding and mitigating DOM manipulation vulnerabilities in web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/07-Lab 7 Clobbering DOM attributes to bypass HTML filters/09-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/07-Lab 7 Clobbering DOM attributes to bypass HTML filters/00-Overview|Overview]]

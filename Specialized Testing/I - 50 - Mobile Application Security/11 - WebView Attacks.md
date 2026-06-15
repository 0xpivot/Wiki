---
tags: [mobile, android, ios, webview, pentesting]
difficulty: advanced
module: "50 - Mobile Application Security"
topic: "50.11 WebView Attacks"
---

# WebView Attacks

## Introduction
A **WebView** is an embedded browser component (`WebView`/`WKWebView` on Android/iOS) that renders web content inside a native app. WebViews are everywhere — hybrid apps, in-app browsers, help screens, OAuth flows — and they blur the native/web boundary. The danger is twofold: **(1)** insecure WebView settings (JavaScript enabled + file access + a **JS-to-native bridge**) can let loaded web content execute privileged native operations, and **(2)** loading attacker-controlled or unvalidated content (XSS, injected URLs from deep links) turns the WebView into a beachhead inside the app's sandbox. This note covers the WebView-specific bug classes on both platforms.

## The JavaScript Bridge (highest impact)
Apps expose native objects to JS so the web layer can call native code:
```java
// Android — addJavascriptInterface exposes a Java object to JS
webView.addJavascriptInterface(new NativeBridge(), "Android");
webView.getSettings().setJavaScriptEnabled(true);
// JS in the page can now call:  Android.someMethod(...)
```
```text
+---------------------------------------------------------------+
|                JS BRIDGE ABUSE                               |
+---------------------------------------------------------------+
|  attacker-controlled JS (XSS / loaded evil page / injected    |
|  deep-link URL)                                               |
|        |  calls the exposed bridge object's methods           |
|        v                                                       |
|  native code runs:  read files, get tokens, exec, exfil...    |
+---------------------------------------------------------------+
```
- **Android pre-4.2**: `addJavascriptInterface` exposed *all* public methods incl. reflection → trivial RCE (`getClass().forName(...)`). Modern Android requires `@JavascriptInterface` annotation, but **any exposed method is still callable by any JS** that runs in the WebView — so the risk is whatever those methods do (read storage, fetch tokens, call privileged APIs).
- **iOS WKWebView**: `WKScriptMessageHandler` (`window.webkit.messageHandlers.X.postMessage`) and `evaluateJavaScript` are the bridge equivalents — same "what does the handler do" analysis.

## Dangerous Settings
```text
   Android WebSettings:
     setJavaScriptEnabled(true)            (needed for bridge, raises risk)
     setAllowFileAccess(true)              file:// access
     setAllowFileAccessFromFileURLs(true)  file:// can read other files
     setAllowUniversalAccessFromFileURLs(true)  file:// -> any origin (BAD)
     loadUrl() of untrusted/HTTP content
   iOS WKWebView:
     allowFileAccessFromFileURLs / universal access prefs
     loading http:// (ATS exceptions)
```
`allowUniversalAccessFromFileURLs=true` + loading a `file://` page is especially bad: malicious local/remote content can read arbitrary app files and exfiltrate them.

## Loading Untrusted Content
WebViews become exploitable when they render content an attacker controls:
- **XSS in app-served web content** → runs in the WebView → calls the bridge / steals in-WebView data.
- **Injected URL via deep link** (`myapp://open?url=` — see [[09 - Android IPC and Intent Attacks]] / [[10 - iOS URL Schemes Deeplinks and Universal Links]]) → load attacker page.
- **HTTP/MITM content** (cleartext or pinning bypassed) → inject JS into the page.
- **`file://` traversal** → load a local file the attacker planted.

## Local File Theft Pattern
```text
   evil page in WebView (universal file access on)
        |  fetch('file:///data/data/<pkg>/shared_prefs/secrets.xml')
        v  read app's private files -> exfil via XHR to attacker
```

## Testing Workflow
```text
1. Find WebViews + settings: grep decompiled code for addJavascriptInterface,
   setJavaScriptEnabled, setAllowFileAccess*, WKScriptMessageHandler.
2. Enumerate bridge methods and what they DO (file/token/exec access?).
3. Find content injection: can you control a loaded URL (deep link),
   inject XSS, or MITM the content?
4. Chain: inject JS -> call bridge / read files -> exfil.
```

## Why It Matters
WebViews sit at the most dangerous seam in mobile apps: web content (easily attacker-influenced) wired to native capabilities (powerful). A single insecure bridge method plus any content-injection vector can yield file theft, token exfiltration, or code execution within the app's sandbox — and these patterns are extremely common in hybrid and OAuth-in-WebView apps.

## Defensive Notes
- Only enable JavaScript when required; **never expose powerful native methods** to the bridge — keep bridge surface minimal and authorize/validate every call.
- Disable file access (`setAllowFileAccess(false)`, never universal/file-URL access); load only **trusted HTTPS** content; validate/allow-list any dynamic URL.
- Use Android `@JavascriptInterface` minimally; on iOS scope `WKScriptMessageHandler`s tightly; sanitize/encode any app-rendered content to prevent XSS.
- Prefer native OAuth (ASWebAuthenticationSession / Custom Tabs) over hand-rolled WebView login.

## Related Notes
- [[09 - Android IPC and Intent Attacks]]
- [[10 - iOS URL Schemes Deeplinks and Universal Links]]
- [[08 - Insecure Data Storage]]
- [[12 - Network Interception and SSL Pinning Bypass]]

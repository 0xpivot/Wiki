---
tags: [c2, red-team, initial-access, phishing, vapt]
difficulty: intermediate
module: "101 - Red Team Initial Access and Payload Delivery"
topic: "101.01 Phishing Tradecraft and Pretexting"
---

# Phishing Tradecraft and Pretexting

## Introduction
Phishing is the dominant **initial access** vector in real-world intrusions and red-team engagements alike. Where the rest of this vault focuses on what happens *after* code execution, phishing is how the operator gets that first execution — by convincing a human to open an attachment, click a link, enter credentials, or approve an MFA prompt. Effective phishing is less about exploits and more about **pretexting** (a believable cover story), **infrastructure** (domains, senders, redirectors that survive reputation checks), and **payload delivery** that evades mail and endpoint defenses. This note covers the tradecraft; the specific payload mechanics live in [[02 - HTML Smuggling]], [[03 - ClickFix and Fake Verification Lures]], [[04 - Malicious Office Documents and Macros]], and [[05 - Windows Download and Execute Cradles]].

## The Phishing Kill Chain
```text
+---------------------------------------------------------------+
|                   PHISHING OPERATION FLOW                    |
+---------------------------------------------------------------+
|  1. RECON     OSINT -> targets, email format, tech stack      |
|  2. PRETEXT   believable scenario (IT, HR, vendor, invoice)   |
|  3. INFRA     domain + sender + landing/redirector + C2       |
|  4. LURE      email/SMS/chat with link or attachment          |
|  5. PAYLOAD   creds capture OR code execution                 |
|  6. ACCESS    session token / shell / MFA approval            |
+---------------------------------------------------------------+
```

## Pretexting
The pretext is the story that makes action feel routine and urgent:
- **Authority** — IT/security ("your account will be locked"), HR, an executive.
- **Familiarity** — a known vendor, an internal tool's notification, a shared-document alert.
- **Urgency/scarcity** — deadlines, failed payments, security alerts.
- **Plausible deniability for the click** — "review the attached invoice," "verify your login."
Recon (email format from [[24 - theHarvester]], LinkedIn, breach data) feeds a tailored pretext; the more specific to the target's real workflows, the higher the success rate.

## Infrastructure That Survives Reputation Checks
```text
   - Domains: aged or look-alike (typosquat/homoglyph); categorized
     (submit to URL categorization services so it's not "uncategorized")
   - Sender: SPF/DKIM/DMARC properly set on YOUR sending domain so mail
     isn't auto-junked; or abuse a compromised/trusted third party
   - Landing: redirectors filter sandboxes/AV crawlers; serve payload
     only to real victims (geo/UA/time/visited-link checks)
   - Separation: phishing infra != C2 infra (burn one, keep the other)
```
Tools: **GoPhish** / **Evilginx** (reverse-proxy phishing that captures *session cookies + MFA*, defeating MFA), **Modlishka**. Evilginx-style adversary-in-the-middle is the modern standard because it harvests live authenticated sessions, not just passwords.

## Delivery Channels
- **Email** — classic; attachment or link.
- **Smishing (SMS)** / **vishing (voice)** — bypass email controls, exploit mobile trust.
- **Chat / collaboration** (Teams, Slack, LinkedIn) — internal-looking, less filtered.
- **MFA fatigue / push bombing** — spam MFA approvals until the user accepts (pairs with captured credentials).
- **QR codes (quishing)** — move the click to a personal phone outside corporate controls.

## Credential Capture vs Code Execution
Two outcomes, chosen by objective:
1. **Credential / session capture** — a fake login (or Evilginx proxy) harvests username/password and the **session cookie**, sidestepping MFA. Best when you want account access (cloud, VPN, email).
2. **Code execution** — an attachment or download runs a payload (maldoc, HTML smuggling, LNK, ClickFix). Best when you want a foothold/shell on an endpoint → C2.

## Why It Matters
Most engagements that simulate real adversaries begin here; the strongest internal/AD attack chain is moot if you can't get the first foothold. Phishing also tests the human and email-security layers that technical controls don't cover, and modern AiTM phishing directly defeats the MFA organisations rely on.

## Defensive Notes
- Enforce **phishing-resistant MFA** (FIDO2/WebAuthn) — defeats AiTM cookie theft and push bombing; alert on impossible-travel / new-device sessions.
- Mail security: DMARC enforcement, external-sender banners, attachment detonation, link rewriting/time-of-click analysis.
- **Security awareness + easy reporting** ("report phish" button); simulate regularly.
- Restrict OAuth app consent; monitor for new look-alike domains (CT logs); block newly-registered/uncategorized domains at the proxy.

## Related Notes
- [[02 - HTML Smuggling]]
- [[03 - ClickFix and Fake Verification Lures]]
- [[04 - Malicious Office Documents and Macros]]
- [[05 - Windows Download and Execute Cradles]]
- [[24 - theHarvester]]

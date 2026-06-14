---
tags: [vapt, xs-leaks, xs-search, side-channel, cross-origin, advanced]
difficulty: advanced
module: "59 - XS-Leaks"
topic: "59.01 What are XS-Leaks (Cross-Site Leaks)"
---

# 59.01 — What are XS-Leaks (Cross-Site Leaks)?

## What is it?
**XS-Leaks** (Cross-Site Leaks), also called **XS-Search**, are a family of **side-channel** attacks that extract small pieces of information from a cross-origin site **without** ever reading its response directly. The Same-Origin Policy stops you from *reading* `bank.com`'s pages from `evil.com` — but it does **not** stop you from *observing side effects* of loading them: how long they took, whether an image `onload` or `onerror` fired, how many frames appeared, whether an error was thrown.

By repeatedly asking yes/no questions ("does the victim's inbox contain the word *acquisition*?") and reading the side channel for each answer, an attacker can **search** the victim's authenticated state one bit at a time — hence "XS-**Search**."

Think of a locked room you can't see into. You can't read what's inside, but you can knock and listen: a thud means furniture is there, silence means empty. Enough knocks in the right places and you map the whole room without opening the door.

## The 5 building blocks
Every XS-Leak combines these pieces:

| Component | Meaning |
|---|---|
| **Vulnerable Web** | Target site holding the victim's authenticated state |
| **Attacker's Web** | Page the victim visits that hosts the exploit |
| **Inclusion Method** | How the attacker loads the target (iframe, `window.open`, `fetch`, `<img>`, `<script>`…) |
| **Leak Technique** | The side channel read to distinguish states (event, timing, limits…) |
| **States** | The two conditions to tell apart (e.g. "search had results" vs "no results") |

The attack works when a **Detectable Difference** exists between the two states.

## Detectable differences (what leaks)
- **Status code** — server/client/auth errors differ cross-origin.
- **API usage** — whether the page uses a specific JS Web API.
- **Redirects** — HTTP, JS, or HTML-triggered navigations.
- **Page content** — response body size, number of embedded frames, image dimensions.
- **HTTP headers** — presence/value of `X-Frame-Options`, `Content-Disposition`, `Cross-Origin-Resource-Policy`, etc.
- **Timing** — consistent time differences between the two states.

## Inclusion methods (how to load the target)
- **HTML elements** — `<img>`, `<script>`, `<link rel=stylesheet>` force the browser to request a resource (see cure53/HTTPLeaks for the full list).
- **Frames** — `iframe`, `object`, `embed`. If the target lacks framing protection, JS can reach `contentWindow` / `frame.length`.
- **Pop-ups** — `window.open` returns a window handle and bypasses framing/cookie restrictions (but modern browsers gate pop-ups behind user gestures).
- **JavaScript requests** — `XMLHttpRequest` / `fetch`, with fine control (e.g. follow-redirect toggle).

## Leak techniques (how to read the channel)
- **Event handlers** — `onload` / `onerror` reveal load success/failure (the classic technique).
- **Error messages** — JS exceptions or special error pages distinguish states.
- **Global limits** — hitting a browser limit (memory, sockets, etc.) signals a threshold.
- **Global state** — e.g. the History interface entry count leaks cross-origin info.
- **Performance API** — `performance.now()` and resource timing infer what loaded.
- **Readable attributes** — a few attributes read cross-origin, e.g. `window.frame.length` counts frames.

## ASCII Diagram
```text
================================================================================
                          XS-LEAK / XS-SEARCH LOOP
================================================================================

  victim (logged into vulnerable-web) visits attacker-web
                         |
   for each guess g:     v
   +--------------------------------------------------+
   | 1. INCLUDE: load vulnerable-web/search?q=<g>      |
   |    via iframe / window.open / fetch / <img>       |
   | 2. LEAK: measure side channel                     |
   |    (onload vs onerror? time? frame count? error?) |
   | 3. STATE: difference => "g matches" / "no match"  |
   +--------------------------------------------------+
                         |
                         v
        reconstruct victim's private data bit-by-bit
================================================================================
```

## Timing-based measurement
Many XS-Leaks use time as the channel. Clocks an attacker can abuse:
- **Explicit:** `performance.now()` (high-resolution).
- **Implicit:** Broadcast Channel API, MessageChannel, `requestAnimationFrame`, `setTimeout`, CSS animations.

Timing leaks are powerful but **noisy, slow, and inaccurate** — often excluded from automated tooling for that reason.

## Tools
- **XSinator** ([xsinator.com](https://xsinator.com/)) — automatically tests a browser against many known XS-Leaks (paper: xsinator.com/paper.pdf). Note it *excludes* service-worker-based leaks, app-specific misconfig leaks (CORS, postMessage, XSS), and timing leaks.

## Defense
- **Framing protection:** `X-Frame-Options: DENY` / `Content-Security-Policy: frame-ancestors 'none'` blocks frame-based inclusion.
- **Cross-Origin isolation headers:**
  - `Cross-Origin-Opener-Policy: same-origin` (COOP) — severs `window.opener`, kills pop-up handle leaks.
  - `Cross-Origin-Resource-Policy: same-origin` (CORP) — blocks cross-origin resource embedding.
  - `Cross-Origin-Embedder-Policy: require-corp` (COEP).
- **SameSite cookies** (`Lax`/`Strict`) — stop the victim's cookies riding along with cross-site inclusions, removing the authenticated state the leak depends on.
- **Cache partitioning** and avoiding observable state differences (uniform error pages, padded responses).

## Related
- [[../I - 12 - CORS/01 - What is CORS]] — the policy XS-Leaks work *around*
- [[../I - 58 - Advanced Web Techniques/26 - XSSI (Cross-Site Script Inclusion)]] — sibling cross-origin data-leak vector
- [[../I - 28 - Clickjacking/06 - Defense — X-Frame-Options, CSP frame-ancestors]] — framing protection shared defense

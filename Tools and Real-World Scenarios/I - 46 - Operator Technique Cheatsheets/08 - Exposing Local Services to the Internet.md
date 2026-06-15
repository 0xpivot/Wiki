---
tags: [tools, post-exploitation, c2, pentesting, red-team]
difficulty: beginner
module: "46 - Operator Technique Cheatsheets"
topic: "46.08 Exposing Local Services to the Internet"
---

# Exposing Local Services to the Internet

## Introduction
Often you need a target (or a victim's browser) to **reach a service running on your local machine** that has no public IP — a reverse-shell listener, a payload/file server, a phishing page, an OAST/callback endpoint, or a webhook receiver. When you're behind NAT/CGNAT, on a home connection, or on a corporate VPN, you can't simply bind a public port. **Tunnel/exposure services** (ngrok, Cloudflare Tunnel, localtunnel, etc.) and reverse SSH solve this by giving your local port a public URL. This note covers the options and their trade-offs. (For pivoting *into* a network from a foothold, see instead [[03 - Tunneling and Port Forwarding]] — that's the inverse direction.)

## Direction: Local → Public
```text
+---------------------------------------------------------------+
|         EXPOSE LOCAL SERVICE  (you are behind NAT)           |
+---------------------------------------------------------------+
|  attacker localhost:8080  --(tunnel)-->  public URL           |
|        ^                                      |               |
|        |                                      v               |
|  your payload server / listener      target/victim reaches it |
+---------------------------------------------------------------+
```

## Options
### ngrok (quickest)
```bash
ngrok http 8080            # public HTTPS URL -> localhost:8080 (phishing page, payload server)
ngrok tcp 4444             # public TCP -> localhost:4444 (reverse-shell catcher)
```
Pros: instant, TLS, TCP+HTTP. Cons: random domains, account/limits, traffic transits a third party (and is visible to them) — avoid for sensitive client data.

### Cloudflare Tunnel (cloudflared)
```bash
cloudflared tunnel --url http://localhost:8080   # quick "TryCloudflare" URL, no account
```
Pros: free, no inbound ports, reputable domain (`*.trycloudflare.com`) that egress filters often allow — good for blending. Cons: HTTP-oriented.

### Reverse SSH to a VPS you own (most trustworthy)
If you control a VPS with a public IP, expose your local port via `-R` (no third party):
```bash
# on your machine: forward VPS:8080 -> your localhost:8080
ssh -R 8080:localhost:8080 user@your-vps
# target reaches  http://your-vps:8080
# (GatewayPorts yes on the VPS sshd to bind non-loopback)
```
Best operational security: traffic only touches infrastructure you own.

### Others
`localtunnel` (`lt --port 8080`), `serveo`, `bore`, `pinggy` — similar quick-URL services; same third-party caveat.

## Common Uses in Engagements
```text
   - Host a payload / second-stage:  python3 -m http.server  + tunnel
   - Catch a reverse shell from a target with only outbound web egress
   - Phishing landing page over HTTPS (clean cert, real URL)
   - OAST/callback for blind SSRF/XXE/RCE (or use Interactsh, note 29)
   - Receive webhooks / OAuth redirects during web testing
```

## Operational & Safety Notes
- **Third-party tunnels see your traffic.** Never route real client data or live credentials through ngrok/cloudflared free tiers — use your own VPS + TLS for sensitive work, and confirm it's within the rules of engagement.
- Public URLs are **internet-reachable by anyone** while up — scanners and bots will find them. Tear them down promptly; don't leave a payload server or open shell catcher exposed.
- For blind-vuln callbacks specifically, a purpose-built OAST service ([[29 - Interactsh Burp Collaborator]]) is cleaner than a raw tunnel.

## Why It Matters
Modern testers rarely have a public IP on hand; exposure tunnels are what make reverse shells, phishing, and OAST callbacks work from a laptop behind NAT. Choosing the right one (own-VPS for sensitive, cloudflared for egress-blending, ngrok for speed) is a routine setup decision with real OpSec and legal implications.

## Defensive Notes
- Block/inspect known tunnel domains (`*.ngrok.io`, `*.trycloudflare.com`, `*.loca.lt`) at the proxy; alert on internal hosts establishing outbound tunnels (a host *running* ngrok/cloudflared is a strong exfil/C2 indicator).
- Egress filtering + TLS inspection limits both inbound-callback and tunnel-based exfil.

## Related Notes
- [[03 - Tunneling and Port Forwarding]]
- [[01 - Reverse and Bind Shell Cheatsheet]]
- [[04 - Data Exfiltration Techniques]]
- [[29 - Interactsh Burp Collaborator]]

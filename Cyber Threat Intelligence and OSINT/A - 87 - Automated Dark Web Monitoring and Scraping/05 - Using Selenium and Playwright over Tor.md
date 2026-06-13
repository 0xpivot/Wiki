---
tags: [darkweb, scraping, automation, vapt]
difficulty: advanced
module: "87 - Automated Dark Web Monitoring and Scraping"
topic: "87.05 Using Selenium and Playwright over Tor"
---

# Using Selenium and Playwright over Tor

## 1. The Shift to Headless Browsers on the Dark Web

Historically, the Dark Web was synonymous with static, archaic HTML. JavaScript was universally shunned due to the catastrophic OpSec risks it presented to users (e.g., browser exploits, zero-days, or telemetry leaking the user's real IP address). Consequently, lightweight HTTP request libraries like Python's `requests` and parsers like `BeautifulSoup` were sufficient for almost all CTI scraping operations.

However, a paradigm shift is occurring. Modern ransomware leak sites, sophisticated darknet markets, and specialized initial access broker (IAB) platforms are increasingly utilizing heavy JavaScript frameworks (like React, Angular, or Vue.js) to build Single Page Applications (SPAs). Furthermore, advanced anti-bot protections now execute complex browser-fingerprinting scripts before serving content. 

When an analyst targets these modern `.onion` services, a simple HTTP GET request returns a blank page or a JavaScript execution error. To interact with, render, and scrape these targets, CTI teams must deploy full headless browser automation—specifically Selenium or Playwright—routed securely through the Tor network.

## 2. Tor Browser vs. Headless Chrome/Firefox

When automating browser interactions over Tor, analysts have two primary paths, each with distinct OpSec trade-offs.

### 2.1 Automating the Official Tor Browser
The official Tor Browser is heavily modified by the Tor Project to resist fingerprinting (it mitigates canvas fingerprinting, WebGL leaks, font enumeration, and normalizes the user agent). Using Selenium to directly drive the Tor Browser binary is the most secure OpSec approach.
**Pros:** Maximum OpSec, identical fingerprint to genuine human Tor users, minimal configuration required to prevent IP leaks.
**Cons:** Extremely difficult to scale in headless environments (like Docker), highly resource-intensive, and the Tor Browser frequently updates its geckodriver requirements, often breaking automation scripts.

### 2.2 Headless Playwright via SOCKS5 (The Industry Standard)
The more common, scalable approach for automated CTI operations is to use a standard Chromium or Firefox headless binary, specifically configured to route traffic through a local Tor daemon. The scraper simultaneously employs extensions and configuration flags to spoof a safe Tor Browser fingerprint.
**Pros:** Highly scalable, integrates perfectly with Docker and CI/CD pipelines, excellent debugging, and asynchronous capabilities.
**Cons:** Requires rigorous, meticulous configuration. A single missed flag can result in WebRTC IP leaks or DNS leakage.

## 3. Configuring Playwright over Tor

Playwright is rapidly superseding Selenium due to its asynchronous nature, superior speed, and deeper control over network interception. 

### 3.1 Critical Security Configurations
To safely route Playwright through Tor, you must strictly define the proxy and disable features like WebRTC, which can bypass proxies and reveal your true IP address via STUN/TURN server requests.

```python
import asyncio
from playwright.async_api import async_playwright

async def scrape_js_onion(url):
    async with async_playwright() as p:
        # Launch Firefox instead of Chromium. Tor Browser is based on Firefox, 
        # so spoofing a Firefox fingerprint is significantly more credible to WAFs.
        browser = await p.firefox.launch(
            headless=True,
            proxy={
                "server": "socks5://127.0.0.1:9050"
            },
            # Disable features that leak data
            args=[
                "--disable-webrtc",
                "--media.peerconnection.enabled=false"
            ]
        )
        
        # Context configuration is vital for OpSec
        context = await browser.new_context(
            # Mimic the current Tor Browser standard user agent
            user_agent="Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0",
            # Tor Browser always defaults to specific window sizes to prevent screen fingerprinting
            viewport={"width": 1280, "height": 720}, 
            # Tor Browser locks timezone to UTC to prevent local time leaks
            timezone_id="UTC", 
            locale="en-US",
            color_scheme="dark"
        )
        
        page = await context.new_page()
        
        print(f"[*] Navigating to {url} via Tor...")
        try:
            # High timeouts are required; JS-heavy onions load incredibly slowly over Tor
            await page.goto(url, timeout=90000, wait_until="networkidle")
            
            print("[+] Page loaded and JavaScript executed successfully.")
            
            # The DOM is now fully rendered. We can extract the HTML.
            rendered_html = await page.content()
            
            # Advanced interaction example:
            # await page.click("button#accept-rules")
            # await page.fill('input#search', 'ransomware')
            
            return rendered_html
            
        except Exception as e:
            print(f"[!] Browser automation failed: {e}")
        finally:
            await browser.close()

# Example Execution
# asyncio.run(scrape_js_onion("http://examplejsheavyonion.onion"))
```

## 4. Handling Complex Automation Flows

The primary advantage of headless browsers is their ability to automate complex interaction flows that are mathematically impossible with raw HTTP requests.

### 4.1 Authenticated Sessions and Local Storage
Many darknet markets require multi-step logins (Username -> Password -> PGP Decryption Challenge). Playwright can automate this entire flow, waiting dynamically for elements to appear. 
Furthermore, modern SPA markets store authentication tokens (like JWTs) in `localStorage` rather than standard HTTP cookies. A headless browser seamlessly handles this storage. By using `await context.storage_state(path="state.json")`, the script can export the browser's context state, allowing subsequent scraper runs to resume fully authenticated sessions without logging in again.

### 4.2 Intercepting Network Traffic (The XHR Hook)
Rather than parsing the complex, rendered HTML with BeautifulSoup, an elite technique using Playwright involves intercepting the underlying XHR/Fetch API requests the SPA makes to its backend.

```python
# Inside the Playwright async function, before navigation
async def log_response(response):
    # Intercept API calls the frontend makes to the backend
    if "api/v1/listings" in response.url and response.status == 200:
        print("[+] Intercepted JSON payload directly from the backend!")
        json_data = await response.json()
        # You can now save this pristine JSON directly to your database, 
        # bypassing the need for complex DOM parsing entirely.

page.on("response", log_response)
```

## 5. ASCII Diagram: Headless Browser Tor Routing Architecture

```text
+-------------------------------------------------------------------------+
|                  Headless Browser Tor Automation Stack                  |
+-------------------------------------------------------------------------+
       |
       v
+-----------------------------+
|    Python Automation Script |
|   (Playwright / Selenium)   |
+--------------+--------------+
               |  (CDP / WebDriver Protocol)
               v
+-----------------------------+
| Headless Firefox Instance   |  <--- JS Execution Engine Active
| - WebRTC Disabled           |  <--- User-Agent Spoofed
| - Canvas Fingerprint Spoof  |  <--- Timezone locked to UTC
+--------------+--------------+
               |  (SOCKS5 Proxy Configuration)
               v
+-----------------------------+
|       Tor Daemon (tor)      |  <--- Translates TCP/IP to Tor Cell Format
|       127.0.0.1:9050        |
+--------------+--------------+
               |
               v
+-----------------------------+
|         Tor Network         |
| (Entry -> Relay -> Target)  |
+--------------+--------------+
               |
               v
+-----------------------------+
|    JS-Heavy .onion Target   |
|     (e.g., React SPA)       |
+-----------------------------+
```

## 6. Real-World Attack Scenario

### Infiltrating a JS-Heavy Threat Actor Comms Channel

**Scenario:** A state-sponsored threat intelligence cell is monitoring a newly established Dark Web communications platform utilized by Initial Access Brokers (IABs). The platform is entirely built on Vue.js. A standard `requests` scrape returns nothing but `<div id="app"></div>`, making traditional scraping impossible.

**The Execution:**
1. **Deployment:** The cell deploys a Docker container running Playwright and a local Tor node.
2. **Execution & Rendering:** Playwright launches headless Firefox, routes through Tor, and navigates to the platform. It waits up to 60 seconds for the Vue.js framework to fetch its payloads, execute the JavaScript, and fully render the login page.
3. **Automated Interaction:** The script types a pre-established sock-puppet account's credentials into the DOM elements `input#user` and `input#pass` using human-like typing delays (`await page.type(..., delay=100)`).
4. **Bypassing Bot Detection:** The site employs a rudimentary mouse-movement heuristic. The Playwright script utilizes a custom helper function to generate bezier-curve mouse movements across the screen before clicking the "Login" button, successfully spoofing genuine human interaction.
5. **API Interception:** Once logged in, the platform loads chat messages dynamically via WebSocket. The Playwright script hooks into the `page.on("websocket")` event, silently intercepting, logging, and decrypting the raw JSON chat messages as they stream in. This feeds directly into an intelligence database in real-time, completely bypassing the need to scrape the frontend HTML.

## 7. Defensive Countermeasures
*   **Advanced Browser Fingerprinting:** Implement robust fingerprinting (e.g., checking WebGL rendering idiosyncrasies, font rendering limits, and hardware concurrency). Headless browsers often fail these checks, revealing their automated nature despite spoofing user agents.
*   **Behavioral Captchas:** Enforce human interaction challenges (like dragging a puzzle piece along an irregular path) that are mathematically difficult to automate smoothly enough to fool the detection algorithms.

## Chaining Opportunities
*   Headless browsers are perfectly suited for bypassing the visual anti-bot challenges discussed in [[03 - Defeating CAPTCHAs and Anti-Bot Protections]].
*   Use headless scraping to handle the login flow and extract session tokens, then pivot back to lightweight `requests` (as shown in [[02 - Routing Python Scripts through Tor Proxies]]) for the heavy-lifting scraping to save massive amounts of computational resources.

## Related Notes
*   [[01 - Challenges in Scraping the Dark Web]]
*   [[JavaScript Deobfuscation Techniques]]
*   [[OpSec for Covert Online Operations]]

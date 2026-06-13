---
tags: [darkweb, forums, marketplaces, leaks, vapt]
difficulty: intermediate
module: "84 - Dark Web Forums, Marketplaces, and Data Leaks"
topic: "84.10 Credit Card Carding Forums and Dumps"
---

# 84.10 Credit Card Carding Forums and Dumps

## Introduction
"Carding" is the illicit trafficking, trading, and fraudulent use of stolen credit card data. It is one of the oldest, most established, and most heavily monetized sectors of the cybercriminal underground. The carding ecosystem operates through specialized Dark Web marketplaces and forums entirely dedicated to the lifecycle of stolen financial data.

For Cyber Threat Intelligence (CTI) analysts, particularly those operating in the financial services (FINSEC) sector or e-commerce, understanding the carding ecosystem is paramount. It involves tracking how Point-of-Sale (POS) systems are breached, how e-commerce sites are skimmed, how the data is packaged ("Dumps" vs. "Fullz"), and the complex money laundering networks ("Cashout" operations) required to turn stolen plastic into usable currency.

## The Taxonomy of Stolen Credit Card Data

Stolen credit card information is categorized based on how it was stolen and what data points are included, which directly dictates its price and utility.

### 1. "Dumps" (Track 1 / Track 2 Data)
*   **What it is:** A "dump" refers specifically to the raw data encoded on the magnetic stripe of a physical credit card. 
    *   *Track 1:* Contains the Primary Account Number (PAN), cardholder name, expiration date, and format codes. It is highly structured (e.g., `%B123456789012345^SMITH/JOHN^24121010...`).
    *   *Track 2:* Contains the PAN, expiration date, and service codes (no name). This is the minimum data required for an ATM withdrawal or POS transaction.
*   **Source:** Dumps are almost exclusively obtained by compromising physical Point-of-Sale (POS) terminals using specialized POS malware (e.g., BlackPOS, Alina) or physical hardware skimmers (Deep Insert Skimmers / Shimmers) attached to ATMs and gas pumps.
*   **Usage:** Dumps are used to create cloned physical credit cards. A carder uses a Magnetic Stripe Writer (MSR hardware) to write the Track data onto a blank plastic card, then uses it for in-store purchases or ATM cashouts.

### 2. "CVV" or "Cards" (Card-Not-Present Data)
*   **What it is:** This refers to the standard details required for online shopping: PAN, Expiration Date, and the Card Verification Value (CVV code on the back).
*   **Source:** Stolen via e-commerce breaches, phishing campaigns, or most prominently, Digital Skimming / Magecart attacks.
*   **Usage:** Used exclusively for Card-Not-Present (CNP) transactions—i.e., online shopping, purchasing gift cards, or buying services.
*   **Value:** Cheaper than dumps due to the high rate of decline by fraud-prevention systems when anomalies are detected in shipping addresses or IP geolocation.

### 3. "Fullz"
*   **What it is:** The holy grail of financial identity theft. "Fullz" (Full Information) contains the credit card data plus the victim's complete personally identifiable information (PII). This includes Date of Birth, Social Security Number (SSN), Mother's Maiden Name, and complete address history.
*   **Source:** Extensive database breaches, complex phishing operations, or aggregated by combining data from multiple distinct breaches.
*   **Usage:** Used for total identity theft. Taking out loans, opening new credit lines, bypassing intense anti-fraud verification, and hijacking bank accounts.

---

## The Dark Web Carding Infrastructure

Carding is a highly specialized economy. Threat actors rarely perform the entire lifecycle from hack to cashout. Instead, it is heavily compartmentalized.

### Carding Forums and Marketplaces
Sites like the infamous (and now defunct) *Joker's Stash*, *Bypass Shop*, or *Brian's Club* operate as massive automated vending machines.
*   **Automated Checking:** Marketplaces offer automated "checkers." Before a buyer completes a purchase, the site silently runs a tiny authorization charge (often against a charity or low-profile merchant) to guarantee the card is "Live" (not yet cancelled).
*   **Geographic Filtering:** Buyers can filter dumps by BIN (Bank Identification Number), country, state, or even zip code. If a carder is cashing out physically in Miami, they need to buy dumps that originated from Miami banks to avoid triggering travel alerts.

### The Cashout Operation (The Riskiest Phase)
Turning a stolen credit card number into anonymous Bitcoin requires a complex operational security (OpSec) chain.

1.  **Drops:** A carder buys a physical item (e.g., a MacBook) online using a stolen CVV. They cannot ship it to their own house. They ship it to a "Drop"—a compromised or vacant address, or an address owned by an unwitting participant.
2.  **Mules:** Money Mules or Reshippers are individuals (often recruited via work-from-home scams) who receive the stolen goods at the Drop address. The Mule is instructed to repackage the goods and ship them to the actual carder (often overseas).
3.  **Fencing:** The carder receives the MacBook and sells it on a local secondary market (like eBay or local classifieds) for cash, which is then converted into cryptocurrency.
4.  **Gift Card Laundering:** A faster, fully digital method. The carder uses the stolen CVV to buy high-liquidity digital gift cards (Amazon, iTunes). They then sell those gift cards at a discount on legitimate cryptocurrency peer-to-peer exchanges (like Paxful) for Bitcoin.

---

## The ASCII Carding Lifecycle

```text
+-----------------------+      +-----------------------+
|  The Vendor / Hacker  |      |   The Marketplace     |
|  (Injects Magecart    |      |   (Joker's Stash /    |
|  into E-Commerce site)|      |   Brian's Club)       |
+-----------+-----------+      +-----------+-----------+
            |                              ^
            | (Extracts CVV/Fullz)         | (Sells Data in Bulk)
            v                              |
+-----------------------+      +-----------+-----------+
|  Victim Checkout      |      |  The Carder (Buyer)   |
|  (Enters CC Details)  |      |  (Purchases Live CVV  |
|                       |      |  using Bitcoin)       |
+-----------------------+      +-----------+-----------+
                                           |
                                           | (Purchases High-Value Goods)
                                           v
+-----------------------+      +-----------------------+
| Legitimate Retailer   |      |  The Drop / Mule      |
| (Apple, Amazon,       +----->+  (Receives Stolen     |
|  Best Buy)            |      |  Goods at local addr) |
+-----------------------+      +-----------+-----------+
                                           |
                                           | (Reships Goods Overseas)
                                           v
+-----------------------+      +-----------------------+
| Cryptocurrency        |      |  The Fencer           |
| Tumbler / Mixer       +<-----+  (Sells Goods Locally |
| (Launders Funds)      |      |  for Cash/Crypto)     |
+-----------------------+      +-----------------------+
```

---

## Real-World Attack Scenario

### The Modern Shift: Magecart and Digital Skimming

Physical POS malware is declining due to the global rollout of EMV (Chip and PIN) standards, which shifted liability to merchants and made cloning physical cards immensely difficult because the chip generates a unique, one-time cryptogram for every transaction. As a result, the carding economy has pivoted heavily to **Magecart (Digital Skimming)**.

1.  **Initial Access:** Attackers hack the web server of a mid-sized e-commerce site, often by exploiting a vulnerable Magento, WooCommerce, or PrestaShop plugin.
2.  **The Skimmer:** They inject a few lines of heavily obfuscated malicious JavaScript into the HTML of the checkout page.
3.  **The Skim:** When a customer types their credit card details into the legitimate form and clicks "Submit," the malicious JavaScript executes in the victim's browser.
4.  **Exfiltration:** The script silently copies the inputted PAN, Expiry, and CVV, and asynchronously POSTs it to a drop server controlled by the attacker. Simultaneously, the legitimate transaction processes normally with the merchant.
5.  **Monetization:** The victim, the merchant, and the payment processor remain completely unaware of the compromise. The attackers aggregate thousands of these CVVs and sell them in bulk on forums, fueling the CNP fraud ecosystem.

---

## Defense and Mitigation Strategies

1.  **PCI-DSS Compliance:** Strict adherence to Payment Card Industry Data Security Standards. Implementing robust segmentation between corporate networks and Cardholder Data Environments (CDE).
2.  **Subresource Integrity (SRI) & Content Security Policy (CSP):** To combat Magecart, e-commerce sites must implement strict CSPs to prevent unauthorized external scripts from loading or sending data to unknown domains. SRI ensures that third-party scripts (like analytics or chat widgets) have not been tampered with.
3.  **EMV Adoption / Tokenization:** For physical retail, fully enforcing Chip-and-PIN and disabling fallback to magnetic stripe. Utilizing tokenization (Apple Pay, Google Pay) where the actual PAN is never transmitted to the merchant.
4.  **Behavioral Fraud Analytics:** Financial institutions must rely on advanced behavioral analytics. If a card that historically only buys groceries in Ohio suddenly purchases $2000 in Steam Gift cards from an IP address resolving to a VPN in Romania, the transaction must be instantly flagged.
5.  **Threat Intel / BIN Monitoring:** CTI teams at banks actively monitor carding marketplaces. They look for "Bases" (batches of cards) being advertised. If they identify a pattern—e.g., thousands of cards originating from a specific regional supermarket chain are suddenly for sale—they can preemptively cancel those cards.

---

## Chaining Opportunities
*   Attackers exploit vulnerabilities in **[[04 - External Attack Surface Management EASM]]** to breach e-commerce infrastructure.
*   They deploy web shells and establish **[[17 - Command and Control C2 Frameworks]]** to maintain access to the webserver.
*   They inject Magecart scripts to harvest CVVs, which are then sold on specialized hubs akin to **[[07 - Data Breach Forums BreachForums Alternatives]]**.

## Related Notes
*   [[07 - Data Breach Forums BreachForums Alternatives]]
*   [[24 - Web Application Vulnerabilities Advanced]]
*   [[05 - Threat Actor Profiling and Attribution]]
*   [[42 - Egress Filtering and Data Exfiltration Prevention]]

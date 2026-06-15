---
tags: [blockchain, web3, wallets, phishing, pentesting]
difficulty: intermediate
module: "52 - Blockchain and Smart Contract Security"
topic: "52.08 Web3 Signing and Wallet Workflow Compromise"
---

# Web3 Signing and Wallet Workflow Compromise

## Introduction
Many real-world crypto losses don't come from smart-contract bugs at all — they come from tricking **users into signing malicious things**. In Web3, a signature can authorize transferring all your tokens, granting unlimited spending allowance, or — in multisig/smart-account contexts — executing a `delegatecall` that takes over the wallet. Because signing UX is confusing and signatures are powerful, **signing-workflow compromise** (malicious dApps, phishing, approval drains, blind signing, Safe/multisig delegatecall takeover) is one of the highest-impact and most common attack vectors. This note covers wallet/signing abuse — the human-facing and workflow side of Web3 security.

## Why Signatures Are Dangerous
```text
+---------------------------------------------------------------+
|              WHAT A SIGNATURE CAN AUTHORIZE                  |
+---------------------------------------------------------------+
|  - a transaction (send funds, call a contract)               |
|  - ERC-20 approve / Permit (allow a spender to move tokens)  |
|  - setApprovalForAll (let an operator move ALL your NFTs)    |
|  - EIP-712 typed data (often signed "blind" / unreadable)    |
|  - multisig/Safe: approve a tx incl. delegatecall to ANY code|
+---------------------------------------------------------------+
```
Users frequently **blind-sign** opaque payloads in their wallet, unable to tell a benign action from a wallet-draining one.

## Attack Classes
### 1. Approval / allowance drains
The dominant wallet-drainer technique: a malicious dApp asks the user to `approve` (or `Permit`) a token spend — often **unlimited** — to an attacker-controlled spender. The user thinks they're "connecting" or doing a small action; the attacker then `transferFrom`s all approved tokens later. `setApprovalForAll` does the same for an entire NFT collection.

### 2. Permit / Permit2 signature phishing
**EIP-2612 Permit** and **Permit2** let approvals happen via an off-chain **signature** (gasless). Phishing a single Permit signature grants spending rights without any on-chain transaction the user notices — extremely popular with drainers.

### 3. Blind signing / typed-data deception
Hardware wallets and dApps often show raw or poorly-decoded **EIP-712** data. Attackers craft payloads that look benign but authorize transfers/approvals; users sign without understanding.

### 4. Safe / multisig delegatecall takeover
Smart-contract wallets like **Safe (Gnosis)** can execute transactions with `operation = delegatecall`. If signers are tricked into approving a transaction that **delegatecalls attacker code**, that code runs in the Safe's storage context ([[04 - Proxy and Delegatecall Vulnerabilities]]) — it can change owners/modules and **take over the entire multisig** and its funds. This is the "web3 signing workflow compromise → Safe delegatecall proxy takeover" class: the exploit is getting enough signers to approve a malicious delegatecall.

### 5. Malicious dApp / WalletConnect session abuse
A connected dApp (or a hijacked one, or a malicious WalletConnect session) repeatedly requests signatures; address-poisoning and clipboard-swap tricks redirect funds; fake airdrops/mints lure connections.

## Testing / Assessment Workflow
```text
1. For a dApp: what does it ask users to sign? Are approvals scoped
   (exact amount) or UNLIMITED? Is Permit used? Is the typed data
   clearly presented?
2. For multisig/Safe setups: are delegatecall transactions possible/
   used? Could signers be socially-engineered into a malicious
   delegatecall? Are modules/guards restricting this?
3. Frontend integrity: can the dApp UI be tampered (supply-chain, DNS,
   XSS) to swap the signing payload? (off-chain web security applies)
4. Simulate signatures (Tenderly/transaction simulation) to reveal true
   effect before signing.
```

## Why It Matters
Wallet-draining via malicious signatures is responsible for vast, ongoing user losses and is far more common than novel contract exploits — it needs no protocol bug, only a deceived user. The Safe delegatecall takeover class extends this to high-value multisigs (treasuries, DAOs). For testers, the dApp's **signing UX and the multisig's delegatecall policy** are core attack surface, intertwined with ordinary web security of the frontend.

## Defensive Notes
- **Scope approvals** to exact amounts (avoid unlimited); revoke stale approvals (revoke.cash); use allowance/Permit2 carefully.
- **Clear-signing**: wallets/dApps should decode and display the true effect of transactions/typed data; users should never blind-sign; use transaction simulation.
- **Multisig/Safe**: disallow or tightly guard `delegatecall` (use a guard/module allowlist); require signer scrutiny of `operation` field; verify the target of any delegatecall.
- Secure the dApp frontend (supply chain, integrity, anti-phishing); educate users on approval drains and address poisoning.

## Related Notes
- [[04 - Proxy and Delegatecall Vulnerabilities]]
- [[07 - ERC-4337 Account Abstraction Security]]
- [[01 - Blockchain and Web3 Security Overview]]
- [[01 - Phishing Tradecraft and Pretexting]]

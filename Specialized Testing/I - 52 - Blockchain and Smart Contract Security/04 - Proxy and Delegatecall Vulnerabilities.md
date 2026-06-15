---
tags: [blockchain, smart-contracts, proxy, delegatecall, pentesting]
difficulty: advanced
module: "52 - Blockchain and Smart Contract Security"
topic: "52.04 Proxy and Delegatecall Vulnerabilities"
---

# Proxy and Delegatecall Vulnerabilities

## Introduction
Smart contracts are immutable, so to make them **upgradeable**, developers use the **proxy pattern**: a proxy contract holds the storage and funds and **`delegatecall`s** to a separate logic/implementation contract. `delegatecall` executes the target's code **in the caller's storage context** — which is exactly what makes upgrades possible and also what makes this a dangerous, high-impact bug class. Storage-layout collisions, uninitialized implementations, and delegatecall to untrusted targets have caused some of the largest losses in Web3 (including Safe/multisig and Wormhole-class incidents). This note covers how proxies work and how they break.

## How delegatecall / Proxies Work
```text
+---------------------------------------------------------------+
|                    PROXY + DELEGATECALL                      |
+---------------------------------------------------------------+
|  User -> PROXY (holds storage + funds)                        |
|             | delegatecall(implementation, calldata)          |
|             v                                                 |
|  IMPLEMENTATION code runs, BUT reads/writes the PROXY's       |
|  storage and uses the PROXY's address/balance/msg.sender.     |
|  Upgrade = point the proxy at a new implementation address.   |
+---------------------------------------------------------------+
```
The key, counter-intuitive rule: `delegatecall` runs the *callee's code* against the *caller's storage*. Storage slots are referenced by position, so the proxy and implementation **must agree on storage layout**.

## Vulnerability Classes
### 1. Storage collision
If the proxy and implementation declare state variables in incompatible slot orders, the implementation writes over the proxy's critical variables (e.g. overwriting the `admin`/`implementation` slot). Modern proxies use **EIP-1967** fixed pseudo-random slots for admin/implementation to avoid collisions; hand-rolled proxies frequently get this wrong, letting an attacker overwrite the admin pointer and seize control.

### 2. Uninitialized implementation / proxy
Upgradeable contracts use an `initialize()` (not a constructor, since constructors don't run in the proxy's context). If the **implementation** contract is left uninitialized, an attacker can call `initialize()` on it directly, become its "owner," and — if the implementation has a `selfdestruct`/`delegatecall` path — **destroy the logic contract**, bricking every proxy pointing at it (the Parity multisig freeze, ~$280M). Uninitialized proxies can likewise be hijacked.

### 3. delegatecall to untrusted/attacker-controlled target
If a contract `delegatecall`s to an address an attacker can influence, the attacker's code runs **in the victim's storage context** — it can overwrite any storage (including owner), drain funds, or `selfdestruct` the contract. This is the basis of the **Safe/Gnosis delegatecall proxy takeover** class: abusing a delegatecall in a signing/module workflow to take over the account/proxy.

### 4. Function selector clashes
Proxy admin functions and implementation functions can share a 4-byte selector, causing calls meant for one to hit the other (transparent-proxy pattern addresses this by routing admin vs user calls).

```text
   attacker goals via proxy/delegatecall bugs:
     overwrite the ADMIN/implementation slot -> upgrade to malicious logic
     initialize an uninitialized impl -> own/selfdestruct it -> brick proxies
     delegatecall to attacker code -> arbitrary storage write -> drain/own
```

## Testing Workflow
```text
1. Identify proxy pattern (Transparent/UUPS/Beacon/Diamond) and where
   delegatecall is used.
2. Compare storage layouts of proxy vs implementation -> collisions?
   Are EIP-1967 slots used for admin/impl?
3. Is the implementation initialized? Can initialize() be called by
   anyone? Any selfdestruct/delegatecall in the impl?
4. Does any delegatecall target an address attacker can influence?
5. Check UUPS upgrade authorization (_authorizeUpgrade) and selector
   clashes; exploit on a fork ([[09]]).
```

## Why It Matters
Proxies sit in front of the most valuable protocols (they hold the funds), and delegatecall's storage-context behaviour makes its bugs **total compromise** — overwrite the admin, brick the logic, or drain everything. The pattern is subtle and frequently hand-rolled incorrectly, making it a recurring source of catastrophic, headline losses.

## Defensive Notes
- Use **audited proxy libraries** (OpenZeppelin Transparent/UUPS proxies) with **EIP-1967** storage slots; never hand-roll proxy storage layout.
- **Disable initializers on implementation contracts** (`_disableInitializers()` in the constructor) so they can't be initialized/hijacked; protect `initialize()` with `initializer`.
- Restrict and authorize upgrades (`_authorizeUpgrade` onlyOwner in UUPS); never `delegatecall` to untrusted/attacker-influenceable addresses.
- Maintain strict storage-layout compatibility across upgrades; use storage-gap patterns and upgrade-safety tooling.

## Related Notes
- [[03 - Common Solidity Vulnerabilities]]
- [[08 - Web3 Signing and Wallet Workflow Compromise]]
- [[02 - Smart Contract Reentrancy]]
- [[09 - Smart Contract Auditing Tools and Methodology]]

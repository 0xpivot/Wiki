---
tags: [blockchain, web3, smart-contracts, pentesting, methodology]
difficulty: beginner
module: "52 - Blockchain and Smart Contract Security"
topic: "52.01 Blockchain and Web3 Security Overview"
---

# Blockchain and Web3 Security Overview

## Introduction
Web3 systems — cryptocurrencies, smart contracts, DeFi protocols, NFTs, bridges, and wallets — carry real, often enormous, value directly in code, with **immutable, public, irreversible** execution. A bug is not a data breach you patch next sprint; it is funds drained permanently in one transaction, with the exploit visible on-chain forever. This changes the security model: the code *is* the bank, anyone can call it, and there is no undo. This note frames the blockchain attack surface and the testing mindset that the rest of the module builds on.

## How the EVM Model Works (briefly)
```text
+---------------------------------------------------------------+
|                  ETHEREUM / EVM BASICS                       |
+---------------------------------------------------------------+
|  Accounts: EOAs (user, private-key) + Contracts (code)        |
|  Smart contract: code + storage deployed at an address;       |
|     ANYONE can call its public/external functions             |
|  Transactions: signed by an EOA, cost GAS, are public in the  |
|     mempool before mining (front-runnable)                    |
|  State: global, transparent; execution is deterministic and   |
|     IRREVERSIBLE once mined                                   |
+---------------------------------------------------------------+
```
Most smart contracts are written in **Solidity** (compiled to EVM bytecode). Key consequences for security:
- **Public callable surface** — every external function is an entry point for any attacker.
- **Composability** — contracts call each other; your contract's safety depends on the contracts it interacts with (and vice-versa).
- **Money in the loop** — value is transferred by code paths, so logic bugs = direct theft.
- **Public mempool** — pending transactions are visible, enabling front-running/MEV.

## The Web3 Attack Surface
```text
   SMART CONTRACTS  reentrancy, access control, arithmetic, logic,
                    proxy/delegatecall ([[02]]-[[04]])
   DeFi PROTOCOLS   price/oracle manipulation, flash loans, AMM math
                    ([[05]],[[06]])
   ACCOUNT/WALLET   signing workflow abuse, approval drains, key mgmt,
                    ERC-4337 account abstraction ([[07]],[[08]])
   INFRASTRUCTURE   bridges (frequent mega-hacks), RPC nodes, oracles
   OFF-CHAIN        the dApp frontend, APIs, keys in CI -> still normal
                    web/API/secrets bugs
```

## Testing Mindset & Workflow
```text
1. Get the code: contracts are often verified on Etherscan (source
   available) — read them. If only bytecode, decompile.
2. Map entry points: every external/public function; who can call it;
   what value/state it touches.
3. Reason about money flow + trust: where do funds move? what external
   contracts/oracles are trusted? what assumptions can be broken?
4. Hunt vuln classes ([[02]]-[[08]]); model an attacker contract that
   calls the target.
5. Test on a FORK: use Foundry/Hardhat to fork mainnet state and
   exploit locally (never test on mainnet with real funds) ([[09]]).
6. Off-chain: assess the dApp frontend, APIs, and key handling.
```
Critically, much testing happens on a **local mainnet fork** so you can attempt exploits against real protocol state safely and for free.

## Why It Matters
Web3 has lost billions to smart-contract and bridge exploits; the immutability and direct-value properties make it the highest-stakes, least-forgiving application security domain. Auditing skills here translate to bug bounties with very large payouts and to protecting protocols where a single missed reentrancy or access-control bug is catastrophic.

## Defensive Notes
- **Audits + formal verification + invariant/fuzz testing** before deploy ([[09]]); assume the code is the final security boundary.
- Follow established patterns (checks-effects-interactions, reentrancy guards, OpenZeppelin libraries); minimize trust in external contracts/oracles.
- Plan for upgradeability **safely** ([[04]]) and have pause/emergency mechanisms and bug-bounty programs; monitor on-chain activity.

## Related Notes
- [[02 - Smart Contract Reentrancy]]
- [[03 - Common Solidity Vulnerabilities]]
- [[05 - DeFi and AMM Exploitation]]
- [[08 - Web3 Signing and Wallet Workflow Compromise]]
- [[09 - Smart Contract Auditing Tools and Methodology]]

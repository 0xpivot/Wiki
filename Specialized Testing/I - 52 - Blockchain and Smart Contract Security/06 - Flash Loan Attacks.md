---
tags: [blockchain, defi, flash-loans, pentesting]
difficulty: advanced
module: "52 - Blockchain and Smart Contract Security"
topic: "52.06 Flash Loan Attacks"
---

# Flash Loan Attacks

## Introduction
A **flash loan** lets anyone borrow a huge amount of assets **with no collateral**, on the condition that the loan is **repaid within the same transaction** — otherwise the entire transaction reverts (atomicity guarantees the lender can't lose). This is a legitimate DeFi primitive (arbitrage, refinancing), but it's also the great **amplifier of DeFi exploits**: it gives any attacker, momentarily, the capital of a whale. Combined with price-oracle manipulation, governance, or accounting bugs, flash loans turn "you'd need millions to exploit this" into "anyone can, for a few dollars of gas." This note covers how flash-loan attacks are constructed.

## How a Flash Loan Works
```text
+---------------------------------------------------------------+
|                   FLASH LOAN (atomic)                        |
+---------------------------------------------------------------+
|  In ONE transaction:                                          |
|   1. borrow X (e.g. 100M USDC) from a pool (Aave/dYdX/etc.)   |
|   2. attacker's contract executes arbitrary logic with X       |
|   3. repay X + fee                                            |
|   If step 3 fails -> WHOLE tx reverts (as if nothing happened)|
|   -> lender bears no risk; borrower needs no collateral       |
+---------------------------------------------------------------+
```

## The Attack Pattern
Flash loans don't exploit anything by themselves; they **fund** an exploit of *another* protocol's flaw:
```text
   borrow huge amount
        |
        +--> MANIPULATE: skew an AMM spot price the target trusts
        |        ([[05]]) -> over-borrow/mint/liquidate on the target
        +--> GOVERNANCE: borrow governance tokens -> pass a malicious
        |        proposal in protocols with instant voting
        +--> ACCOUNTING: trigger share-inflation/rounding bugs at scale
        |
   profit from the target's flaw
        |
   repay loan + fee, keep the difference   (all atomic)
```
The canonical chain is **flash loan → oracle manipulation → drain** (see [[05 - DeFi and AMM Exploitation]]). Numerous nine-figure hacks follow this template.

## Example Flow (oracle manipulation)
```text
1. Flash-borrow 50M of token B.
2. Dump it into a small AMM pool that the target lending protocol uses
   as its price oracle -> token A's price (in B) spikes/crashes.
3. On the target: deposit a little token A as collateral now valued
   absurdly high -> borrow far more than its real worth.
4. Reverse the AMM swap to recover most of the borrowed B.
5. Repay the flash loan + fee; walk away with the over-borrowed funds.
   All in one transaction.
```

## Testing Workflow
```text
1. Determine: does any exploit you found require large capital? If so,
   a flash loan likely removes that barrier -> reassess severity.
2. Identify flash-loan sources (Aave, Balancer, dYdX, Uniswap flash
   swaps) available for the assets involved.
3. Build a single attacker contract: borrow -> exploit (manipulate/
   govern/inflate) -> repay; ensure atomic profitability.
4. Test on a mainnet FORK ([[09]]) with realistic liquidity.
5. Check the target's defenses: TWAP oracles, flash-loan guards,
   per-block action limits, governance timelocks.
```

## Why It Matters
Flash loans **democratize** capital-intensive attacks: a vulnerability that would require a wealthy attacker becomes exploitable by anyone for the cost of gas. They've been the funding mechanism behind many of DeFi's largest exploits. For testers, the rule is: **any economic vulnerability must be evaluated assuming the attacker has unlimited momentary capital** — that often turns a "theoretical" finding into a critical one.

## Defensive Notes
- **Don't trust manipulable spot prices** — use TWAP/decentralized oracles so a single-tx price swing can't fool the protocol ([[05]]).
- Add **flash-loan awareness**: per-block action limits, timelocks/snapshots for governance (so borrowed voting power can't pass instant proposals), and checks that deposits/borrows in the same tx as large swaps are bounded.
- Design economic invariants that hold even under unlimited momentary capital; fuzz/invariant-test with simulated flash loans ([[09]]).

## Related Notes
- [[05 - DeFi and AMM Exploitation]]
- [[03 - Common Solidity Vulnerabilities]]
- [[01 - Blockchain and Web3 Security Overview]]
- [[09 - Smart Contract Auditing Tools and Methodology]]

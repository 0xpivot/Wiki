---
tags: [blockchain, smart-contracts, auditing, tooling, pentesting]
difficulty: intermediate
module: "52 - Blockchain and Smart Contract Security"
topic: "52.09 Smart Contract Auditing Tools and Methodology"
---

# Smart Contract Auditing Tools and Methodology

## Introduction
Smart-contract review combines **manual reading** (the most important part), **static analysis**, **fuzzing/invariant testing**, **mutation testing**, and **fork-based exploitation**. Because deployed code is immutable and holds funds, the goal is to find issues *before* deployment (audit) or to prove exploitability safely (research/bounty) without risking real assets. This note covers the toolchain and a repeatable methodology, tying together the vuln classes from the rest of the module.

## The Toolchain
```text
+---------------------------------------------------------------+
|                 SMART-CONTRACT AUDIT TOOLS                   |
+---------------------------------------------------------------+
| Static analysis   Slither (Solidity static analyzer),        |
|                   Mythril (symbolic), Semgrep rules           |
| Dev/test/fuzz     Foundry (forge: fast tests + fuzzing +      |
|                   invariant testing + mainnet fork),          |
|                   Hardhat, Echidna (property fuzzing),        |
|                   Medusa                                      |
| Symbolic/formal   Manticore, Certora (formal verification),  |
|                   halmos (symbolic via Foundry)              |
| Mutation testing  slither-based / vertigo -> tests the TESTS  |
| Decompile         (unverified bytecode) Panoramix, Dedaub     |
| Simulation        Tenderly (tx simulation/debug), forks       |
+---------------------------------------------------------------+
```

### Slither (start here)
Fast static analysis catching many known patterns:
```bash
slither .                          # run all detectors on a project
slither . --print human-summary    # overview
slither . --print inheritance-graph
# flags: reentrancy, unchecked calls, tx.origin, shadowing,
#        uninitialized state/proxies, arbitrary-send, etc.
```
Triage Slither output (some findings are false positives), then manually verify the real ones.

### Foundry (test + fuzz + fork)
The modern workhorse for exploitation and invariant testing:
```bash
forge test                                    # run tests
forge test --match-test testExploit -vvvv     # verbose trace of an exploit PoC
# fuzzing: parameters are randomized
# invariant testing: assert protocol invariants hold under random calls
forge test --fork-url $RPC_URL                # FORK mainnet state -> exploit
```
Writing an exploit as a Foundry test against a **mainnet fork** is the standard way to prove a DeFi/flash-loan exploit ([[06 - Flash Loan Attacks]]) safely.

### Echidna / property fuzzing & mutation testing
- **Echidna/Medusa**: define invariants (e.g. "total shares == sum of balances", "no user can withdraw more than deposited") and fuzz thousands of call sequences to break them — excellent for the accounting/precision bugs in [[05 - DeFi and AMM Exploitation]].
- **Mutation testing** (e.g. with Slither): deliberately mutate the contract and check whether the test suite catches it — measures whether your *tests* are actually meaningful, not just present.

## Methodology
```text
1. UNDERSTAND  read docs/specs; map contracts, roles, money flows,
   external dependencies (oracles, tokens, other protocols).
2. MANUAL REVIEW  every external/public function: access control,
   checks-effects-interactions, arithmetic, trust assumptions
   ([[02]]-[[04]],[[07]]).
3. STATIC  run Slither/Mythril; triage findings.
4. DYNAMIC  write Foundry tests; fuzz + invariant-test core properties
   (Echidna); mutation-test the suite.
5. ECONOMIC  model oracle/flash-loan/MEV attacks ([[05]],[[06]]).
6. EXPLOIT  prove issues with PoC exploits on a mainnet fork.
7. REPORT  severity (impact x likelihood), clear repro, fix guidance.
```
Manual review finds the logic/economic bugs tools miss; tools find the mechanical ones and validate coverage. Both are required.

## Why It Matters
Immutable, fund-holding code demands finding bugs before deployment — and proving them without touching real money. This toolchain (especially Foundry fork-exploits + invariant fuzzing) is how auditors and bounty hunters reliably surface and demonstrate the catastrophic issues covered in this module, turning "this looks risky" into a reproducible exploit and a concrete fix.

## Defensive Notes
- Integrate **Slither + Foundry tests + invariant/fuzz testing** into CI; require them to pass before deploy; use mutation testing to ensure the suite is meaningful.
- Commission independent **audits** and run **bug bounties**; consider **formal verification** (Certora) for critical invariants.
- Follow secure patterns/libraries (OpenZeppelin), timelocks, pause mechanisms, and staged rollouts; monitor deployed contracts on-chain.

## Related Notes
- [[02 - Smart Contract Reentrancy]]
- [[03 - Common Solidity Vulnerabilities]]
- [[05 - DeFi and AMM Exploitation]]
- [[06 - Flash Loan Attacks]]
- [[05 - Finding and Vetting Exploits]]

---
tags: [blockchain, smart-contracts, reentrancy, pentesting]
difficulty: intermediate
module: "52 - Blockchain and Smart Contract Security"
topic: "52.02 Smart Contract Reentrancy"
---

# Smart Contract Reentrancy

## Introduction
**Reentrancy** is the most famous smart-contract vulnerability — the bug behind the 2016 DAO hack that drained ~$60M and forced the Ethereum hard fork. It occurs when a contract makes an **external call** (e.g. sending ETH) **before updating its own state**, and the called contract **calls back into the original function** before the first invocation finishes — re-entering it while its state is stale. An attacker contract exploits this to, for example, withdraw the same balance repeatedly. This note covers the mechanism, variants, and prevention.

## The Mechanism
```text
+---------------------------------------------------------------+
|                   REENTRANCY ATTACK                          |
+---------------------------------------------------------------+
|  Vulnerable withdraw():                                       |
|    1. check balance[msg.sender] > 0                           |
|    2. SEND ETH to msg.sender   <-- external call FIRST        |
|    3. balance[msg.sender] = 0   <-- state update AFTER (bug)  |
|                                                               |
|  Attacker contract's receive()/fallback() is triggered by     |
|  step 2 and CALLS withdraw() AGAIN before step 3 runs:        |
|       check passes (balance still > 0) -> send again -> ...    |
|       loop until the contract is drained                      |
+---------------------------------------------------------------+
```
Vulnerable pattern (Solidity):
```solidity
function withdraw() public {
    uint amount = balances[msg.sender];
    require(amount > 0);
    (bool ok,) = msg.sender.call{value: amount}("");  // external call
    require(ok);
    balances[msg.sender] = 0;                           // state AFTER -> bug
}
```
Attacker:
```solidity
receive() external payable {
    if (address(target).balance >= 1 ether) target.withdraw(); // re-enter
}
```

## Variants
- **Single-function reentrancy** — re-enter the same function (the DAO case, above).
- **Cross-function reentrancy** — re-enter a *different* function that shares state with the first (e.g. `transfer()` while `withdraw()` is mid-execution), bypassing a guard that only protects one function.
- **Cross-contract / read-only reentrancy** — re-enter via a third contract, or read stale state during a callback (e.g. an oracle/price read that's temporarily inconsistent) — affects modern DeFi even when classic withdrawal reentrancy is guarded.
- **ERC-777/hooks** — token standards with transfer hooks (`tokensReceived`) silently introduce external calls that enable reentrancy even where plain ERC-20 wouldn't.

## Testing Workflow
```text
1. Find external calls (.call/.transfer/.send, token transfers, hooks)
   that occur BEFORE state updates.
2. Check the order: is checks-effects-interactions violated?
3. Is there a reentrancy guard (nonReentrant)? Does it cover cross-
   function and the shared state?
4. Write an attacker contract whose receive()/hook re-enters; test on
   a fork ([[09]]).
5. For DeFi: check read-only reentrancy on price/balance reads during
   callbacks.
```

## Why It Matters
Reentrancy directly drains funds and has caused some of the largest crypto losses in history. Modern variants (cross-function, read-only) still hit well-known protocols, so it remains a top finding despite being decades old — especially as composability and token hooks reintroduce external-call surfaces developers don't expect.

## Defensive Notes
- **Checks-Effects-Interactions**: update state **before** any external call (set `balances[msg.sender]=0` first).
- Use a **reentrancy guard** (`nonReentrant` modifier, e.g. OpenZeppelin `ReentrancyGuard`) — and ensure it covers cross-function paths and read-only reentrancy in price-sensitive logic.
- Prefer pull-over-push payment patterns; be cautious with ERC-777/hook-bearing tokens; use `transfer`'s gas behaviour knowingly (and account for post-EIP changes).
- Invariant/fuzz testing ([[09]]) to catch reentrancy paths automatically.

## Related Notes
- [[01 - Blockchain and Web3 Security Overview]]
- [[03 - Common Solidity Vulnerabilities]]
- [[05 - DeFi and AMM Exploitation]]
- [[09 - Smart Contract Auditing Tools and Methodology]]

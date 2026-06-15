---
tags: [blockchain, smart-contracts, solidity, pentesting]
difficulty: intermediate
module: "52 - Blockchain and Smart Contract Security"
topic: "52.03 Common Solidity Vulnerabilities"
---

# Common Solidity Vulnerabilities

## Introduction
Beyond reentrancy ([[02 - Smart Contract Reentrancy]]), Solidity contracts share a recurring catalog of bug classes — broken access control, arithmetic issues, bad randomness, unchecked calls, front-running exposure, and logic errors. Many map to familiar application-security concepts (authorization, input validation) but with on-chain twists (public state, gas, immutability). This note is a field guide to the high-frequency classes auditors check on every contract.

## The Catalog
```text
+---------------------------------------------------------------+
|              HIGH-FREQUENCY SOLIDITY BUGS                    |
+---------------------------------------------------------------+
| Access control      missing/incorrect modifier on sensitive   |
|                     funcs (anyone can call mint/withdraw/      |
|                     selfdestruct/setOwner)                     |
| Arithmetic          overflow/underflow (pre-0.8.0 or unchecked|
|                     blocks); precision/rounding loss          |
| Unchecked calls     ignoring .call/.send return value         |
| Bad randomness      block.timestamp/blockhash as RNG ->        |
|                     predictable/miner-influenced              |
| tx.origin auth      using tx.origin instead of msg.sender ->  |
|                     phishing/relay bypass                     |
| Front-running/MEV   public mempool: ordering attacks,         |
|                     sandwiching, approval race                |
| DoS                 unbounded loops; revert-on-transfer to    |
|                     block a queue; gas griefing               |
| delegatecall/proxy  storage collisions, untrusted target      |
|                     ([[04]])                                  |
| Signature replay    missing nonce/chainId in signed messages  |
| Uninitialized       proxy/implementation left uninitialized   |
| Default visibility  functions/vars more public than intended  |
+---------------------------------------------------------------+
```

## Selected Classes in Detail
### Access control
The most common real-world bug: a privileged function (mint, withdraw, `setOwner`, `upgradeTo`, `selfdestruct`) lacks an `onlyOwner`/role check, so **anyone** can call it. The Parity multisig freeze (~$280M locked) stemmed from an unprotected `initWallet`/`kill`. Always map every state-changing function to "who is *supposed* to call this, and is that enforced?".

### Arithmetic
Before Solidity 0.8.0, `uint` math wrapped silently (overflow/underflow) — e.g. balance underflow grants huge balances. 0.8.0+ reverts by default, but `unchecked { }` blocks reintroduce the risk, and **precision/rounding** errors in division (especially DeFi share math) remain exploitable ([[05 - DeFi and AMM Exploitation]]).

### Bad randomness
`block.timestamp`, `blockhash`, `block.difficulty` are **public and miner-influenceable** — useless as RNG for lotteries/NFT traits. Attackers predict or compute the "random" outcome in the same block. Use commit-reveal or a VRF (Chainlink VRF).

### tx.origin authentication
`require(tx.origin == owner)` is bypassable: a malicious contract the owner is tricked into calling will have `tx.origin == owner` while `msg.sender` is the malicious contract — a phishing/relay bypass. Always authenticate with **`msg.sender`**.

### Front-running / MEV
The mempool is public, so attackers see your tx before it's mined and can **front-run** (place a tx ahead), **back-run**, or **sandwich** it. Affects DEX trades, auctions, and the ERC-20 approve race. Mitigate with commit-reveal, slippage limits, private mempools/flashbots.

## Testing Workflow
```text
1. Enumerate state-changing functions -> verify access control on each.
2. Check arithmetic (compiler version, unchecked blocks, division order).
3. Grep for tx.origin, block.timestamp-as-RNG, unchecked .call/.send.
4. Look for unbounded loops / external-call-in-loop (DoS).
5. Check signed-message handling for nonce + chainId (replay).
6. Confirm proxies/implementations are initialized ([[04]]).
7. Model ordering attacks (front-run/sandwich) on value-moving txs.
8. Verify with static analysis + fuzzing ([[09]]); exploit on a fork.
```

## Why It Matters
These classes account for the majority of audit findings and real exploits. Access-control and arithmetic bugs in particular have caused nine-figure losses, and because contracts are immutable and hold funds, a single missed `onlyOwner` is direct, irreversible theft. They're the bread-and-butter checklist of every smart-contract audit and bounty.

## Defensive Notes
- Use **OpenZeppelin** access-control (`Ownable`/`AccessControl`), `ReentrancyGuard`, and SafeMath/0.8+ checked arithmetic; minimize `unchecked`.
- Authenticate with `msg.sender`, never `tx.origin`; use VRF/commit-reveal for randomness; check all external-call return values.
- Add nonces + chainId to signed messages; initialize proxies; set explicit visibility; bound loops.
- Audit, fuzz, and formally verify ([[09]]); follow established secure patterns rather than rolling your own.

## Related Notes
- [[02 - Smart Contract Reentrancy]]
- [[04 - Proxy and Delegatecall Vulnerabilities]]
- [[05 - DeFi and AMM Exploitation]]
- [[09 - Smart Contract Auditing Tools and Methodology]]

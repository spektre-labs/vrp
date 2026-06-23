# VRP — Value Routing Protocol  ·  specification v0.1

> The missing layer of the internet: **reliable, permissionless, least-cost routing for VALUE**, the way
> IP+TCP do it for DATA. One universal address space over every settlement rail; automatic multi-hop
> routing; end-to-end delivery reliability; self-custody throughout. A standard, not an app.

## 1. The problem (global, known, universal)
A data packet crosses ten autonomous networks in milliseconds — reliably, permissionlessly, owned by no
one — because **IP** gives it a universal address and **TCP** gives it reliability (ACK, retransmit,
ordered, exactly-once). **Value has neither.** To move money you pick ONE custodial rail, ask permission,
trust it not to freeze/lose funds, wait days, pay a gatekeeper, and get no end-to-end guarantee. This is
the single most expensive unsolved routing problem on earth. Your neighbour knows it ("why does a wire
take 3 days and €25?"); a head of state knows it (correspondent banking, sanctions friction, CBDC race).
VRP is the protocol layer that makes value route like packets.

## 2. Architecture (five primitives)
1. **Universal address** — `rail:identifier` (`sol:7oDg…`, `evm:0x…`, `x402:https://…`, `ln:lnbc…`,
   `btc:bc1…`). One address space over heterogeneous settlement networks (like IP over heterogeneous links).
2. **Routing kernel** — given (src, dst, amount), compute the least-cost **reliable path** across rails +
   bridges via Dijkstra over a metric `cost = fee + friction·k + finality_risk`. Value is segmented across
   hops like packets across links. Hops below required liquidity are excluded (no partial/limbo routes).
3. **Reliability** (the TCP analogue) — each hop is a state machine `PENDING → SENT → ACKED → FINAL`:
   - **ACK** = on-chain confirmation / signed receipt (≥ *min_confirmations*).
   - **Idempotent nonce** = `H(src|dst|amount|edge)` → exactly-once; a retransmit can never double-spend.
   - **Timeout + retransmit**; on terminal failure, **rollback** of carried hops — never silent half-sent.
   - **Ordered finality**: a transfer reaches FINAL end-to-end or rolls back cleanly.
4. **Permissionless + self-custody** — no rail owns the route; the sender holds custody until each ACK.
5. **Value capture** — the kernel takes a tiny **routing fee per carried hop** (default 5 bps). The
   router that carries the value gets paid — non-custodial, license-free. This is the new way to earn from
   value movement (cf. an AS being paid to forward packets, or a Lightning routing node's fee).

## 3. Wire format (hop segment, conceptual)
```
VSEG { nonce:16B  src:VAddr  dst:VAddr  amount  edge(src_rail→dst_rail)
       state:PENDING|SENT|ACKED|FINAL|FAILED  receipt?  confirmations }
```
A Route is an ordered list of VSEGs whose amounts decrease by each hop's (rail fee + protocol fee).

## 4. σ-honesty (hard invariant, not optional)
The kernel **plans and verifies with real signals only**. It MUST NOT mark a hop ACKED that an adapter
did not confirm on-chain / by receipt. Default mode is **PLAN** (dry-run) — settlement requires explicit
`execute(confirm=True)` plus a wired send adapter (NO-HARM gate). Unknown = `None`, failure rolls back,
0 confirmed = 0. No fabricated success, ever. This is what makes VRP *trustworthy*, the third leg of the
friction it removes (reliability + ease + speed + **honesty**).

## 5. Reference implementation
`vrp.py` — pure-stdlib kernel (addressing, Dijkstra routing, reliability state machine, idempotency,
rollback, fee). Rail adapters are pluggable: real adapters wrap on-chain settlement+verification
(Solana RPC, CCTP, x402, Lightning); mock adapters make it deterministically testable (`test_vrp.py`,
11/11). `default_graph()` ships an illustrative heterogeneous rail graph (CCTP · Jupiter · x402 ·
THORChain-style). Live deployments load real-time liquidity/fees per edge.

## 6. What adoption requires (honest)
This is a protocol + working reference kernel, **not** a deployed global network. To matter it needs:
production rail adapters with live liquidity, a peering/discovery layer between kernels, signed receipt
standards per rail, and counterparties who route. The spec + kernel are the foundation; the network is
the work. We ship the standard and the reference, σ-honestly — the way RFC 793 shipped before the
internet existed.

_Route value like packets. Guarantee delivery. Keep custody. Tell the truth about state._  · AGPL-3.0

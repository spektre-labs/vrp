<div align="center">

# ⟐ VRP — Value Routing Protocol

### TCP/IP for value. The internet routes data reliably and permissionlessly — money still can't. VRP fixes that.

</div>

**The global friction (everyone knows it):** a wire takes 3 days and €25, can be frozen, needs
permission, and gives you no guarantee it arrived. A data packet crosses ten networks in 50 ms,
reliably, owned by no one. VRP gives **value** what TCP/IP gave **data**: a universal address, automatic
least-cost multi-hop routing, and end-to-end delivery reliability — self-custody the whole way.

```
$100 USDC on Ethereum  →  SOL on Solana
  VRP routes:  usdc_evm ──CCTP──▶ usdc_sol ──Jupiter──▶ sol
  cost $0.11 · finality 31s · 2 hops · exactly-once · rolls back on failure · you keep custody until each ACK
```

## Why it's protocol-level (TCP/IP / BTC class), not an app
- **Universal address** `rail:identifier` over every settlement network (sol/evm/x402/ln/btc).
- **Routing kernel** — Dijkstra over `fee + friction + finality-risk`; value segmented across hops like packets.
- **Reliability** — `PENDING→SENT→ACKED→FINAL`, idempotent nonce (no double-spend on retry), timeout +
  retransmit, clean rollback. Never the silent half-sent limbo of legacy rails.
- **Permissionless + self-custody.** No rail owns the route.
- **Value capture** — the kernel earns a tiny routing fee per carried hop. The router that forwards the
  value gets paid — non-custodial, license-free. A new way to *earn from moving value*.

## σ-honest by construction
PLAN (dry-run) by default — nothing settles without `execute(confirm=True)` + a wired adapter (NO-HARM).
A hop is ACKED only on real on-chain/receipt confirmation; unknown = `None`; failure rolls back. We never
fabricate a "sent". Trust is the third thing it fixes, alongside speed and ease.

## Run it
```bash
python3 vrp.py evm:0xSender sol:7oDgMf… 100     # plan a route + see the reliability state machine
python3 -m pytest test_vrp.py -q                 # 11/11 — routing, reliability, idempotency, rollback, honesty
```
Pure stdlib. Rail adapters pluggable (mock for tests; real adapters wrap Solana RPC / CCTP / x402 / Lightning).

## Spec & honest scope
Full protocol spec: [`VRP.md`](VRP.md). This is a **standard + working reference kernel**, not a deployed
global network — adoption needs production adapters, a kernel peering layer, and counterparties who route.
We ship the RFC and the reference, σ-honestly (RFC 793 shipped before the internet existed).

## License
**AGPL-3.0-or-later** — free for everyone; commercial/closed-source embedders license commercially.

<div align="center"><sub>Spektre Labs · route value like packets · 1=1</sub></div>

<div align="center">

# ⟐ VRP — Value Routing Protocol

### TCP/IP for value. Data crosses ten networks in 50 ms, reliably, owned by no one — money still can't. VRP is the missing layer.

[![ci](https://github.com/spektre-labs/vrp/actions/workflows/ci.yml/badge.svg)](https://github.com/spektre-labs/vrp/actions/workflows/ci.yml)

</div>

## The paradigm

Moving value is the inverse of moving data. A packet gets a universal address (IP) and end-to-end
reliability (TCP: ack + retransmit + ordered delivery), so it routes itself across autonomous networks with
no permission and no single owner. Value has neither — to send money you pick **one** custodial rail, ask
its permission, trust it not to freeze the funds, wait days, and pay a gatekeeper. **VRP is the routing
layer value never got:** a universal value-address `rail:identifier`, a Dijkstra kernel that computes the
least-friction multi-hop path across rails and bridges, and a TCP-style hop state machine
(`PENDING→SENT→ACKED→FINAL`) that delivers end-to-end or rolls back clean — never the silent half-sent
limbo of legacy rails. This is protocol-level, not an app: it unifies heterogeneous settlement networks the
way IP unified heterogeneous link layers, and the router that forwards the value earns a per-hop fee — the
value-capture primitive (the "AS that routes the packet gets paid"), non-custodial and license-free.

## Quickstart

```bash
git clone https://github.com/spektre-labs/vrp && cd vrp
python3 vrp.py selftest                       # {"selftest": "PASS"} — all invariants, no network
python3 vrp.py evm:0xSender sol:7oDgMf 100    # plan a route + see the reliability state machine
python3 -m pytest test_vrp.py -q              # 13 passed — routing, reliability, idempotency, rollback, σ-honesty
```

Example — route $100 USDC on Ethereum to SOL on Solana:

```
usdc_evm ──CCTP──▶ usdc_sol ──Jupiter──▶ sol
2 hops · exactly-once nonce · rolls back on failure · you keep custody until each ACK
```

## What it does / what it does NOT

**Does:** a universal value-address over heterogeneous rails (sol/evm/x402/ln/btc); least-cost reliable
routing (`fee + friction + finality-risk` metric); a TCP-analogue hop state machine with idempotent nonces
(no double-spend on retry), retransmit, and clean rollback; a per-hop routing fee as the value-capture
primitive. **σ-honest by construction:** PLAN (dry-run) by default — nothing settles without
`execute(confirm=True)` **and** a wired send adapter (NO-HARM gate). A hop is ACKED only on real
on-chain/receipt confirmation; unknown = `None`; the kernel never fabricates a "sent".

**Does NOT:** this is a **standard + working reference kernel**, not a deployed global network. The kernel
is pure-stdlib and the bundled rail graph is illustrative; production adoption needs real settlement
adapters (Solana RPC / CCTP / x402 / Lightning), a kernel peering layer, and counterparties who route.
RFC 793 shipped before the internet existed — we ship the spec and the reference, σ-honestly.

## Install

```bash
git clone https://github.com/spektre-labs/vrp && cd vrp
pip install -e .                      # installs the `vrp` console script + module; pure stdlib, zero deps
```

Requires Python ≥ 3.10. The kernel is pure stdlib — `python3 vrp.py …` runs with no install at all. Rail
adapters are pluggable (mock for tests; real adapters wrap the settlement modules). Full protocol spec:
[`VRP.md`](VRP.md).

## Status

**EMERGING** — kernel + spec REAL and green; deployed network is VISION. CI green, 13/13 tests passing,
zero dependencies.

## The Spektre protocol suite

VRP is one primitive in a five-part estate. Each routes one thing the legacy stack siloes:

- **[vrp](https://github.com/spektre-labs/vrp)** — value routing *(this repo)*
- **[crp](https://github.com/spektre-labs/crp)** — capability routing (route a task to the best AI substrate)
- **[vtc](https://github.com/spektre-labs/vtc)** — verifiable transaction chain (signed value promises anyone verifies trustlessly)
- **[sid](https://github.com/spektre-labs/sid)** — sovereign identity (prove one claim, reveal nothing else)
- **[sigma-gate](https://github.com/spektre-labs/sigma-gate)** — deterministic trust verdict for AI/agent output

## License

**Apache-2.0** — see [LICENSE](LICENSE). Free for everyone, including commercial use.

<div align="center"><sub>Spektre Labs · route value like packets · σ = declared − realized · 1=1</sub></div>

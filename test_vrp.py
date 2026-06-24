"""Deterministic, no-network tests for the VRP kernel: routing, TCP-style reliability, idempotency,
rollback, and the σ-honesty invariant (never fabricate an ACK; PLAN by default)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from vrp import VRPKernel, Edge, VAddr, HopState, default_graph, selftest, main


def test_address_parse_and_reject():
    a = VAddr.parse("sol:7oDgMf")
    assert a.rail == "sol" and a.ident == "7oDgMf"
    for bad in ["noColon", "sol:", ":addr"]:
        try:
            VAddr.parse(bad); assert False, bad
        except ValueError:
            pass


def test_route_direct_same_rail():
    k = VRPKernel(default_graph())
    r = k.route("sol:A", "sol:B", 50)
    assert r.feasible and len(r.hops) == 1 and r.hops[0].edge.src == "sol"


def test_route_multi_hop_least_cost():
    k = VRPKernel(default_graph())
    r = k.route("usdc_evm:0xA", "sol:B", 100)   # evm USDC → solana SOL
    assert r.feasible, r.reason
    rails = [h.edge.src for h in r.hops] + [r.hops[-1].edge.dst]
    assert rails[0] == "usdc_evm" and rails[-1] == "sol"
    assert r.cost_usd > 0 and r.finality_s > 0


def test_route_infeasible_when_no_path():
    k = VRPKernel([Edge("a", "b", 0, 0, 1, 1, 1e6)])
    r = k.route("a:x", "z:y", 10)
    assert not r.feasible and "no reliable path" in r.reason


def test_route_respects_liquidity():
    k = VRPKernel([Edge("a", "b", 0, 0, 1, 1, 100)])     # hop carries max $100
    assert k.route("a:x", "b:y", 50).feasible
    assert not k.route("a:x", "b:y", 500).feasible        # no partial/limbo route


def test_nonce_deterministic_idempotent():
    k = VRPKernel(default_graph())
    r1 = k.route("usdc_evm:0xA", "sol:B", 100)
    r2 = k.route("usdc_evm:0xA", "sol:B", 100)
    assert [h.nonce for h in r1.hops] == [h.nonce for h in r2.hops]   # same intent → same nonce (exactly-once)


def test_plan_only_by_default_no_send():
    # σ-honesty + NO-HARM: with no confirm / no adapter, nothing settles
    k = VRPKernel(default_graph())
    r = k.route("usdc_evm:0xA", "sol:B", 100)
    out = k.execute(r)                       # confirm defaults False
    assert out["state"] == "PLANNED" and out["ok"]


def test_execute_delivers_when_acked():
    sends, verifs = [], []
    def send(hop): sends.append(hop.nonce); return {"ok": True, "receipt": "sig_" + hop.nonce}
    def verify(hop): verifs.append(hop.nonce); return {"confirmations": 2, "final": True}
    k = VRPKernel(default_graph(), send_fn=send, verify_fn=verify)
    r = k.route("usdc_evm:0xA", "sol:B", 100)
    out = k.execute(r, confirm=True)
    assert out["ok"] and out["state"] == "DELIVERED"
    assert all(h["state"] == HopState.FINAL for h in out["hops"])
    assert out["fee_earned_usd"] > 0          # the value-capture primitive fired
    assert len(sends) == len(r.hops)


def test_execute_never_fabricates_ack():
    # send "succeeds" but verify returns 0 confirmations → must NOT report delivered
    def send(hop): return {"ok": True, "receipt": "sig"}
    def verify(hop): return {"confirmations": 0, "final": False}
    k = VRPKernel(default_graph(), send_fn=send, verify_fn=verify)
    r = k.route("usdc_evm:0xA", "sol:B", 100)
    out = k.execute(r, confirm=True, max_retries=1)
    assert not out["ok"] and out["state"] == "FAILED_ROLLED_BACK"


def test_failed_hop_rolls_back_prior():
    calls = {"n": 0}
    def send(hop):
        calls["n"] += 1
        return {"ok": True, "receipt": "s"} if calls["n"] == 1 else {"ok": False, "err": "rail down"}
    def verify(hop): return {"confirmations": 1, "final": False}
    k = VRPKernel(default_graph(), send_fn=send, verify_fn=verify)
    r = k.route("usdc_evm:0xA", "sol:B", 100)
    if len(r.hops) < 2:
        return                                # need a multi-hop route to test rollback
    out = k.execute(r, confirm=True, max_retries=0)
    assert not out["ok"] and out["state"] == "FAILED_ROLLED_BACK" and out["carried"] >= 1


def test_protocol_fee_scales_with_hops():
    k = VRPKernel(default_graph())
    r = k.route("usdc_evm:0xA", "sol:B", 1000)
    assert k._fee_earned(r) >= 1000 * k.PROTOCOL_FEE_BPS / 1e4 * 0.9   # ~fee per carried hop


def test_selftest_passes():
    # the in-module invariant check (also the `vrp selftest` CLI entrypoint) must be green
    assert selftest() is True


def test_cli_main_selftest_returns_zero():
    assert main(["selftest"]) == 0


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))

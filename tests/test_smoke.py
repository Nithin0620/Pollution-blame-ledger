"""Fast checks (no MCMC): generator schema, feature shapes, health monotonicity, diagnostics flagging."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ledger.synth import simulate
from ledger.features import build, REQUIRED
from ledger.health import af, burden
from ledger.diagnostics import identifiability


def test_schema_and_features():
    df, st, truth = simulate(seed=1, days=4)
    assert all(c in df.columns for c in REQUIRED)
    f = build(df, st)
    assert f["X"].shape == (4, len(st), 96)
    assert np.allclose(f["X"].mean(2), 1.0)                      # unit-mean proxies
    assert abs(f["w"].sum() - 1) < 1e-9


def test_truth_sums_to_pm25_roughly():
    df, st, truth = simulate(seed=2, days=4)
    recon = truth["background"][None, :] + truth["contrib"].sum(0)
    obs = np.vstack([df[df.station == n].pm25.values for n in st.station])
    assert abs((obs - recon).mean()) < 2.0


def test_health_monotone():
    assert af(150, 0.143) > af(60, 0.143) > af(20, 0.143) > 0
    th = np.full((50, 4, 3), 20.0)
    B = np.full((50, 5), 30.0)
    b = burden(th, B, np.array([5., 5., 5.]), ["a", "b", "c", "d"], 5)
    assert b["a@1.0"].mean() > b["a@0.5"].mean() > 0


def test_flags_tradeoff():
    rng = np.random.default_rng(0)
    x = rng.normal(size=2000)
    post = np.c_[20 + x, 20 - x + 0.1 * rng.normal(size=2000), 10 + rng.normal(size=2000) * 0.1]
    prior = rng.normal(size=(2000, 3)) * 10 + 20
    out = identifiability(post, prior, ["a", "b", "c"])
    assert out["flagged_pairs"] and out["status"]["a"] == "unresolved" and out["status"]["c"] == "identified"

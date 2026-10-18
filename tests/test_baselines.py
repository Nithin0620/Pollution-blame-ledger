import numpy as np
from ledger.synth import simulate
from ledger.baselines import nnls_episode, FIXED_SHARES
from ledger.literature import benchmark


def test_fixed_shares_sum_to_one():
    assert abs(sum(FIXED_SHARES.values()) - 1) < 1e-9


def test_nnls_nonnegative_and_reasonable_total():
    df, st, _ = simulate(seed=3)
    est, draws, ymean = nnls_episode(df, st, boots=20)
    assert (est >= 0).all() and draws.shape == (20, 5)
    assert abs(est.sum() - ymean) / ymean < 0.05       # fitted contributions + intercept reproduce mean PM2.5


def test_literature_overlap_logic():
    comps = [{"id": "traffic", "share": {"mean": .25, "lo": .2, "hi": .3}}]
    assert benchmark(comps)["traffic"]["refs"][0]["overlaps"] is True

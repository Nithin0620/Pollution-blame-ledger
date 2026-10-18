import os, pytest
from ledger.realdata import load_fire_daily, to_episode_multi
from ledger.features import build

F = "data/firms_viirs_punjab_haryana_daily_2018.csv"


@pytest.mark.skipif(not (os.path.exists(F) and os.path.exists("data/cpcb")), reason="real data files not present")
def test_real_multistation_episode():
    fd = load_fire_daily(F)
    df, st = to_episode_multi(fd, "2018-10-28", "2018-11-11")
    f = build(df, st)
    assert f["X"].shape == (4, 6, 14 * 24) and not df.isna().any().any()
    df2, _ = to_episode_multi(fd, "2018-11-26", "2018-12-10")
    assert df.frp_footprint.mean() > 10 * df2.frp_footprint.mean()   # burning peak far above post-season

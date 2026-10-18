"""Published Delhi PM2.5 apportionment ranges, for benchmarking any episode's shares (percent of PM2.5).

Categories differ between studies, so the mapping to our sources is approximate and stated per row.
Sources: IIT Kanpur winter CMB (via CSE India); CEEW 2019 inventory comparison (range across studies).
Caveat: these are seasonal/annual averages, an individual episode may legitimately fall outside them.
"""
from __future__ import annotations

REFS = {
    "traffic": [("IIT Kanpur winter CMB: vehicles", 25, 25), ("CEEW 2019: transport (inventories)", 17.9, 39.2)],
    "dust": [("IIT Kanpur winter CMB: road + construction dust", 6, 6), ("CEEW 2019: road dust (inventories)", 18.1, 37.8)],
    "biomass": [("IIT Kanpur winter CMB: biomass burning", 26, 26)],
    "industry": [("IIT Kanpur winter CMB: coal + fly ash (closest match)", 5, 5)],
}


def benchmark(components):
    """For each source: our 90% share interval (percent) vs each published figure/range."""
    out = {}
    for c in components:
        k = c["id"]
        if k not in REFS:
            continue
        lo, hi, mean = c["share"]["lo"] * 100, c["share"]["hi"] * 100, c["share"]["mean"] * 100
        rows = []
        for name, a, b in REFS[k]:
            rows.append({"ref": name, "low": a, "high": b, "overlaps": bool(lo <= b and hi >= a)})
        out[k] = {"ours": {"mean": mean, "lo": lo, "hi": hi}, "refs": rows}
    return out

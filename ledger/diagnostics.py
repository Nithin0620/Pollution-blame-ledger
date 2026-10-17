"""Identifiability diagnostics: which source pairs can the data NOT separate?"""
from __future__ import annotations
import numpy as np

CORR_FLAG = -0.5    # strongly anti-correlated posteriors = the data only pins down their sum
GAIN_FLAG = 0.5     # information gain below this = posterior barely narrower than prior
WIDTH_FLAG = 1.0    # 90% CI wider than the mean


def identifiability(post_means, prior_means, names):
    """post_means/prior_means: [draws, M] pop-weighted episode-mean contribution per component."""
    corr = np.corrcoef(post_means.T)
    gain = 1 - post_means.var(0) / np.maximum(prior_means.var(0), 1e-9)
    lo, hi = np.percentile(post_means, [5, 95], axis=0)
    width = (hi - lo) / np.maximum(post_means.mean(0), 1e-9)
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if corr[i, j] < CORR_FLAG:
                pairs.append({"a": names[i], "b": names[j], "corr": float(corr[i, j]),
                              "message": f"{names[i]} and {names[j]} trade off against each other (posterior r = {corr[i, j]:.2f}); "
                                         f"only their sum is well constrained."})
    status = {}
    for i, n in enumerate(names):
        weak = gain[i] < GAIN_FLAG or width[i] > WIDTH_FLAG
        in_pair = any(n in (p["a"], p["b"]) for p in pairs)
        status[n] = "unresolved" if in_pair else "weak" if weak else "identified"
    return {"names": names, "corr": corr.round(3).tolist(), "info_gain": gain.round(3).tolist(),
            "rel_width": width.round(3).tolist(), "flagged_pairs": pairs, "status": status}

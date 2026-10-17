"""Pollution Blame Ledger - probabilistic PM2.5 source apportionment for Delhi (MVP)."""
SOURCES = ["traffic", "industry", "dust", "biomass"]
SOURCE_LABELS = {
    "traffic": "Vehicular exhaust",
    "industry": "Industrial point sources",
    "dust": "Road & construction dust",
    "biomass": "Crop-residue burning",
    "background": "Regional background (unresolved)",
}

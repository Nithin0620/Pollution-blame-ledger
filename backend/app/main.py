from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import datasets, simulate, upload, jobs

app = FastAPI(
    title="Pollution Blame Ledger API",
    description="Bayesian receptor model API for source apportionment & health burden estimation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets.router)
app.include_router(simulate.router)
app.include_router(upload.router)
app.include_router(jobs.router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "pollution-blame-ledger-api"}

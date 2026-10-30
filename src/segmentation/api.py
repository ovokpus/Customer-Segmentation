import json
import os
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import core

ARTIFACT_DIR = Path(os.getenv("ARTIFACT_DIR", "artifacts"))

app = FastAPI(title="Customer Segmentation API", version="1.0.0",
              description="RFM segments and K-Means clusters for the UCI Online Retail dataset.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@lru_cache
def store():
    customers = pd.read_csv(ARTIFACT_DIR / "customers.csv")
    meta = json.loads((ARTIFACT_DIR / "meta.json").read_text())
    model = joblib.load(ARTIFACT_DIR / "kmeans.joblib")
    return customers, meta, model


class AssignIn(BaseModel):
    recency: int = Field(..., ge=0, description="Days since last purchase", examples=[12])
    frequency: int = Field(..., ge=1, description="Number of orders", examples=[6])
    monetary: float = Field(..., gt=0, description="Total spend (GBP)", examples=[2100.0])


def _group(df: pd.DataFrame, col: str, total_rev: float) -> list[dict]:
    g = df.groupby(col).agg(customers=("CustomerID", "size"), revenue=("Monetary", "sum"),
                            recency=("Recency", "median"), frequency=("Frequency", "median"),
                            monetary=("Monetary", "median"))
    g["revenue_share"] = g.revenue / total_rev
    g = g.sort_values("revenue", ascending=False).round(3).reset_index().rename(columns={col: "name"})
    return g.to_dict(orient="records")


@app.get("/health")
def health():
    store()
    return {"status": "ok"}


@app.get("/summary")
def summary():
    df, meta, _ = store()
    return {k: meta[k] for k in ("transactions", "customers", "revenue", "period", "n_clusters", "silhouette")} | {
        "avg_order_value": round(df.Monetary.sum() / df.Frequency.sum(), 2),
        "monthly_revenue": meta["monthly_revenue"],
    }


@app.get("/segments")
def segments():
    df, _, _ = store()
    return _group(df, "Segment", df.Monetary.sum())


@app.get("/clusters")
def clusters():
    df, _, _ = store()
    return _group(df, "Cluster", df.Monetary.sum())


@app.get("/cohorts")
def cohorts():
    return store()[1]["cohorts"]


@app.get("/customers")
def customers(segment: str | None = None, cluster: str | None = None,
              limit: int = Query(20, le=500), sample: bool = False):
    df, _, _ = store()
    if segment:
        df = df[df.Segment == segment]
    if cluster:
        df = df[df.Cluster == cluster]
    df = df.sample(min(limit, len(df)), random_state=0) if sample else df.nlargest(limit, "Monetary")
    return df.to_dict(orient="records")


@app.get("/customers/{customer_id}")
def customer(customer_id: int):
    df, _, _ = store()
    row = df[df.CustomerID == customer_id]
    if row.empty:
        raise HTTPException(404, f"customer {customer_id} not found")
    return row.iloc[0].to_dict()


@app.post("/assign")
def assign(body: AssignIn):
    _, meta, model = store()
    q = meta["quartiles"]
    r = core.score(body.recency, q["Recency"], higher_is_better=False)
    f = core.score(body.frequency, q["Frequency"], higher_is_better=True)
    m = core.score(body.monetary, q["Monetary"], higher_is_better=True)
    X = pd.DataFrame([[body.recency, body.frequency, body.monetary]], columns=core.RFM)
    c = int(model["kmeans"].predict(X)[0])
    return {"R": r, "F": f, "M": m, "rfm_score": f"{r}{f}{m}",
            "segment": core.segment_name(r, f, m), "cluster": model["names"][c]}

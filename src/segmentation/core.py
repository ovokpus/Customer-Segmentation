"""RFM scoring, named segments, K-Means clustering and cohort retention.

Logic follows retail_project.ipynb:
- clean: drop rows without CustomerID, keep Quantity > 0 and UnitPrice > 0, TotalPrice = Quantity * UnitPrice
- RFM snapshot date 2011-12-09 12:50 (last invoice in the data)
- quartile scores 1..4 where 1 is best (most recent / most frequent / highest spend)
- K-Means on standardized RFM
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

SNAPSHOT = pd.Timestamp("2011-12-09 12:50")
RFM = ["Recency", "Frequency", "Monetary"]

# Notebook segments, made mutually exclusive by checking them in priority order.
SEGMENTS = [
    ("Best Customers", lambda r, f, m: r == 1 and f == 1 and m == 1),
    ("Lost Cheap Customers", lambda r, f, m: r == 4 and f == 4 and m == 4),
    ("Lost Customers", lambda r, f, m: r == 4 and f == 1 and m == 1),
    ("Almost Lost", lambda r, f, m: r == 3 and f == 1 and m == 1),
    ("Loyal Customers", lambda r, f, m: f == 1),
    ("Big Spenders", lambda r, f, m: m == 1),
    ("Recent Customers", lambda r, f, m: r == 1),
    ("At Risk", lambda r, f, m: r == 4),
]
OTHER = "Needs Attention"


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["CustomerID"])
    df = df[(df.Quantity > 0) & (df.UnitPrice > 0)].copy()
    df["CustomerID"] = df.CustomerID.astype(int)
    df["InvoiceDate"] = pd.to_datetime(df.InvoiceDate)
    df["TotalPrice"] = df.Quantity * df.UnitPrice
    return df


def rfm_table(tx: pd.DataFrame, snapshot: pd.Timestamp = SNAPSHOT) -> pd.DataFrame:
    g = tx.groupby("CustomerID")
    out = pd.DataFrame({
        "Recency": (snapshot - g.InvoiceDate.max()).dt.days,
        "Frequency": g.InvoiceNo.nunique(),  # distinct orders (the notebook counted line items)
        "Monetary": g.TotalPrice.sum().round(2),
        "Country": g.Country.agg(lambda s: s.mode().iat[0]),
    })
    return out.reset_index()


def quartiles(rfm: pd.DataFrame) -> dict:
    q = rfm[RFM].quantile([0.25, 0.5, 0.75])
    return {c: [float(q.loc[p, c]) for p in (0.25, 0.5, 0.75)] for c in RFM}


def score(value: float, cuts: list[float], higher_is_better: bool) -> int:
    s = 1 + sum(value > c for c in cuts)  # 1..4, low value -> 1
    return 5 - s if higher_is_better else s


def segment_name(r: int, f: int, m: int) -> str:
    return next((name for name, rule in SEGMENTS if rule(r, f, m)), OTHER)


def add_scores(rfm: pd.DataFrame, q: dict) -> pd.DataFrame:
    rfm = rfm.copy()
    rfm["R"] = rfm.Recency.apply(score, cuts=q["Recency"], higher_is_better=False)
    rfm["F"] = rfm.Frequency.apply(score, cuts=q["Frequency"], higher_is_better=True)
    rfm["M"] = rfm.Monetary.apply(score, cuts=q["Monetary"], higher_is_better=True)
    rfm["RFMscore"] = rfm.R.astype(str) + rfm.F.astype(str) + rfm.M.astype(str)
    rfm["Segment"] = [segment_name(*x) for x in rfm[["R", "F", "M"]].itertuples(index=False)]
    return rfm


def build_kmeans(k: int = 4) -> Pipeline:
    # log1p tames the heavy right tail of Frequency and Monetary before scaling.
    return Pipeline([
        ("log", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
        ("scale", StandardScaler()),
        ("kmeans", KMeans(n_clusters=k, n_init=10, random_state=42)),
    ])


def name_clusters(rfm: pd.DataFrame, labels: np.ndarray) -> dict[int, str]:
    """Rank clusters by a value score (high F and M, low R) and give them readable names."""
    prof = rfm.assign(c=labels).groupby("c")[RFM].median()
    value = (prof.Frequency.rank() + prof.Monetary.rank() - prof.Recency.rank())
    names = ["Champions", "Loyal Regulars", "Potential", "Hibernating", "Lost", "Dormant"]
    return {int(c): names[i] for i, c in enumerate(value.sort_values(ascending=False).index)}


def cohort_retention(tx: pd.DataFrame) -> dict:
    t = tx[["CustomerID", "InvoiceDate"]].copy()
    t["InvoiceMonth"] = t.InvoiceDate.dt.to_period("M")
    t["CohortMonth"] = t.groupby("CustomerID").InvoiceMonth.transform("min")
    t["Index"] = (t.InvoiceMonth - t.CohortMonth).apply(lambda d: d.n)
    counts = t.groupby(["CohortMonth", "Index"]).CustomerID.nunique().unstack()
    ret = counts.divide(counts[0], axis=0).round(4)
    return {
        "cohorts": [str(c) for c in ret.index],
        "sizes": [int(x) for x in counts[0]],
        "retention": [[None if pd.isna(v) else float(v) for v in row] for row in ret.values],
    }

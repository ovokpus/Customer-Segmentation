"""Download the UCI Online Retail data, compute RFM segments, fit K-Means, write artifacts."""
import io
import json
import os
import urllib.request
import zipfile
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import silhouette_score

from . import core

DATA_URL = os.getenv("DATA_URL", "https://archive.ics.uci.edu/static/public/352/online+retail.zip")
ARTIFACT_DIR = Path(os.getenv("ARTIFACT_DIR", "artifacts"))
N_CLUSTERS = int(os.getenv("N_CLUSTERS", "4"))


def load_raw() -> pd.DataFrame:
    with urllib.request.urlopen(DATA_URL, timeout=120) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    name = next(n for n in z.namelist() if n.endswith(".xlsx"))
    return pd.read_excel(z.open(name), dtype={"InvoiceNo": str, "StockCode": str})


def main() -> None:
    tx = core.clean(load_raw())
    rfm = core.rfm_table(tx)
    q = core.quartiles(rfm)
    rfm = core.add_scores(rfm, q)

    km = core.build_kmeans(N_CLUSTERS).fit(rfm[core.RFM])
    labels = km.predict(rfm[core.RFM])
    names = core.name_clusters(rfm, labels)
    rfm["Cluster"] = [names[int(c)] for c in labels]
    X = km[:-1].transform(rfm[core.RFM])
    sil = float(silhouette_score(X, labels, sample_size=3000, random_state=0))

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"kmeans": km, "names": names}, ARTIFACT_DIR / "kmeans.joblib")
    rfm.to_csv(ARTIFACT_DIR / "customers.csv", index=False)
    meta = {
        "quartiles": q, "n_clusters": N_CLUSTERS, "silhouette": round(sil, 3),
        "transactions": int(len(tx)), "customers": int(len(rfm)),
        "revenue": round(float(tx.TotalPrice.sum()), 2),
        "period": [str(tx.InvoiceDate.min().date()), str(tx.InvoiceDate.max().date())],
        "cohorts": core.cohort_retention(tx),
        "monthly_revenue": {str(k): round(float(v), 2) for k, v in tx.groupby(tx.InvoiceDate.dt.to_period("M")).TotalPrice.sum().items()},
    }
    (ARTIFACT_DIR / "meta.json").write_text(json.dumps(meta))
    print(json.dumps({k: meta[k] for k in ("transactions", "customers", "revenue", "silhouette")}))
    print(rfm.Segment.value_counts().to_string())
    print(rfm.groupby("Cluster")[core.RFM].median().to_string())


if __name__ == "__main__":
    main()

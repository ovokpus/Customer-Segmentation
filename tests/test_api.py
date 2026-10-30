import json

import joblib
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from segmentation import core


@pytest.fixture()
def client(tmp_path, monkeypatch):
    import numpy as np
    rng = np.random.default_rng(0)
    rfm = pd.DataFrame({"CustomerID": range(200), "Recency": rng.integers(0, 370, 200),
                        "Frequency": rng.integers(1, 30, 200), "Monetary": rng.uniform(10, 5000, 200).round(2),
                        "Country": "UK"})
    q = core.quartiles(rfm)
    rfm = core.add_scores(rfm, q)
    km = core.build_kmeans(3).fit(rfm[core.RFM])
    names = core.name_clusters(rfm, km.predict(rfm[core.RFM]))
    rfm["Cluster"] = [names[int(c)] for c in km.predict(rfm[core.RFM])]
    rfm.to_csv(tmp_path / "customers.csv", index=False)
    joblib.dump({"kmeans": km, "names": names}, tmp_path / "kmeans.joblib")
    meta = {"quartiles": q, "n_clusters": 3, "silhouette": 0.3, "transactions": 1000, "customers": 200,
            "revenue": float(rfm.Monetary.sum()), "period": ["2010-12-01", "2011-12-09"],
            "cohorts": {"cohorts": ["2010-12"], "sizes": [10], "retention": [[1.0, 0.4]]},
            "monthly_revenue": {"2010-12": 100.0}}
    (tmp_path / "meta.json").write_text(json.dumps(meta))
    from segmentation import api
    monkeypatch.setattr(api, "ARTIFACT_DIR", tmp_path)
    api.store.cache_clear()
    yield TestClient(api.app)
    api.store.cache_clear()


def test_endpoints(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/summary").json()["customers"] == 200
    segs = client.get("/segments").json()
    assert sum(s["customers"] for s in segs) == 200
    assert len(client.get("/clusters").json()) == 3
    assert client.get("/cohorts").json()["retention"][0][0] == 1.0
    assert len(client.get("/customers", params={"limit": 5}).json()) == 5
    assert client.get("/customers/3").json()["CustomerID"] == 3
    assert client.get("/customers/9999").status_code == 404


def test_assign(client):
    r = client.post("/assign", json={"recency": 1, "frequency": 100, "monetary": 99999}).json()
    assert r["rfm_score"] == "111" and r["segment"] == "Best Customers" and r["cluster"]
    assert client.post("/assign", json={"recency": -1, "frequency": 1, "monetary": 1}).status_code == 422

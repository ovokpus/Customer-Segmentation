import pandas as pd

from segmentation import core


def tx():
    rows = []
    for cid, n, days, price in [(1, 10, 1, 50), (2, 1, 300, 5), (3, 4, 30, 20), (4, 2, 90, 10)]:
        for i in range(n):
            rows.append(dict(InvoiceNo=f"{cid}-{i}", Quantity=2, UnitPrice=price, CustomerID=float(cid),
                             Country="UK", InvoiceDate=core.SNAPSHOT - pd.Timedelta(days=days + i)))
    rows.append(dict(InvoiceNo="C1", Quantity=-1, UnitPrice=5, CustomerID=1.0, Country="UK", InvoiceDate=core.SNAPSHOT))
    rows.append(dict(InvoiceNo="X", Quantity=1, UnitPrice=5, CustomerID=None, Country="UK", InvoiceDate=core.SNAPSHOT))
    return pd.DataFrame(rows)


def test_clean_drops_returns_and_missing_ids():
    df = core.clean(tx())
    assert (df.Quantity > 0).all() and df.CustomerID.notna().all()
    assert len(df) == 17


def test_rfm_and_scores():
    rfm = core.rfm_table(core.clean(tx()))
    best = rfm.set_index("CustomerID").loc[1]
    assert best.Recency == 1 and best.Frequency == 10 and best.Monetary == 1000
    scored = core.add_scores(rfm, core.quartiles(rfm)).set_index("CustomerID")
    assert scored.loc[1, "RFMscore"] == "111" and scored.loc[1, "Segment"] == "Best Customers"
    assert scored.loc[2, "RFMscore"] == "444" and scored.loc[2, "Segment"] == "Lost Cheap Customers"


def test_score_direction():
    cuts = [10, 20, 30]
    assert core.score(5, cuts, higher_is_better=False) == 1
    assert core.score(50, cuts, higher_is_better=True) == 1
    assert core.score(5, cuts, higher_is_better=True) == 4


def test_segment_priority():
    assert core.segment_name(4, 1, 1) == "Lost Customers"
    assert core.segment_name(2, 1, 3) == "Loyal Customers"
    assert core.segment_name(2, 2, 2) == core.OTHER


def test_cohort_first_month_is_full_retention():
    c = core.cohort_retention(core.clean(tx()))
    assert all(row[0] == 1.0 for row in c["retention"])

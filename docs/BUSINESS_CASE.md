# Business case: Customer Segmentation (RFM + K-Means)

**Group customers by how recently, how often and how much they buy, so each group gets its own plan.**

## Who buys this

The buyer is a marketing or CRM lead at an online retailer with a few thousand to a few hundred thousand customers. The users are campaign managers choosing who gets which offer.

## The problem and what it costs

Treating every customer the same wastes budget, and looking at them one at a time is impossible. On the UCI Online Retail data used here (397,884 cleaned transactions from 4,338 customers, about £8.9M, Dec 2010 to Dec 2011), the repo's own analysis finds that **about 16% of customers bring in about 64% of revenue** ([dataset at UCI](https://archive.ics.uci.edu/dataset/352/online+retail)). That kind of concentration is why segments matter.

## How the repo solves it

| Need | What in the repo does it |
|---|---|
| Score customers | RFM quartiles (recency, frequency, monetary) and a K-Means model, fitted in `retail_project.ipynb` and packaged in `src/` |
| Assign a new customer | `POST /assign` returns R, F and M scores, an RFM segment and a cluster |
| See the groups | A React dashboard with segment sizes, revenue share and cohort retention |
| Cohort view | Monthly cohorts. Typically 20 to 25% come back the next month, and the earliest cohort holds 30 to 50% all year. |

## Use-case scenarios

All of these organisations are fictional.

1. **A UK gift retailer** sends a second-purchase offer to the "Potential" group and a win-back offer to "At Risk".
2. **A specialty coffee subscription** stops discounting to its most loyal segment, which buys anyway.
3. **A homewares shop** assigns each new customer a segment at checkout so the first follow-up email matches their behaviour.

## ROI: a worked model (illustrative)

These figures are **illustrative assumptions** unless a source is linked.

| Input | Value | Basis |
|---|---|---|
| Marketing spend a year | US$100,000 | Assumption |
| Share of spend currently going to customers unlikely to respond | 30% | Assumption |
| Share of that waste removed by targeting segments | 50% | Assumption |

Saving: $100,000 × 30% × 50% = **US$15,000 a year** in better-targeted spend, before any revenue gain from campaigns that fit each group.

## Path to production

1. Connect to the live order database or warehouse and refresh scores nightly.
2. Push segments to the email or CRM tool.
3. Test each campaign against a hold-out group to measure the real lift.

## Risks and limits

- RFM ignores product mix and margins, so a high-spend customer may still be unprofitable.
- K-Means clusters shift when refitted, so segment labels need to be kept stable for marketing.
- The data is 2010 to 2011 retail transactions.

**Case strength:** **Good.** It is simple, explainable and maps directly to marketing actions. The dataset is real, though old.

## Sources

- UCI Machine Learning Repository, Online Retail dataset: https://archive.ics.uci.edu/dataset/352/online+retail

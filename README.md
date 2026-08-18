# Bella Napoli — Pizza Chain Operations Analytics

An end-to-end Power BI project analysing the operations of a fictional Spanish
pizza chain (20 stores, \~1M order lines). It answers two business questions:
**which stores underperform, and is the cause traffic or ticket size?** — then
drills into the menu to explain the store-level story at product level.

All data is 100% synthetic, generated with a documented Python script.

\---

## Dashboard

**Page 1 — Store Performance**
[docs/page1_store_performance.png](https://github.com/PierpaoloInfuso/bella-napoli-analytics/blob/50d90235282bed8abdd9b6701785f800f6bded82/docs/page1_store_performance.png)

**Page 2 — Menu Engineering**
!\[Menu Engineering](docs/page2\_menu\_engineering.png)

\---

## The business questions

|Question|Where it's answered|
|-|-|
|Which stores under- or over-perform?|Store scatter: traffic (orders) vs ticket (avg order value)|
|Is weak performance driven by low traffic or low ticket?|Quadrant classification on the scatter|
|Which menu items to promote, reprice, reposition or remove?|Menu-engineering matrix: popularity vs profitability|
|Why does a specific store underperform?|Drillthrough from a store into its own menu mix|

## Key insights the model surfaces

* **Traffic ≠ revenue quality.** Some high-traffic stores sit on the lowest
average ticket — they sell a lot but cheaply. The scatter separates a traffic
problem from a ticket problem, which need different fixes.
* **The best-sellers are the least profitable *by percentage*.** The two
top-selling pizzas fall below the median margin %, flagged as **Reprice** — a
small price/cost adjustment there has outsized impact given the volume.
* **% margin and € margin tell opposite stories.** Beverages win on margin %
(\~86%) but a pizza generates far more margin *per unit* in euros. The report
shows both, so the recommendation isn't "push drinks" but "protect the
volume drivers while trimming their cost".

## Technical architecture

* **Star schema** — one fact table (`FactOrderLines`, order-line grain with
timestamp) and five dimensions (Store, Product, Channel, Date, Hour). All
relationships one-to-many, single filter direction.
* **DAX** — dynamic quadrant classification using `MEDIANX` + `ALLSELECTED` so
the median thresholds recalculate against the stores/products currently in
view (respecting slicers, ignoring the row's own filter via context
transition). Time intelligence on a marked date table.
* **Menu engineering** — popularity (units) vs profitability (margin %),
bubble size = total margin (€), classified into Promote / Reprice /
Reposition / Remove.
* **Drillthrough** — Page 1 → Page 2 carries the selected store as context.
Page 2 is intentionally kept free of slicers: it is a contextual detail view,
so propagating page-level filters as well would create ambiguity over which
filter wins.
* **Custom theme** — a JSON theme for consistent colour and typography.

## How to use

1. Open `pbix/BellaNapoli.pbix` in Power BI Desktop — the model already
contains the data, so it works out of the box.
2. To inspect or regenerate the raw data: unzip `data/FactOrderLines.zip`, or
run `scripts/generate\_pizza\_data.py` to regenerate the full dataset from
scratch (requires `pandas`, `numpy`).

## Tech stack

Power BI Desktop · DAX · Power Query (M) · Python (pandas, numpy) · star-schema
data modelling

\---

## About

Built by **Pierpaolo Infuso** — Power BI Developer.
[LinkedIn](https://www.linkedin.com/in/pierpaolo-infuso-a407b0b6/)


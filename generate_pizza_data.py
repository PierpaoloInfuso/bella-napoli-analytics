"""
Pizza Chain Operations Analytics - Synthetic Data Generator
===========================================================
Fictional Spanish pizza chain ("Bella Napoli"). 100% synthetic data.

Design goals (why this generator is not just random numbers):
  1. REALISTIC TIME PATTERNS  - lunch & (late) dinner peaks, weekend lift,
     summer/holiday seasonality, channel-dependent hour curves.
  2. MENU ENGINEERING          - each product has cost & price so the
     popularity x profitability matrix yields real Stars / Plowhorses /
     Puzzles / Dogs, not an undifferentiated blob.
  3. SEEDED STORE STORIES       - store performance varies on purpose so the
     "which stores underperform, and is it traffic or ticket?" question has a
     discoverable answer (traffic-rich/ticket-poor, a growing new store, etc.).

Output: /mnt/user-data/outputs/pizza/*.csv  (+ this script goes in the repo)
GitHub-friendly: integer surrogate keys, fact kept ~1M rows.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

rng = np.random.default_rng(7)
OUT = Path("/mnt/user-data/outputs/pizza")
OUT.mkdir(parents=True, exist_ok=True)

START = date(2024, 7, 1)
END   = date(2026, 6, 30)           # 24 months -> supports YoY
DATES = [START + timedelta(d) for d in range((END - START).days + 1)]

# ---------------------------------------------------------------------------
# DIM_CHANNEL
# ---------------------------------------------------------------------------
channels = pd.DataFrame({
    "ChannelID":   [1, 2, 3],
    "ChannelName": ["Dine-in", "Takeaway", "Delivery"],
    "CommissionPct": [0.0, 0.0, 0.18],   # delivery carries platform commission
})
channels.to_csv(OUT / "DimChannel.csv", index=False)

# ---------------------------------------------------------------------------
# DIM_STORE  (with seeded archetypes -> the analysis has something to find)
# ---------------------------------------------------------------------------
cities = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Malaga"]
loc_types = ["City Center", "Suburban", "Mall"]

# archetype: (traffic_factor, basket_factor, opens_late_months)
# basket_factor < 1 => lower average ticket (smaller / cheaper baskets)
store_rows = []
archetypes = (
    ["normal"] * 12 +
    ["traffic_rich_ticket_poor", "low_traffic_high_ticket"] +
    ["underperformer", "underperformer"] +
    ["star"] +
    ["new_growing"] +
    ["normal", "normal"]
)
rng.shuffle(archetypes)
for i, arch in enumerate(archetypes, start=1):
    city = cities[(i - 1) % len(cities)]
    loc  = rng.choice(loc_types, p=[0.45, 0.35, 0.20])
    traffic, basket, open_offset = 1.0, 1.0, 0
    if arch == "traffic_rich_ticket_poor":
        traffic, basket = 1.6, 0.72
    elif arch == "low_traffic_high_ticket":
        traffic, basket = 0.6, 1.45
    elif arch == "underperformer":
        traffic, basket = 0.55, 0.85
    elif arch == "star":
        traffic, basket = 1.8, 1.25
    elif arch == "new_growing":
        traffic, basket = 1.1, 1.0
        open_offset = rng.integers(300, 430)     # opens partway through window
    else:
        traffic = float(rng.uniform(0.8, 1.25))
        basket  = float(rng.uniform(0.9, 1.15))
    opening = START + timedelta(int(open_offset))
    store_rows.append((i, f"Bella Napoli {city} {i:02d}", city, loc,
                       opening.isoformat(), int(rng.integers(30, 90)),
                       round(traffic, 3), round(basket, 3), arch))
dim_store = pd.DataFrame(store_rows, columns=[
    "StoreID", "StoreName", "City", "LocationType", "OpeningDate",
    "SeatingCapacity", "_traffic", "_basket", "_archetype"])
# public CSV excludes the internal generator columns
dim_store.drop(columns=["_traffic", "_basket", "_archetype"]).to_csv(
    OUT / "DimStore.csv", index=False)

# ---------------------------------------------------------------------------
# DIM_PRODUCT  (menu engineering economics baked in)
# ---------------------------------------------------------------------------
# (Name, Category, UnitCost, UnitPrice, popularity_weight)
menu = [
    # Pizzas - the core. Margins vary; popularity varies -> Stars/Plowhorses/Puzzles/Dogs
    ("Margherita",            "Pizza", 2.10, 8.90, 10.0),  # cheap, hugely popular -> Plowhorse
    ("Diavola",               "Pizza", 2.80, 10.90, 9.0),  # popular + good margin -> Star
    ("Prosciutto e Funghi",   "Pizza", 3.10, 11.50, 6.5),
    ("Quattro Formaggi",      "Pizza", 3.40, 11.90, 5.5),
    ("Capricciosa",           "Pizza", 3.30, 11.90, 4.0),
    ("Napoli",                "Pizza", 2.60, 10.50, 4.5),
    ("Vegetariana",           "Pizza", 2.90, 10.90, 3.0),
    ("Bufala DOP",            "Pizza", 4.60, 14.50, 2.2),  # premium, low pop -> Puzzle
    ("Tartufo",               "Pizza", 5.40, 16.90, 1.3),  # premium, rare -> Puzzle
    ("Frutti di Mare",        "Pizza", 5.10, 15.90, 1.1),  # costly, rare -> Dog risk
    ("Calzone Classico",      "Pizza", 3.20, 11.90, 2.5),
    ("Pizza del Giorno",      "Pizza", 3.60, 12.50, 1.8),
    # Starters
    ("Bruschetta",            "Starter", 1.10, 5.50, 3.2),
    ("Garlic Bread",          "Starter", 0.80, 4.50, 4.0),
    ("Arancini",              "Starter", 1.60, 6.90, 2.0),
    ("Antipasto Misto",       "Starter", 3.20, 9.90, 1.4),
    # Pasta
    ("Spaghetti Carbonara",   "Pasta", 2.40, 10.90, 3.5),
    ("Lasagne",               "Pasta", 2.90, 11.50, 3.0),
    ("Penne Arrabbiata",      "Pasta", 1.90, 9.90, 2.2),
    # Salads
    ("Insalata Caprese",      "Salad", 2.20, 7.90, 2.0),
    ("Caesar Salad",          "Salad", 2.00, 8.50, 2.4),
    # Desserts
    ("Tiramisu",              "Dessert", 1.30, 5.90, 3.6),
    ("Panna Cotta",           "Dessert", 1.10, 5.50, 1.8),
    ("Gelato",                "Dessert", 0.90, 4.50, 2.6),
    # Beverages - very high margin (Stars if pushed)
    ("Soft Drink 33cl",       "Beverage", 0.40, 2.80, 9.0),
    ("Water 50cl",            "Beverage", 0.20, 2.00, 6.0),
    ("Beer 33cl",             "Beverage", 0.80, 3.90, 5.5),
    ("House Wine Glass",      "Beverage", 0.90, 4.50, 2.8),
    ("Espresso",              "Beverage", 0.30, 1.90, 3.4),
    ("Limoncello",            "Beverage", 0.70, 4.00, 1.2),
]
dim_product = pd.DataFrame(
    [(i + 1, *m) for i, m in enumerate(menu)],
    columns=["ProductID", "ProductName", "Category", "UnitCost", "UnitPrice", "_pop"])
dim_product.drop(columns=["_pop"]).to_csv(OUT / "DimProduct.csv", index=False)

pizza_ids   = dim_product.loc[dim_product.Category == "Pizza", "ProductID"].to_numpy()
pizza_pop   = dim_product.loc[dim_product.Category == "Pizza", "_pop"].to_numpy()
pizza_pop   = pizza_pop / pizza_pop.sum()
attach_ids  = dim_product.loc[dim_product.Category != "Pizza", "ProductID"].to_numpy()
attach_pop  = dim_product.loc[dim_product.Category != "Pizza", "_pop"].to_numpy()
attach_pop  = attach_pop / attach_pop.sum()
price_by_id = dim_product.set_index("ProductID")["UnitPrice"].to_dict()

# ---------------------------------------------------------------------------
# DIM_DATE  &  DIM_HOUR
# ---------------------------------------------------------------------------
holidays = set()  # a few Spanish-ish peak dates (holidays lift demand)
for y in (2024, 2025, 2026):
    for m, d in [(1,1),(1,6),(12,24),(12,25),(12,31),(5,1),(10,12),(8,15)]:
        holidays.add(date(y, m, d))
dd = pd.DataFrame({"Date": pd.to_datetime(DATES)})
dd["DateKey"]   = dd.Date.dt.strftime("%Y%m%d").astype(int)
dd["Year"]      = dd.Date.dt.year
dd["Quarter"]   = "Q" + dd.Date.dt.quarter.astype(str)
dd["Month"]     = dd.Date.dt.month
dd["MonthName"] = dd.Date.dt.strftime("%b")
dd["Day"]       = dd.Date.dt.day
dd["DOW"]       = dd.Date.dt.dayofweek            # 0=Mon
dd["WeekdayName"]= dd.Date.dt.strftime("%a")
dd["IsWeekend"] = dd.DOW.isin([4, 5, 6])          # Fri/Sat/Sun treated as weekend lift
dd["IsHoliday"] = dd.Date.dt.date.isin(holidays)
dd[["DateKey","Date","Year","Quarter","Month","MonthName","Day",
    "DOW","WeekdayName","IsWeekend","IsHoliday"]].to_csv(OUT / "DimDate.csv", index=False)

dim_hour = pd.DataFrame({"Hour": range(24)})
def daypart(h):
    if 12 <= h <= 15: return "Lunch"
    if 19 <= h <= 23: return "Dinner"
    if 16 <= h <= 18: return "Afternoon"
    return "Off-hours"
dim_hour["Daypart"] = dim_hour.Hour.map(daypart)
dim_hour.to_csv(OUT / "DimHour.csv", index=False)

# hour weight curve (Spain dines late): bimodal, dinner-heavy
hour_w = np.array([0,0,0,0,0,0,0,0,0,0,0,1,  # 0-11
                   6,9,7,2,1,1,2,7,10,10,8,4], dtype=float)  # 12-23
hour_w = hour_w / hour_w.sum()

# ---------------------------------------------------------------------------
# ORDER GENERATION  (vectorised per store-day)
# ---------------------------------------------------------------------------
season_by_month = {1:0.95,2:0.92,3:1.0,4:1.03,5:1.05,6:1.10,
                   7:1.15,8:0.80,9:1.05,10:1.02,11:1.0,12:1.20}  # Aug dip (holidays)
dow_factor = {0:0.80,1:0.82,2:0.85,3:0.95,4:1.35,5:1.55,6:1.25}   # Fri/Sat peak

date_meta = dd.set_index("Date")
orders_records = []   # (StoreID, DateKey, Date, ChannelID, Hour)
BASE = 26.0           # avg orders/store/day baseline (calibrated for ~1M lines)

for _, s in dim_store.iterrows():
    sid, traffic, basket = s.StoreID, s._traffic, s._basket
    open_dt = pd.to_datetime(s.OpeningDate)
    for dt in DATES:
        pdt = pd.Timestamp(dt)
        if pdt < open_dt:
            continue
        ramp = 1.0
        if s._archetype == "new_growing":
            days_open = (pdt - open_dt).days
            ramp = min(1.0, 0.35 + days_open / 240.0)   # ramps up over ~8 months
        mean = (BASE * traffic *
                dow_factor[pdt.dayofweek] *
                season_by_month[pdt.month] * ramp)
        if pdt.date() in holidays:
            mean *= 1.4
        n = rng.poisson(mean)
        if n == 0:
            continue
        dk = int(pdt.strftime("%Y%m%d"))
        # channel mix: delivery heavier on weekends/evenings
        is_wknd = pdt.dayofweek in (4, 5, 6)
        ch_p = [0.50, 0.20, 0.30] if not is_wknd else [0.40, 0.18, 0.42]
        chans = rng.choice([1, 2, 3], size=n, p=ch_p)
        hours = rng.choice(np.arange(24), size=n, p=hour_w)
        # delivery skews ~1h later
        hours = np.clip(hours + (chans == 3) * rng.integers(0, 2, size=n), 0, 23)
        for c, h in zip(chans, hours):
            orders_records.append((sid, dk, c, int(h), basket))

orders = pd.DataFrame(orders_records, columns=["StoreID","DateKey","ChannelID","Hour","_basket"])
orders.insert(0, "OrderID", np.arange(1, len(orders) + 1))
print(f"orders generated: {len(orders):,}")

# ---------------------------------------------------------------------------
# EXPLODE ORDERS -> ORDER LINES
# ---------------------------------------------------------------------------
n_ord = len(orders)
# lines per order depends on store basket factor (low basket -> fewer add-ons)
base_lines_p = np.array([0.30, 0.34, 0.22, 0.10, 0.04])   # 1..5 extra-attach baseline
# every order has 1 pizza (line 1) + N attach lines
lam = np.clip(1.4 * orders["_basket"].to_numpy(), 0.4, 3.0)
attach_counts = rng.poisson(lam)                 # extra (non-pizza) lines per order
attach_counts = np.clip(attach_counts, 0, 5)

# --- line 1: the pizza (one per order) ---
pizza_line = pd.DataFrame({
    "OrderID": orders.OrderID.to_numpy(),
    "ProductID": rng.choice(pizza_ids, size=n_ord, p=pizza_pop),
})
# --- attach lines (drinks/sides/desserts/pasta) ---
order_idx_for_attach = np.repeat(orders.OrderID.to_numpy(), attach_counts)
attach_line = pd.DataFrame({
    "OrderID": order_idx_for_attach,
    "ProductID": rng.choice(attach_ids, size=len(order_idx_for_attach), p=attach_pop),
})
lines = pd.concat([pizza_line, attach_line], ignore_index=True)

# join order context back onto each line
lines = lines.merge(orders[["OrderID","StoreID","ChannelID","DateKey","Hour"]],
                    on="OrderID", how="left")
# quantity: mostly 1, sometimes 2 (drinks a bit more)
q = np.ones(len(lines), dtype=int)
bump = rng.random(len(lines)) < 0.18
q[bump] = 2
lines["Quantity"] = q
# price at time of sale = base price; occasional promo discount
lines["UnitPrice"] = lines.ProductID.map(price_by_id).astype(float)
disc = np.zeros(len(lines))
promo = rng.random(len(lines)) < 0.06
disc[promo] = np.round(lines.loc[promo, "UnitPrice"] * lines.loc[promo, "Quantity"] * 0.15, 2)
lines["DiscountAmount"] = disc

fact = lines[["OrderID","StoreID","ChannelID","ProductID","DateKey","Hour",
              "Quantity","UnitPrice","DiscountAmount"]].sort_values(
              ["DateKey","OrderID"]).reset_index(drop=True)
fact.to_csv(OUT / "FactOrderLines.csv", index=False)

# ---------------------------------------------------------------------------
# SUMMARY + REALISM CHECKS
# ---------------------------------------------------------------------------
print(f"\nfact order-lines: {len(fact):,}")
for f in sorted(OUT.glob("*.csv")):
    print(f"  {f.name:22s} {f.stat().st_size/1e6:6.1f} MB  rows={sum(1 for _ in open(f))-1:,}")

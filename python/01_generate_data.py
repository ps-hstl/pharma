"""Generate synthetic pharma commercial data (reproducible, seed=42).
Planted business patterns: ~25% of doctors are mis-tiered by reps, so some
high-potential doctors are under-visited and some low-potential doctors are over-visited.
Sales respond to visits with diminishing returns."""
import numpy as np, pandas as pd
from pathlib import Path
rng = np.random.default_rng(42)
OUT = Path(__file__).resolve().parent.parent / "data" / "raw"

territories = pd.DataFrame({
    "territory_id": [f"T{i:02d}" for i in range(1, 9)],
    "territory_name": ["Mumbai","Pune","Delhi","Jaipur","Bengaluru","Chennai","Kolkata","Ahmedabad"],
    "region": ["West","West","North","North","South","South","East","West"]})
reps = pd.DataFrame({
    "rep_id": [f"R{i:03d}" for i in range(1, 25)],
    "rep_name": [f"Rep {i:02d}" for i in range(1, 25)],
    "territory_id": np.repeat(territories.territory_id, 3),
    "tenure_years": rng.integers(1, 12, 24)})
products = pd.DataFrame({
    "product_id": [f"P{i}" for i in range(1, 7)],
    "product_name": ["CardioSafe","GlucoBalance","RespiClear","NeuroCalm","GastroEase","VitaPlus"],
    "therapy_area": ["Cardiology","Diabetes","Respiratory","Neurology","Gastro","General Health"],
    "unit_price": [180, 150, 120, 220, 90, 60]})
specs = ["Cardiologist","Diabetologist","Pulmonologist","Neurologist","Gastroenterologist","General Physician"]
aff = np.array([[1.0,.25,.05,.05,.05,.3],[.2,1.0,.05,.05,.1,.3],[.05,.05,1.0,.05,.05,.3],
                [.05,.05,.05,1.0,.1,.25],[.05,.1,.05,.1,1.0,.3],[.3,.35,.3,.15,.25,.8]])
N = 1200
doc_terr = rng.choice(territories.territory_id, N, p=[.16,.12,.16,.08,.14,.12,.12,.10])
doctors = pd.DataFrame({
    "doctor_id": [f"D{i:04d}" for i in range(1, N+1)],
    "specialty": rng.choice(specs, N, p=[.14,.14,.12,.10,.12,.38]),
    "territory_id": doc_terr,
    "hospital_type": rng.choice(["Private Clinic","Private Hospital","Government Hospital","Multispecialty"], N, p=[.40,.25,.15,.20]),
    "experience_years": rng.integers(2, 35, N)})
doctors["rep_id"] = [rng.choice(reps[reps.territory_id==t].rep_id) for t in doctors.territory_id]
true_pot = rng.lognormal(3.0, 0.7, N)
doctors["est_monthly_potential"] = np.round(true_pot * rng.normal(1, .12, N)).clip(5).astype(int)
rank = pd.Series(true_pot).rank(pct=True).values
noisy = np.where(rng.random(N) < .25, rng.random(N), rank)
doctors["assigned_tier"] = pd.cut(noisy, [0,.6,.85,1.0], labels=["C","B","A"]).astype(str)
visit_mu = {"A":3.0, "B":1.6, "C":0.8}

months = pd.period_range("2025-01", "2025-12", freq="M")
season = np.array([.92,.9,.97,1.0,1.02,.98,.95,.97,1.03,1.08,1.1,1.08])
vrows = []
for i, d in doctors.iterrows():
    pr = aff[specs.index(d.specialty)]; pr = pr/pr.sum()
    for mi, m in enumerate(months):
        for _ in range(rng.poisson(visit_mu[d.assigned_tier])):
            p = rng.choice(6, p=pr)
            vrows.append((d.doctor_id, d.rep_id, products.product_id[p], f"2025-{mi+1:02d}-{rng.integers(1,28):02d}",
                          rng.choice(["In-person","Virtual"], p=[.8,.2]), int(rng.integers(5, 40)), int(rng.integers(0, 6))))
visits = pd.DataFrame(vrows, columns=["doctor_id","rep_id","product_id","visit_date","visit_type","duration_min","samples_given"])
visits.insert(0, "visit_id", [f"V{i:06d}" for i in range(1, len(visits)+1)])
visits["month"] = visits.visit_date.str[:7]

vc = visits.groupby(["doctor_id","product_id","month"]).size().to_dict()
srows = []
for i, d in doctors.iterrows():
    a = aff[specs.index(d.specialty)]
    for pi in range(6):
        for mi, m in enumerate(months):
            v = vc.get((d.doctor_id, products.product_id[pi], str(m)), 0)
            lam = true_pot[i] * a[pi] * 0.55 * (1 + 1.1*(1-np.exp(-v/1.5))) * season[mi] * (1 + .012*mi)
            units = rng.poisson(lam)
            if units > 0:
                srows.append((d.doctor_id, products.product_id[pi], str(m), units, int(units*products.unit_price[pi])))
sales = pd.DataFrame(srows, columns=["doctor_id","product_id","month","units","revenue"])
sales.insert(0, "sale_id", [f"S{i:06d}" for i in range(1, len(sales)+1)])

for n, df in dict(territories=territories, reps=reps, products=products, doctors=doctors, visits=visits, sales=sales).items():
    df.to_csv(OUT/f"{n}.csv", index=False); print(n, df.shape)

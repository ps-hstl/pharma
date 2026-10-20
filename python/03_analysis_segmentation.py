"""EDA + doctor segmentation (rule-based potential x engagement matrix + KMeans) + reallocation simulation.
Outputs: reports/charts/*.png, data/powerbi/*.csv, reports/key_numbers.json"""
import json, sqlite3, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
ROOT = Path(__file__).resolve().parent.parent
con = sqlite3.connect(ROOT/"data"/"pharmapulse.db")
CH, PB = ROOT/"reports"/"charts", ROOT/"data"/"powerbi"
plt.rcParams.update({"figure.dpi":130,"axes.spines.top":False,"axes.spines.right":False,"font.size":9})
NAVY, TEAL, ORANGE, RED, GREY = "#1F3A5F", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"

doctors = pd.read_sql("select * from doctors", con)
visits  = pd.read_sql("select * from visits", con)
sales   = pd.read_sql("select * from sales", con)
terr    = pd.read_sql("select * from territories", con)
prod    = pd.read_sql("select * from products", con)
reps    = pd.read_sql("select * from reps", con)

# ---------- 1. Doctor feature table ----------
f = doctors.set_index("doctor_id")
f["visits_12m"]  = visits.groupby("doctor_id").size()
f["revenue_12m"] = sales.groupby("doctor_id").revenue.sum()
f["units_12m"]   = sales.groupby("doctor_id").units.sum()
h1 = sales[sales.month<="2025-06"].groupby("doctor_id").revenue.sum()
h2 = sales[sales.month> "2025-06"].groupby("doctor_id").revenue.sum()
f["h1_revenue"], f["h2_revenue"] = h1, h2
f["products_prescribed"] = sales.groupby("doctor_id").product_id.nunique()
f = f.fillna({"visits_12m":0,"revenue_12m":0,"units_12m":0,"h1_revenue":0,"h2_revenue":0,"products_prescribed":0})
f["growth_pct"] = np.where(f.h1_revenue>0, (f.h2_revenue/f.h1_revenue-1)*100, 0)
f["revenue_per_visit"] = f.revenue_12m/f.visits_12m.replace(0,np.nan)
f["visits_per_month"] = f.visits_12m/12

# ---------- 2. Rule-based segmentation: Potential x Engagement ----------
pot_cut = f.est_monthly_potential.quantile(.67)       # top third = high potential
vis_cut = f.visits_12m.median()                       # median visits = high engagement
hp, he = f.est_monthly_potential>=pot_cut, f.visits_12m>=vis_cut
f["segment"] = np.select([hp&he, hp&~he, ~hp&he], ["Protect & Grow (Core)","Under-served (Increase)","Over-served (Reduce)"], "Maintain (Low-touch)")
f["potential_group"] = np.where(hp,"High","Low/Mid")

# ---------- 3. KMeans (data-driven check) ----------
X = f[["est_monthly_potential","visits_12m","revenue_12m","growth_pct","products_prescribed"]].copy()
X["revenue_12m"], X["est_monthly_potential"] = np.log1p(X.revenue_12m), np.log1p(X.est_monthly_potential)
Xs = StandardScaler().fit_transform(X)
from sklearn.metrics import silhouette_score
sil = {k: round(silhouette_score(Xs, KMeans(k, n_init=10, random_state=42).fit_predict(Xs)),3) for k in range(2,8)}
BEST_K = max(sil, key=sil.get)   # pick k by silhouette
f["cluster"] = KMeans(BEST_K, n_init=10, random_state=42).fit_predict(Xs)
prof = f.groupby("cluster").agg(doctors=("segment","size"), potential=("est_monthly_potential","mean"), visits=("visits_12m","mean"),
        revenue=("revenue_12m","mean"), growth=("growth_pct","mean"), products=("products_prescribed","mean")).round(1)
print("Silhouette by k:", sil); print(prof)

# ---------- 4. Visit-response model & reallocation simulation ----------
d = f[f.visits_12m>0].copy()
Xm = np.column_stack([np.ones(len(d)), np.log(d.visits_12m), np.log(d.est_monthly_potential)])
beta, *_ = np.linalg.lstsq(Xm, np.log1p(d.revenue_12m), rcond=None)
ELAST = beta[1]; print(f"Log-log visit elasticity (controlling for potential): {ELAST:.3f}")
seg = f.groupby("segment").agg(doctors=("segment","size"), visits=("visits_12m","sum"), revenue=("revenue_12m","sum"),
        avg_potential=("est_monthly_potential","mean"), avg_visits=("visits_12m","mean"))
cut_pct, give = 0.30, 0                       # cut 30% of visits to over-served, move to under-served
ov, un = f.segment=="Over-served (Reduce)", f.segment=="Under-served (Increase)"
freed = (f.loc[ov,"visits_12m"]*cut_pct).sum()
new_v = f.visits_12m.astype(float).copy()
new_v[ov] *= (1-cut_pct)
new_v[un] += freed * (f.loc[un,"est_monthly_potential"]/f.loc[un,"est_monthly_potential"].sum())
ratio = (new_v.clip(lower=1)/f.visits_12m.clip(lower=1))
f["sim_revenue"] = f.revenue_12m * ratio**ELAST
uplift = f.sim_revenue.sum()-f.revenue_12m.sum()
sim = {"visits_moved": int(freed), "baseline_revenue": int(f.revenue_12m.sum()), "simulated_revenue": int(f.sim_revenue.sum()),
       "uplift": int(uplift), "uplift_pct": round(uplift/f.revenue_12m.sum()*100,2), "elasticity": round(float(ELAST),3)}
print(sim)

# ---------- 5. Key numbers ----------
tot = f.revenue_12m.sum()
srt = f.revenue_12m.sort_values(ascending=False)
key = {"doctors": len(f), "visits": int(f.visits_12m.sum()), "revenue": int(tot),
       "top20pct_doctor_share": round(srt.head(int(len(f)*.2)).sum()/tot*100,1),
       "tierC_high_potential": int(((f.assigned_tier=="C")&hp).sum()),
       "tierA_not_high_potential": int(((f.assigned_tier=="A")&~hp).sum()),
       "segment_counts": f.segment.value_counts().to_dict(),
       "segment_visit_share": (seg.visits/seg.visits.sum()*100).round(1).to_dict(),
       "segment_revenue_share": (seg.revenue/seg.revenue.sum()*100).round(1).to_dict(),
       "segment_avg_visits": seg.avg_visits.round(1).to_dict(), "segment_avg_potential": seg.avg_potential.round(1).to_dict(),
       "silhouette": sil, "simulation": sim,
       "high_pot_declining": int(((f.growth_pct<-10)&hp).sum())}
json.dump(key, open(ROOT/"reports"/"key_numbers.json","w"), indent=2, default=str); print(json.dumps(key, indent=1, default=str))

# ---------- 6. Charts ----------
mo = sales.groupby("month").revenue.sum()/1e6
terr_rev = sales.merge(doctors[["doctor_id","territory_id"]]).groupby("territory_id").revenue.sum().rename("revenue").reset_index().merge(terr)
terr_rev = terr_rev.sort_values("revenue")
pr = sales.merge(prod).groupby("product_name").revenue.sum().sort_values()/1e6
colors = {"Protect & Grow (Core)":NAVY,"Under-served (Increase)":RED,"Over-served (Reduce)":ORANGE,"Maintain (Low-touch)":GREY}

def save(fig, name): fig.tight_layout(); fig.savefig(CH/name); plt.close(fig)
fig, ax = plt.subplots(figsize=(6,3.2)); ax.plot(mo.index, mo.values, marker="o", color=NAVY); ax.set_title("Monthly revenue (Rs M)"); ax.tick_params(axis="x", rotation=45); save(fig,"01_monthly_revenue.png")
fig, ax = plt.subplots(figsize=(6,3.2)); ax.barh(terr_rev.territory_name, terr_rev.revenue/1e6, color=TEAL); ax.set_title("Revenue by territory (Rs M)"); save(fig,"02_territory_revenue.png")
fig, ax = plt.subplots(figsize=(6,3.2)); ax.barh(pr.index, pr.values, color=NAVY); ax.set_title("Revenue by product (Rs M)"); save(fig,"03_product_revenue.png")
fig, ax = plt.subplots(figsize=(6.5,4.5))
for s,c in colors.items():
    m = f.segment==s; ax.scatter(f[m].est_monthly_potential, f[m].visits_12m, s=9, alpha=.6, color=c, label=f"{s} ({m.sum()})")
ax.axvline(pot_cut, ls="--", color="k", lw=.7); ax.axhline(vis_cut, ls="--", color="k", lw=.7)
ax.set_xlabel("Estimated monthly Rx potential"); ax.set_ylabel("Visits in 2025"); ax.set_title("Doctor segmentation: potential vs visit effort"); ax.legend(fontsize=7, frameon=False); save(fig,"04_segmentation_matrix.png")
fig, axs = plt.subplots(1,2, figsize=(8,3.2)); order=list(colors)
sv = seg.loc[order]; x=np.arange(4)
axs[0].bar(x-.2, sv.visits/sv.visits.sum()*100, .4, label="% of visits", color=ORANGE); axs[0].bar(x+.2, sv.revenue/sv.revenue.sum()*100, .4, label="% of revenue", color=NAVY)
axs[0].set_xticks(x); axs[0].set_xticklabels([o.split(" (")[0] for o in order], rotation=20, fontsize=7); axs[0].legend(frameon=False, fontsize=7); axs[0].set_title("Effort vs outcome by segment")
tm = pd.crosstab(f.assigned_tier, pd.cut(f.est_monthly_potential,[0,f.est_monthly_potential.quantile(.33),pot_cut,1e9],labels=["Low","Mid","High"])).loc[["A","B","C"]]
tm.plot(kind="bar", stacked=True, ax=axs[1], color=[GREY,TEAL,RED], rot=0); axs[1].set_title("Rep tier vs true potential"); axs[1].set_xlabel("Assigned tier"); axs[1].legend(title="True potential", frameon=False, fontsize=7)
save(fig,"05_effort_vs_outcome.png")
fig, ax = plt.subplots(figsize=(5.5,3.2)); ax.plot(list(sil), list(sil.values()), marker="o", color=NAVY); ax.set_title("KMeans silhouette score by k"); ax.set_xlabel("k"); save(fig,"06_kmeans_silhouette.png")

# Dashboard preview (what the Power BI page should look like)
fig = plt.figure(figsize=(14,8)); gs = fig.add_gridspec(3,4, height_ratios=[.45,1,1])
kp = [("Revenue", f"Rs {tot/1e6:.1f}M"),("Doctors", f"{len(f):,}"),("Visits", f"{int(f.visits_12m.sum()):,}"),("Revenue / visit", f"Rs {tot/f.visits_12m.sum():,.0f}")]
for i,(k,v) in enumerate(kp):
    a = fig.add_subplot(gs[0,i]); a.axis("off"); a.text(.5,.62,v,ha="center",fontsize=22,color=NAVY,weight="bold"); a.text(.5,.15,k,ha="center",fontsize=11,color="#555")
a=fig.add_subplot(gs[1,:2]); a.plot(mo.index, mo.values, marker="o", color=NAVY); a.set_title("Monthly revenue (Rs M)"); a.tick_params(axis="x", rotation=45)
a=fig.add_subplot(gs[1,2:]); a.barh(terr_rev.territory_name, terr_rev.revenue/1e6, color=TEAL); a.set_title("Revenue by territory (Rs M)")
a=fig.add_subplot(gs[2,:2])
for s,c in colors.items():
    m=f.segment==s; a.scatter(f[m].est_monthly_potential, f[m].visits_12m, s=6, alpha=.6, color=c, label=s.split(" (")[0])
a.set_title("Doctor segments: potential vs visits"); a.legend(fontsize=7, frameon=False, ncol=2)
a=fig.add_subplot(gs[2,2:]); a.bar(x-.2, sv.visits/sv.visits.sum()*100, .4, color=ORANGE, label="% visits"); a.bar(x+.2, sv.revenue/sv.revenue.sum()*100, .4, color=NAVY, label="% revenue")
a.set_xticks(x); a.set_xticklabels([o.split(" (")[0] for o in order], fontsize=8); a.legend(frameon=False); a.set_title("Effort vs outcome by segment")
fig.suptitle("PharmaPulse - Dashboard preview (matplotlib mock of the Power BI page)", fontsize=13, weight="bold"); fig.tight_layout(); fig.savefig(CH/"07_dashboard_preview.png"); plt.close(fig)

# ---------- 7. Exports for Power BI ----------
dd = f.reset_index()
dd.drop(columns=["h1_revenue","h2_revenue"]).round(2).to_csv(PB/"dim_doctor.csv", index=False)
terr.to_csv(PB/"dim_territory.csv", index=False); prod.to_csv(PB/"dim_product.csv", index=False); reps.to_csv(PB/"dim_rep.csv", index=False)
pd.DataFrame({"month":sorted(sales.month.unique())}).assign(month_start=lambda x: x.month+"-01", month_num=lambda x: range(1,13),
    month_name=lambda x: pd.to_datetime(x.month_start).dt.strftime("%b"), quarter=lambda x: "Q"+pd.to_datetime(x.month_start).dt.quarter.astype(str)).to_csv(PB/"dim_date.csv", index=False)
visits.to_csv(PB/"fact_visits.csv", index=False); sales.to_csv(PB/"fact_sales.csv", index=False)
f.groupby("segment").agg(doctors=("segment","size"), avg_potential=("est_monthly_potential","mean"), avg_visits=("visits_12m","mean"), revenue=("revenue_12m","sum"), sim_revenue=("sim_revenue","sum")).round(1).to_csv(PB/"segment_summary.csv")
print("done")

import pandas as pd, numpy as np
from pathlib import Path

FILES = {
    "PPO": "reports/ppo_v3_guard_best_1e6.csv",
    "QRDQN": "reports/qrdqn_eval_1e6.csv",
    "Newsvendor": "reports/baselines.csv",
}

def per_seed(path,label):
    df = pd.read_csv(path)
    if label=="Newsvendor":
        df = df[df["policy"].str.lower()=="newsvendor"].copy()
        df["policy"] = "Newsvendor"
    else:
        df["policy"] = label
    for c in ["profit","avg_wait_seconds","abandoned","leftover_units"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return (df.groupby(["policy","seed"],as_index=False)
              .agg(profit=("profit","mean"),
                   wait=("avg_wait_seconds","mean"),
                   aband=("abandoned","mean"),
                   waste=("leftover_units","mean")))

by = pd.concat([per_seed(p,l) for l,p in FILES.items()], ignore_index=True)

def summarize(v):
    v = pd.to_numeric(v, errors="coerce").dropna()
    n=v.size; mu=v.mean()
    sd = v.std(ddof=1) if n>1 else float("nan")
    se = sd/np.sqrt(n) if n>1 else float("nan")
    ci = 1.96*se if n>1 else float("nan")
    return n, mu, sd, se, ci

rows=[]
for pol,grp in by.groupby("policy"):
    n,mu,sd,se,ci = summarize(grp["profit"])
    rows.append((pol,n,mu,sd,se,ci))
rows.sort()
summary = pd.DataFrame(rows, columns=["policy","n","mean_profit","sd","se","ci95"])

wide = by.pivot(index="seed", columns="policy", values="profit").dropna()
def boot_ci(arr,B=10000,seed=0):
    rng=np.random.default_rng(seed)
    if len(arr)==0: return float("nan"), float("nan")
    idx=rng.integers(0,len(arr),(B,len(arr)))
    bs = arr[idx].mean(axis=1)
    return float(np.quantile(bs,0.025)), float(np.quantile(bs,0.975))
pairs=[]
if "Newsvendor" in wide.columns:
    for pol in [c for c in ["PPO","QRDQN"] if c in wide.columns]:
        d=(wide[pol]-wide["Newsvendor"]).dropna().values
        lo,hi = boot_ci(d)
        pairs.append((f"{pol} - Newsvendor", float(d.mean()) if d.size else float("nan"), lo, hi, int(d.size)))
pairtbl = pd.DataFrame(pairs, columns=["comparison","mean_diff","ci_lo","ci_hi","n_pairs"])

Path("reports").mkdir(exist_ok=True)
summary.to_csv("reports/stats_profit_summary.csv", index=False)
pairtbl.to_csv("reports/stats_vs_newsvendor.csv", index=False)
print(summary.to_string(index=False, formatters={"mean_profit":"{:.2f}".format,"sd":"{:.2f}".format,"se":"{:.2f}".format,"ci95":"{:.2f}".format}))
print()
print(pairtbl.to_string(index=False, formatters={"mean_diff":"{:.2f}".format,"ci_lo":"{:.2f}".format,"ci_hi":"{:.2f}".format}))

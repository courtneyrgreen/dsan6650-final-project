## Bellman's Bakery — Project Context (share this in a new chat)

This document summarizes the project so a fresh assistant session has full context.

### What this project is
- A pastel café simulator where an agent manages baking, serving, and pricing to maximize profit and customer delight.
- Deep RL: PPO with action masking for within‑day scheduling.
- Shallow RL: a Thompson‑sampling pricing bandit that picks a global daily price multiplier in {0.9, 1.0, 1.1}.

### Key environment choices (MDP)
- Episode: one “day”, fixed 240 ticks (10s per tick).
- Ovens: 2; capacity = 4 units. Item sizes: red velvet 3u, drip cake 4u, slice 1u, rolls 1.5u.
- Bake times (seconds): red velvet 90, matcha roll 60, strawberry slice 36, drip cake 120, orange roll 60.
- Batch yields: red velvet 2, matcha roll 4, slice 4, drip cake 1, orange roll 4.
- Prices: $6.00, $4.50, $3.50, $8.00, $4.50 (cost = 40% of price).
- Queue: cap 12; customers abandon with patience 30–90s; serve can target any matching customer (not restricted to head‑of‑line).
- Demand: 60/day, time‑of‑day peaks, skewed mix (slice 30%, rolls 20% each, red velvet 15%, drip 15%), mild non‑stationarity (±10% daily, ±10% weekly item swings).
- Rewards: +price − cost +0.1 on serve; −0.02 per tick per waiting customer; −0.5 on abandonment; −cost for leftover waste at day end; small idle penalty.

### Repo layout (after cleanup)
- `bellmans_bakery/` — `env.py` (environment), `viewer.py` (Pygame viewer).
- `scripts/`
  - `training.py` — one function `train(use_bandit: bool, steps: int, ...)` for PPO and PPO+bandit.
  - `evaluate.py` — `eval_baselines(...)` and `eval_model(...)` produce CSVs.
  - `pricing_bandit.py` — Thompson‑sampling wrapper.
  - `baselines.py` — heuristic policies (bake‑to‑par, greedy, newsvendor).
  - `export_tb_plots.py` — export TensorBoard scalars to PNGs.
  - `run.py` — single CLI entrypoint that calls the above.
- `images/desserts/` — UI assets.
- `models/` — flat model files (`ppo_*.zip`, `ppo_bandit_*.zip`, plus `best_ppo.zip`, `best_ppo_bandit.zip`).
- `runs/` — TensorBoard logs for each training run (`runs/ppo`, `runs/ppo_bandit`, etc.).
- `reports/figs/` — exported PNG plots.

### One‑line commands (Windows PowerShell, project root)
- PPO quick sanity (3e5 steps):
```
python -m scripts.run train --steps 300000
```
- PPO + bandit:
```
python -m scripts.run train --bandit --steps 300000
```
- Longer runs (overnight, better results):
```
python -m scripts.run train --steps 1000000
python -m scripts.run train --bandit --steps 1000000
```
- Baselines CSV (heuristics):
```
python -m scripts.run eval-baselines --seeds 5 --days 10 --out reports/baselines.csv
```
- Evaluate a trained model to CSV:
```
python -m scripts.run eval-model --model models/ppo_1000000.zip --out reports/ppo_eval.csv
python -m scripts.run eval-model --model models/ppo_bandit_1000000.zip --bandit --out reports/ppo_bandit_eval.csv
```
- Export plots (reward curves only):
```
python -m scripts.export_tb_plots --logdir runs/ppo --outdir reports/figs/ppo
python -m scripts.export_tb_plots --logdir runs/ppo_bandit --outdir reports/figs/ppo_bandit
```
- Viewer (uses your PNGs):
```
python -m scripts.run_viewer --model models/best_ppo.zip
python -m scripts.run_viewer --model models/best_ppo_bandit.zip
```

### What to look at in results
- Reward plots: `rollout/ep_rew_mean`, `eval/mean_reward` (we intentionally skip episode length since the day length is fixed).
- CSVs: profit per day, abandonment %, avg wait seconds, waste %, service level; compare PPO, PPO+bandit, and baselines.
- If curves keep rising near the end of training at 3e5 steps, scale to 1e6–2e6.

### How to change difficulty (for ablations or to make learning non‑trivial)
- Reduce patience to 20–60s; start inventory to zero; make capacity 3u or 1 oven.
- Increase arrival peaks or overall average customers (e.g., 80/day).
- Force head‑of‑line serving only (no queue skipping).
- Increase non‑stationarity (e.g., ±20%) so bandit matters more.

### Notes
- The exporter needs a concrete run folder (e.g., `runs/ppo/PPO_2`) if the top level has multiple runs. Use `Get-ChildItem runs\\ppo -Recurse -Filter "events.*"` to find the freshest event file.
- Episode length is constant (240 ticks) by design; it appears only for completeness.



# Bellman's Bakery — RL Final Project

Quick start (Windows PowerShell, CPU):

1) Create/activate env and install deps

```powershell
conda create -n bakery-rl python=3.11 -y
conda activate bakery-rl
python -m pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install gymnasium==0.29.1 stable-baselines3==2.3.0 sb3-contrib==2.3.0 numpy>=1.24 pygame>=2.5.2 tqdm rich tensorboard matplotlib
```

2) Train a quick PPO model (≈20–30 min CPU)

```powershell
python -m scripts.run train --steps 300000
```

Train PPO with pricing bandit (global daily 0.9/1.0/1.1 multipliers via Thompson Sampling)

```powershell
python -m scripts.run train --bandit --steps 300000
```

3) Visualize with the cute viewer (uses your PNGs under `images/desserts/`)

```powershell
python -m scripts.run_viewer --model models/best_ppo.zip
```

4) TensorBoard (training curves)

```powershell
tensorboard --logdir runs/ppo
```

This project implements a day‑level bakery simulator with capacity‑constrained ovens, skewed demand, queueing and abandonment, and a PPO agent with action masking. A global daily pricing multiplier (bandit) is included; EvalCallback logs `eval/mean_reward` alongside rollout metrics.

Key modules:
- `bellmans_bakery/` — package import for env and viewer (`BellmansBakeryEnv`, `PastelViewer`)
- `scripts/` — training (`training.py`), evaluation (`evaluate.py`), pricing bandit, baselines, TensorBoard exporter, unified CLI (`run.py`), and viewer runner.
- `images/desserts/` — item art assets

Note: episode length is constant (= day_ticks=240) by design; focus on reward/profit curves and baseline comparisons.

Planned reporting artifacts:
- Training curves: `rollout/ep_rew_mean`, `eval/mean_reward` (from TensorBoard)
- Final evaluation table vs baselines (FIFO + bake‑to‑stock + newsvendor)
- Ablations: without masking, without wait penalty, stationary vs non‑stationary demand

Final Project for Georgetown Data Science & Analytics 

# Bellman's Bakery (DSAN 6650 — Reinforcement Learning)

Final project for Georgetown University — Data Science & Analytics (DSAN 6650, Reinforcement Learning).

Bellman’s Bakery is a stylized RL environment of a one‑day bakery with two capacity‑constrained ovens, stochastic arrivals, customer patience/abandonment, and non‑stationary demand. We train and evaluate agents (PPO with action masking, plus baselines) and provide a lightweight Pygame viewer for demos and screenshots.

## Project structure

- `bellmans_bakery/`
  - `env.py`: `BellmansBakeryEnv` (Gymnasium). Discrete time, 10s per tick, queueing, baking, serving.
  - `viewer.py`: `PastelViewer` used for live demos and screenshots.
- `scripts/`
  - `run.py`: unified CLI for training/evaluation.
  - `training.py`, `evaluate.py`, `baselines.py`, `pricing_bandit.py`.
  - `run_viewer.py`: launches the viewer and optionally loads a trained model.
- `images/`: art assets (`images/oven.png`, `images/desserts/*.png`).
- `website-source/`: report site sources (Quarto).

## Environment at a glance

- Actions: 11 discrete actions → serve one of 5 items, bake one of 5 items, idle.
- Two ovens with 4u capacity; items have sizes and bake times; completed bakes add inventory.
- Customers arrive stochastically with demand mix; each has patience and may abandon.
- Reward primarily tracks sales margin minus penalties (waiting, abandonment).
- Optional global daily pricing multiplier controlled by a simple bandit.

## Setup (Windows PowerShell, CPU)

```powershell
conda create -n bakery-rl python=3.11 -y
conda activate bakery-rl
python -m pip install --upgrade pip

# PyTorch CPU wheels (GPU users can install the CUDA build instead)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Core dependencies
pip install gymnasium==0.29.1 stable-baselines3==2.3.0 sb3-contrib==2.3.0 numpy>=1.24 pygame>=2.5.2 tqdm rich tensorboard matplotlib imageio
```

Notes
- If Pygame can’t open a window, ensure you’re not in WSL and your Python is a desktop build.
- All commands run from the project root: `dsan6650-final-project/`.

## Quickstart: train PPO and preview in the viewer

1) Train a small PPO policy (≈20–30 min CPU)
```powershell
python -m scripts.run train --steps 300000
```

Optional: train with a simple pricing bandit (global 0.9/1.0/1.1 multiplier via Thompson Sampling):
```powershell
python -m scripts.run train --bandit --steps 300000
```

2) Launch the viewer (loads `models/best_ppo.zip` if present; otherwise runs a random policy)
```powershell
python -m scripts.run_viewer --model models/best_ppo.zip
```

Viewer controls
- Space or `P`: pause / resume the simulation.
- `S` or `F12`: save a PNG screenshot to `screenshots/` (auto‑created).
- `--fps 30`: control the playback speed (default 30 FPS).
- Optional video capture (writes MP4 from in‑memory frames, no screen recorder needed):
  ```powershell
  # For site embedding (Quarto copies website-source/videos/* to docs/videos/*)
  python -m scripts.run_viewer --baseline newsvendor --record_mp4 website-source/videos/viewer_index_demo.mp4 --record_seconds 12

  # Or any arbitrary clip location
  python -m scripts.run_viewer --model models/best_ppo.zip --record_mp4 runs/demo.mp4 --record_seconds 20
  ```

## Reproducing training curves

```powershell
# Train
python -m scripts.run train --steps 500000

# Launch TensorBoard
tensorboard --logdir runs/ppo
```

Typical logs include:
- `rollout/ep_rew_mean`, `train/value_loss`, `train/policy_gradient_loss`
- `eval/mean_reward` from periodic evaluation episodes

## Baselines and evaluation

We include simple baselines in `scripts/baselines.py` (e.g., FIFO serve, bake‑to‑stock heuristics). Evaluate via:
```powershell
python -m scripts.run eval --model models/best_ppo.zip --episodes 20
```

## Report and deliverables

- The write‑up and figures are generated from `website-source/` (Quarto).
- Key comparisons: PPO vs simple heuristics; ablations (masking, penalties, non‑stationarity).

## Troubleshooting

- If dessert or oven images don’t appear, verify files exist under `images/oven.png` and `images/desserts/*.png`.
- If you see “Model not found… running a random policy”, confirm `--model` points to an existing `.zip` or train first.
- On macOS/Linux, replace PowerShell commands with your shell equivalents and ensure a GUI session is available for Pygame.

---

This repository is the final project submission for Georgetown DSAN 6650 (Reinforcement Learning).

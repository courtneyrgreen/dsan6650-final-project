import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator


def load_scalar(path: Path, tag: str):
    ea = EventAccumulator(str(path))
    ea.Reload()
    if tag not in ea.Tags().get("scalars", []):
        return None, None
    events = ea.Scalars(tag)
    steps = np.array([e.step for e in events], dtype=np.int64)
    vals = np.array([e.value for e in events], dtype=np.float64)
    return steps, vals


def _find_event_file(logdir: Path) -> Path | None:
    runs = sorted(logdir.glob("**/events.*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return runs[0] if runs else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--logdir", type=str, default=None, help="Single run directory")
    parser.add_argument("--outdir", type=str, default="reports/figs")
    parser.add_argument(
        "--series",
        action="append",
        default=None,
        help='Overlay multiple runs: label=RUN_DIR (e.g., "PPO=runs/ppo_v3_guard_1e6")',
    )
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Build list of (label, event_file)
    series: list[tuple[str, Path]] = []
    if args.series:
        for s in args.series:
            if "=" not in s:
                print(f"Ignoring malformed --series: {s}")
                continue
            label, path = s.split("=", 1)
            ev = _find_event_file(Path(path))
            if ev is None:
                print(f"No TB event files in: {path}")
                continue
            series.append((label.strip(), ev))
    elif args.logdir:
        ev = _find_event_file(Path(args.logdir))
        if ev is None:
            print("No TensorBoard event files found.")
            return
        series.append(("run", ev))
    else:
        print("Provide --logdir or one/more --series entries.")
        return

    # Export reward-focused plots; overlay if multiple series
    plots = [
        ("rollout/ep_rew_mean", "Episode reward (mean)"),
        ("eval/mean_reward", "Eval mean reward"),
    ]

    colors = ["#8a5fbf", "#ff6b6b", "#4dabf7", "#51cf66", "#ffa94d", "#f06595", "#74c0fc"]

    for tag, title in plots:
        plt.figure(figsize=(7.5, 4.5))
        any_ok = False
        for i, (label, ev) in enumerate(series):
            steps, vals = load_scalar(ev, tag)
            if steps is None:
                print(f"[{label}] Tag missing: {tag}")
                continue
            any_ok = True
            c = colors[i % len(colors)]
            plt.plot(steps, vals, label=label, color=c, linewidth=1.8)
        if not any_ok:
            plt.close()
            continue
        plt.title(title)
        plt.xlabel("steps")
        plt.ylabel(tag)
        plt.grid(alpha=0.2)
        if len(series) > 1:
            plt.legend(loc="best", frameon=False)
        outfile = outdir / (tag.replace("/", "_") + ("" if len(series) == 1 else "_overlay") + ".png")
        plt.tight_layout()
        plt.savefig(outfile, dpi=160)
        plt.close()
        print(f"Saved {outfile}")


if __name__ == "__main__":
    main()



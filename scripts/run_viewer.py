import argparse
import time

import pygame
from sb3_contrib import MaskablePPO
from sb3_contrib.qrdqn import QRDQN
from sb3_contrib.common.wrappers import ActionMasker

from bellmans_bakery import BellmansBakeryEnv, PastelViewer


def mask_fn(env):
    return env.unwrapped._action_mask()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="models/best_ppo.zip")
    parser.add_argument("--algo", type=str, choices=["ppo", "qrdqn"], default="ppo")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument(
        "--screenshot-dir", type=str, default="screenshots", help="Where to save PNGs"
    )
    parser.add_argument(
        "--record_mp4",
        type=str,
        default=None,
        help="If set, save a video (MP4) directly from Pygame frames to this path",
    )
    parser.add_argument(
        "--record_seconds",
        type=int,
        default=None,
        help="Optional limit for recording duration (in seconds)",
    )
    args = parser.parse_args()

    env = ActionMasker(BellmansBakeryEnv(), mask_fn)
    viewer = PastelViewer()

    # Load model if present
    try:
        if args.algo == "qrdqn":
            model = QRDQN.load(args.model, env=env)
        else:
            model = MaskablePPO.load(args.model, env=env)
    except Exception:
        model = None
        print(f"Model not found or unsupported at {args.model}; running a random policy for preview.")

    obs, info = env.reset()
    done = False
    paused = False

    # Ensure screenshot directory exists
    import os
    os.makedirs(args.screenshot_dir, exist_ok=True)

    # Optional MP4 recording (pure Python, no screen capture)
    writer = None
    frames_recorded = 0
    if args.record_mp4:
        try:
            import imageio.v2 as imageio

            os.makedirs(os.path.dirname(args.record_mp4) or ".", exist_ok=True)
            writer = imageio.get_writer(args.record_mp4, fps=max(1, int(args.fps)))
        except Exception as e:
            print(f"Could not initialize MP4 writer: {e}")
            writer = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if writer is not None:
                    try:
                        writer.close()
                    except Exception:
                        pass
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_p):
                    paused = not paused
                elif event.key in (pygame.K_s, pygame.K_F12):
                    # Save current frame
                    import time as _time
                    ts = _time.strftime("%Y%m%d-%H%M%S")
                    path = os.path.join(args.screenshot_dir, f"viewer_{ts}.png")
                    pygame.image.save(viewer.screen, path)
                    print(f"Saved screenshot: {path}")
        if not done:
            if not paused:
                if model:
                    action, _ = model.predict(obs, deterministic=True)
                else:
                    action = env.action_space.sample()
                obs, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated
        else:
            obs, info = env.reset()
            done = False
        viewer.render(env)

        # Append frame to MP4 if enabled
        if writer is not None:
            try:
                import numpy as np
                import pygame.surfarray as surfarray

                frame = surfarray.array3d(viewer.screen)  # (W, H, 3), RGB
                frame = np.transpose(frame, (1, 0, 2))    # -> (H, W, 3)
                writer.append_data(frame)
                frames_recorded += 1
                if args.record_seconds is not None:
                    if frames_recorded >= int(args.record_seconds * max(1, int(args.fps))):
                        try:
                            writer.close()
                        except Exception:
                            pass
                        writer = None
                        print("Stopped recording (duration reached).")
            except Exception as e:
                print(f"Frame write failed: {e}")
                try:
                    writer.close()
                except Exception:
                    pass
                writer = None

        time.sleep(1.0 / args.fps)


if __name__ == "__main__":
    main()



from pathlib import Path
from typing import Dict

import pygame

from .env import ITEM_NAMES, ITEM_BAKE_SECONDS


class PastelViewer:
    """
    Lightweight Pygame viewer for Bellman's Bakery.
    The viewer reads the env's public attributes via `env.unwrapped`.
    """

    def __init__(self, width: int = 900, height: int = 640):
        pygame.init()
        pygame.display.set_caption("Bellman's Bakery — Viewer")
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        mont = pygame.font.match_font("montserrat")
        if mont:
            self.font = pygame.font.Font(mont, 24)
            self.small = pygame.font.Font(mont, 18)
            self.title = pygame.font.Font(mont, 28)
        else:
            self.font = pygame.font.SysFont("arial", 24)
            self.small = pygame.font.SysFont("arial", 18)
            self.title = pygame.font.SysFont("arial", 28, bold=True)

        # Palette
        self.COLORS = {
            "bg": (250, 218, 221),  # pink
            "cream": (255, 247, 230),
            "mint": (223, 245, 225),
            "lav": (233, 216, 253),
            "text": (60, 60, 60),
            "queue": (190, 170, 210),
            "queue_border": (160, 140, 190),
        }

        # Load item images
        root = Path(__file__).resolve().parents[1]
        img_dir = root / "images" / "desserts"
        oven_path = root / "images" / "oven.png"
        self.oven_img = None
        if oven_path.exists():
            base = pygame.image.load(str(oven_path)).convert_alpha()
            self.oven_img = pygame.transform.smoothscale(base, (300, 170))
        name_to_file = {
            "mini_red_velvet": "red_velvet.png",
            "raspberry_matcha_roll": "matcha_roll.png",
            "strawberry_cream_slice": "strawberry_cream.png",
            "chocolate_almond_drip_cake": "chocolate_drip.png",
            "chocolate_orange_roll": "orange_roll.png",
        }
        self.icons: Dict[str, pygame.Surface] = {}
        for name, fn in name_to_file.items():
            p = img_dir / fn
            if p.exists():
                img = pygame.image.load(str(p)).convert_alpha()
                self.icons[name] = pygame.transform.smoothscale(img, (64, 64))
            else:
                surf = pygame.Surface((64, 64))
                surf.fill(self.COLORS["cream"])
                self.icons[name] = surf

        # Precompute normalization for progress
        self.max_bake_ticks = max(
            int(ITEM_BAKE_SECONDS[i] // 10) for i in range(len(ITEM_NAMES))
        )

        # Layout constants (keep rows evenly spaced vertically)
        self.ROW_SPACING = 90  # aim for 80–100px between rows
        self.LAYOUT = {
            "inventory_y": 90,
            "ovens_y": 230,  # leaves ~ROW_SPACING below inventory boxes
            "queue_y": 450,  # moved slightly down for more space under ovens
            "action_y": 520,  # dedicated action bar, no overlapping icons
        }

    def draw_header(self, env) -> None:
        s = env.unwrapped
        t = s.t
        mm = int((t * 10) // 60)
        ss = int((t * 10) % 60)
        self._rounded_rect((20, 20, 860, 46), self.COLORS["cream"], radius=14)
        title = self.title.render("Bellman's Bakery", True, self.COLORS["text"])
        self.screen.blit(title, (30, 26))
        header = self.font.render(
            f"Time {mm:02d}:{ss:02d}   Profit ${s.profit:.2f}   Mult x{s.daily_price_multiplier:.2f}",
            True,
            self.COLORS["text"],
        )
        self.screen.blit(header, (340, 28))

    def draw_inventory(self, env) -> None:
        s = env.unwrapped
        x = 20
        y = self.LAYOUT["inventory_y"]
        # Section label
        inv_lbl = self.small.render("Inventory", True, self.COLORS["text"])
        self.screen.blit(inv_lbl, (20, y - 24))
        for i, name in enumerate(ITEM_NAMES):
            self._rounded_rect((x, y, 168, 88), self.COLORS["lav"], radius=14)
            self.screen.blit(self.icons[name], (x + 10, y + 12))
            count = int(s.inventory[i])
            price = float(s.prices_today[i]) if hasattr(s, "prices_today") else 0.0
            txt = self.small.render(
                f"x{count}  ${price:.2f}", True, self.COLORS["text"]
            )
            self.screen.blit(txt, (x + 82, y + 32))
            x += 176
            if (i + 1) % 5 == 0:
                x = 20
                y += 96

    def draw_ovens(self, env) -> None:
        s = env.unwrapped
        oy = self.LAYOUT["ovens_y"]
        # Center two ovens horizontally with a fixed gap
        oven_w, oven_h = 300, 170
        gap = 120
        total_w = 2 * oven_w + gap
        ox = max(20, (self.screen.get_width() - total_w) // 2)

        for idx, oven in enumerate(s.ovens):
            if self.oven_img is not None:
                self.screen.blit(self.oven_img, (ox, oy))
                # Label above each oven (centered)
                idx_surf = self.small.render(
                    f"Oven {idx + 1}", True, self.COLORS["text"]
                )
                self.screen.blit(
                    idx_surf, (ox + oven_w // 2 - idx_surf.get_width() // 2, oy - 18)
                )
                # Progress bar below the oven
                bar_x, bar_y, bar_w, bar_h = ox + 12, oy + oven_h + 10, 276, 12
            else:
                # Fallback simple oven shape
                self._rounded_rect(
                    (ox, oy, oven_w, oven_h), self.COLORS["cream"], radius=18
                )
                # Dark inner "window"
                pygame.draw.rect(
                    self.screen,
                    (70, 70, 70),
                    (ox + 20, oy + 36, oven_w - 40, 90),
                    border_radius=12,
                )
                idx_surf = self.small.render(
                    f"Oven {idx + 1}", True, self.COLORS["text"]
                )
                self.screen.blit(
                    idx_surf, (ox + oven_w // 2 - idx_surf.get_width() // 2, oy - 18)
                )
                # Progress bar below the oven
                bar_x, bar_y, bar_w, bar_h = ox + 12, oy + oven_h + 10, oven_w - 24, 12

            if oven:
                max_ticks = max(load[2] for load in oven)
                frac = max(
                    0.0, min(1.0, 1.0 - (max_ticks / max(1, self.max_bake_ticks)))
                )
            else:
                frac = 0.0
            # Progress bar
            pygame.draw.rect(
                self.screen,
                (210, 235, 215),
                (bar_x, bar_y, int(bar_w * frac), bar_h),
                border_radius=8,
            )
            # Larger thumbnails, centered over the oven window area
            thumb_size = 50
            step = 38
            ty = oy + 82
            n = len(oven)
            if n > 0:
                row_w = n * thumb_size + (n - 1) * (step - thumb_size)
                tx = ox + oven_w // 2 - row_w // 2
                for item_idx, _size, _ticks_remaining in oven:
                    name = ITEM_NAMES[item_idx]
                    thumb = pygame.transform.smoothscale(
                        self.icons[name], (thumb_size, thumb_size)
                    )
                    self.screen.blit(thumb, (tx, ty))
                    tx += step
            ox += oven_w + gap  # move to next oven

    def draw_queue(self, env) -> None:
        s = env.unwrapped
        # Queue row (separate from current action bar)
        qy = self.LAYOUT["queue_y"]
        q_label = self.small.render("Queue:", True, self.COLORS["text"])
        self.screen.blit(q_label, (20, qy - 24))
        # Move avatars down and to the right to avoid overlapping the label
        x = 100
        y = qy + 14
        for i, _cust in enumerate(s.queue[:12]):
            pygame.draw.circle(self.screen, self.COLORS["queue"], (x, y), 16)
            pygame.draw.circle(
                self.screen, self.COLORS["queue_border"], (x, y), 16, width=3
            )
            x += 40

    def draw_action_bar(self, env) -> None:
        s = env.unwrapped
        ay = self.LAYOUT["action_y"]
        # Dedicated current action bar; no customer icons drawn here
        self._rounded_rect((20, ay, 860, 64), self.COLORS["cream"], radius=18)
        # Format action text: replace underscores with spaces and capitalize
        raw = getattr(s, "last_action_str", "idle")
        nice = raw.replace("_", " ").strip()
        if len(nice) > 0:
            nice = nice[0].upper() + nice[1:]
        lbl = self.small.render(f"Current action: {nice}", True, self.COLORS["text"])
        self.screen.blit(lbl, (32, ay + 20))

    def render(self, env) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
        self.screen.fill(self.COLORS["bg"])
        self.draw_header(env)
        self.draw_inventory(env)
        self.draw_ovens(env)
        self.draw_queue(env)
        self.draw_action_bar(env)
        pygame.display.flip()
        self.clock.tick(30)

    def _rounded_rect(self, rect, color, radius=8):
        pygame.draw.rect(self.screen, color, rect, border_radius=radius)

import json
import math
import random
import sys
from pathlib import Path

import pygame


WIDTH, HEIGHT = 960, 540
GROUND_Y = 424
FPS = 60
RECORD_FILE = Path("cat_dash_record.json")

SKY_TOP = (19, 25, 55)
SKY_BOTTOM = (83, 91, 137)
INK = (35, 38, 67)
CREAM = (255, 242, 211)
CORAL = (255, 132, 119)
MINT = (142, 224, 194)
GOLD = (255, 205, 116)


def draw_text(surface, text, font, color, position, anchor="center"):
    image = font.render(str(text), True, color)
    rect = image.get_rect()
    setattr(rect, anchor, position)
    surface.blit(image, rect)


def load_record():
    try:
        data = json.loads(RECORD_FILE.read_text(encoding="utf-8"))
        return max(0, int(data.get("best", 0)))
    except FileNotFoundError:
        return 0
    except (json.JSONDecodeError, TypeError, ValueError):
        return 0


def save_record(record):
    try:
        RECORD_FILE.write_text(
            json.dumps({"best": int(record)}, indent=2), encoding="utf-8"
        )
    except OSError as error:
        print(f"Could not save your local record: {error}", file=sys.stderr)


class Cat:
    WIDTH = 58
    HEIGHT = 62

    def __init__(self):
        self.x = 142
        self.y = float(GROUND_Y - self.HEIGHT)
        self.velocity_y = 0.0
        self.on_ground = True
        self.run_time = 0.0
        self.jump_time = 0.0

    @property
    def hitbox(self):
        return pygame.Rect(round(self.x + 7), round(self.y + 8), 44, 49)

    def jump(self):
        if self.on_ground:
            self.velocity_y = -785
            self.on_ground = False
            self.jump_time = 0.0

    def update(self, dt):
        self.run_time += dt * (10 if self.on_ground else 3)
        if not self.on_ground:
            self.jump_time += dt
            self.velocity_y += 2050 * dt
            self.y += self.velocity_y * dt
            if self.y >= GROUND_Y - self.HEIGHT:
                self.y = float(GROUND_Y - self.HEIGHT)
                self.velocity_y = 0
                self.on_ground = True

    def draw(self, surface):
        x, y = round(self.x), round(self.y)
        bounce = math.sin(self.run_time) * 2 if self.on_ground else 0
        cy = y + round(bounce)
        # Curled tail and a soft shadow make the simple vector cat feel lively.
        pygame.draw.ellipse(surface, (28, 33, 65), (x + 2, GROUND_Y - 7, 57, 13))
        tail_points = [
            (x + 15, cy + 40),
            (x + 5, cy + 32),
            (x + 2, cy + 22),
            (x + 7, cy + 18),
            (x + 13, cy + 21),
        ]
        pygame.draw.lines(surface, (232, 153, 111), False, tail_points, 8)
        pygame.draw.circle(surface, (232, 153, 111), tail_points[-1], 4)

        body = pygame.Rect(x + 10, cy + 25, 42, 31)
        pygame.draw.ellipse(surface, (243, 174, 123), body)
        pygame.draw.ellipse(surface, (255, 218, 174), (x + 20, cy + 39, 23, 16))

        leg_swing = math.sin(self.run_time) * 5 if self.on_ground else 0
        for leg_x, swing in ((x + 18, leg_swing), (x + 39, -leg_swing)):
            pygame.draw.line(
                surface,
                (211, 130, 103),
                (leg_x, cy + 48),
                (leg_x - swing, cy + 59),
                7,
            )
            pygame.draw.ellipse(
                surface,
                (255, 218, 174),
                (round(leg_x - swing - 5), cy + 54, 13, 7),
            )

        # Ears sit behind the head; pink inner triangles add a clear cat silhouette.
        pygame.draw.polygon(
            surface,
            (243, 174, 123),
            [(x + 13, cy + 25), (x + 14, cy + 2), (x + 29, cy + 16)],
        )
        pygame.draw.polygon(
            surface,
            (243, 174, 123),
            [(x + 32, cy + 16), (x + 50, cy + 1), (x + 53, cy + 27)],
        )
        pygame.draw.polygon(
            surface,
            (255, 139, 151),
            [(x + 18, cy + 18), (x + 18, cy + 8), (x + 25, cy + 16)],
        )
        pygame.draw.polygon(
            surface,
            (255, 139, 151),
            [(x + 39, cy + 15), (x + 48, cy + 7), (x + 49, cy + 19)],
        )

        head = pygame.Rect(x + 12, cy + 12, 43, 37)
        pygame.draw.ellipse(surface, (255, 205, 155), head)
        pygame.draw.ellipse(surface, (255, 224, 190), (x + 18, cy + 22, 32, 24))
        pygame.draw.circle(surface, (51, 53, 78), (x + 28, cy + 29), 2)
        pygame.draw.circle(surface, (51, 53, 78), (x + 43, cy + 29), 2)
        pygame.draw.polygon(
            surface, (227, 111, 130), [(x + 33, cy + 35), (x + 38, cy + 35), (x + 35, cy + 38)]
        )
        pygame.draw.line(surface, (119, 89, 91), (x + 35, cy + 38), (x + 35, cy + 40), 1)
        pygame.draw.arc(surface, (119, 89, 91), (x + 29, cy + 37, 7, 6), 0, math.pi / 2, 1)
        pygame.draw.arc(surface, (119, 89, 91), (x + 35, cy + 37, 7, 6), math.pi / 2, math.pi, 1)
        for whisker_y in (cy + 34, cy + 38):
            pygame.draw.line(surface, (167, 127, 112), (x + 24, whisker_y), (x + 9, whisker_y - 3), 1)
            pygame.draw.line(surface, (167, 127, 112), (x + 46, whisker_y), (x + 59, whisker_y - 3), 1)


class Obstacle:
    def __init__(self, x, kind):
        self.x = float(x)
        self.kind = kind
        self.phase = random.random() * math.tau
        if kind == "plant":
            self.width, self.height = 43, random.randint(43, 62)
        else:
            self.width, self.height = 54, random.randint(48, 60)

    @property
    def hitbox(self):
        inset = 7
        return pygame.Rect(
            round(self.x + inset),
            GROUND_Y - self.height + 5,
            self.width - inset * 2,
            self.height - 7,
        )

    def update(self, dt, speed):
        self.x -= speed * dt
        self.phase += dt * 5

    def draw(self, surface):
        x = round(self.x)
        top = GROUND_Y - self.height
        pygame.draw.ellipse(surface, (28, 33, 65), (x - 3, GROUND_Y - 6, self.width + 8, 12))
        if self.kind == "plant":
            green = (91, 194, 157)
            pygame.draw.rect(surface, green, (x + 17, top + 13, 11, self.height - 13), border_radius=5)
            pygame.draw.ellipse(surface, (109, 211, 169), (x + 2, top + 22, 23, 18))
            pygame.draw.ellipse(surface, (109, 211, 169), (x + 22, top + 8, 19, 16))
            pygame.draw.circle(surface, (238, 250, 208), (x + 11, top + 27), 2)
            pygame.draw.circle(surface, (238, 250, 208), (x + 32, top + 15), 2)
        else:
            bob = round(math.sin(self.phase) * 2)
            pygame.draw.rect(
                surface, (164, 129, 199), (x + 3, top + 14 + bob, 48, self.height - 14), border_radius=9
            )
            pygame.draw.rect(
                surface, (196, 160, 224), (x + 8, top + 18 + bob, 38, 10), border_radius=5
            )
            pygame.draw.line(
                surface,
                (226, 211, 236),
                (x + 14, top + 36 + bob),
                (x + 40, top + 36 + bob),
                3,
            )


class CatDash:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Cat Dash — a tiny moonlit runner")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont("arial", 18, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 26, bold=True)
        self.font_large = pygame.font.SysFont("arial", 62, bold=True)
        self.font_score = pygame.font.SysFont("arial", 25, bold=True)
        self.best = load_record()
        self.state = "title"
        self.cat = Cat()
        self.obstacles = []
        self.distance = 0.0
        self.elapsed = 0.0
        self.spawn_timer = 0.8
        self.ground_offset = 0.0
        self.far_offset = 0.0
        self.near_offset = 0.0
        self.stars = [
            (random.randrange(WIDTH), random.randrange(30, 260), random.choice((1, 1, 2)))
            for _ in range(55)
        ]
        self.sky = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            amount = y / HEIGHT
            color = tuple(
                round(SKY_TOP[index] * (1 - amount) + SKY_BOTTOM[index] * amount)
                for index in range(3)
            )
            pygame.draw.line(self.sky, color, (0, y), (WIDTH, y))
        self.clouds = [
            [random.randrange(WIDTH), random.randrange(105, 290), random.uniform(0.2, 0.5)]
            for _ in range(7)
        ]

    @property
    def score(self):
        return int(self.distance / 10)

    @property
    def speed(self):
        return min(730.0, 360.0 + self.distance * 0.045)

    def start_game(self):
        self.cat = Cat()
        self.obstacles = []
        self.distance = 0.0
        self.elapsed = 0.0
        self.spawn_timer = 1.15
        self.state = "playing"

    def finish_game(self):
        self.state = "game_over"
        if self.score > self.best:
            self.best = self.score
            save_record(self.best)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if self.state == "playing":
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    self.cat.jump()
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_UP, pygame.K_w):
                self.start_game()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == "playing":
                self.cat.jump()
            else:
                self.start_game()
        return True

    def update(self, dt):
        world_speed = self.speed if self.state == "playing" else 115
        self.ground_offset = (self.ground_offset + world_speed * dt) % 56
        self.far_offset = (self.far_offset + world_speed * 0.12 * dt) % WIDTH
        self.near_offset = (self.near_offset + world_speed * 0.25 * dt) % WIDTH
        for cloud in self.clouds:
            cloud[0] -= cloud[2] * world_speed * dt
            if cloud[0] < -100:
                cloud[0] = WIDTH + random.randrange(40, 260)
                cloud[1] = random.randrange(105, 290)
        if self.state != "playing":
            return

        self.elapsed += dt
        self.distance += self.speed * dt
        self.cat.update(dt)
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.obstacles.append(Obstacle(WIDTH + 25, random.choice(("plant", "plant", "parcel"))))
            self.spawn_timer = random.uniform(1.05, 1.7) * max(0.68, 360 / self.speed)

        for obstacle in self.obstacles:
            obstacle.update(dt, self.speed)
            if self.cat.hitbox.colliderect(obstacle.hitbox):
                self.finish_game()
                break
        self.obstacles = [item for item in self.obstacles if item.x + item.width > -10]

    def draw_background(self):
        self.screen.blit(self.sky, (0, 0))

        for x, y, radius in self.stars:
            twinkle = 0.65 + 0.35 * math.sin(pygame.time.get_ticks() / 700 + x)
            color = tuple(round(channel * twinkle) for channel in (218, 224, 255))
            pygame.draw.circle(self.screen, color, (x, y), radius)

        pygame.draw.circle(self.screen, (255, 224, 170), (758, 112), 42)
        pygame.draw.circle(self.screen, (255, 235, 195), (746, 100), 37)
        pygame.draw.circle(self.screen, SKY_TOP, (731, 91), 33)

        for x, y, _ in self.clouds:
            cx, cy = round(x), round(y)
            cloud_color = (116, 128, 174)
            pygame.draw.ellipse(self.screen, cloud_color, (cx, cy + 8, 84, 20))
            pygame.draw.circle(self.screen, cloud_color, (cx + 22, cy + 13), 14)
            pygame.draw.circle(self.screen, cloud_color, (cx + 43, cy + 5), 19)
            pygame.draw.circle(self.screen, cloud_color, (cx + 62, cy + 13), 13)

        for layer_offset, base_y, color, height in (
            (self.far_offset, 352, (53, 67, 111), 65),
            (self.near_offset, 388, (45, 59, 96), 43),
        ):
            for index in range(-1, 3):
                x = index * WIDTH - round(layer_offset)
                pygame.draw.polygon(
                    self.screen,
                    color,
                    [
                        (x, base_y),
                        (x + 125, base_y - height),
                        (x + 290, base_y - height // 3),
                        (x + 455, base_y - height),
                        (x + 650, base_y - height // 2),
                        (x + WIDTH, base_y),
                    ],
                )

        pygame.draw.rect(self.screen, (46, 48, 78), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.line(self.screen, MINT, (0, GROUND_Y), (WIDTH, GROUND_Y), 4)
        for index in range(-1, WIDTH // 56 + 2):
            x = index * 56 - round(self.ground_offset)
            pygame.draw.line(self.screen, (80, 83, 116), (x, GROUND_Y + 32), (x + 22, GROUND_Y + 32), 3)
            pygame.draw.circle(self.screen, (73, 78, 111), (x + 37, GROUND_Y + 72), 2)

    def draw_hud(self):
        pygame.draw.rect(self.screen, (33, 38, 72), (24, 22, 188, 58), border_radius=18)
        pygame.draw.rect(self.screen, (68, 75, 111), (24, 22, 188, 58), width=2, border_radius=18)
        draw_text(self.screen, "DISTANCE", self.font_small, (183, 194, 224), (42, 33), "topleft")
        draw_text(self.screen, f"{self.score:05d}", self.font_score, CREAM, (42, 50), "topleft")
        draw_text(self.screen, f"BEST  {self.best:05d}", self.font_small, (211, 218, 240), (WIDTH - 30, 34), "topright")
        if self.state == "playing" and self.elapsed < 4:
            draw_text(
                self.screen,
                "SPACE / ↑ / CLICK TO JUMP",
                self.font_small,
                (224, 230, 250),
                (WIDTH // 2, 40),
            )

    def draw_title(self):
        panel = pygame.Rect(208, 93, 544, 274)
        pygame.draw.rect(self.screen, (30, 35, 69), panel, border_radius=28)
        pygame.draw.rect(self.screen, (105, 116, 160), panel, width=2, border_radius=28)
        draw_text(self.screen, "CAT DASH", self.font_large, CREAM, (WIDTH // 2, 151))
        draw_text(self.screen, "A little moonlit sprint", self.font_medium, MINT, (WIDTH // 2, 205))
        draw_text(
            self.screen,
            "Dodge the garden things. Keep your paws moving.",
            self.font_small,
            (213, 221, 242),
            (WIDTH // 2, 250),
        )
        draw_text(self.screen, "PRESS SPACE TO PLAY", self.font_medium, GOLD, (WIDTH // 2, 307))
        draw_text(
            self.screen,
            "SPACE / ↑ / W / CLICK  ·  ESC TO QUIT",
            self.font_small,
            (184, 197, 226),
            (WIDTH // 2, 342),
        )

    def draw_game_over(self):
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((17, 20, 42, 150))
        self.screen.blit(veil, (0, 0))
        panel = pygame.Rect(286, 125, 388, 252)
        pygame.draw.rect(self.screen, (34, 39, 73), panel, border_radius=26)
        pygame.draw.rect(self.screen, (255, 132, 119), panel, width=2, border_radius=26)
        draw_text(self.screen, "PAWS DOWN!", self.font_large, CREAM, (WIDTH // 2, 185))
        draw_text(self.screen, f"DISTANCE   {self.score:05d}", self.font_medium, MINT, (WIDTH // 2, 245))
        draw_text(self.screen, f"BEST   {self.best:05d}", self.font_small, (207, 218, 241), (WIDTH // 2, 282))
        draw_text(self.screen, "PRESS SPACE TO RUN AGAIN", self.font_medium, GOLD, (WIDTH // 2, 333))

    def draw(self):
        self.draw_background()
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        self.cat.draw(self.screen)
        self.draw_hud()
        if self.state == "title":
            self.draw_title()
        elif self.state == "game_over":
            self.draw_game_over()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000, 1 / 30)
            for event in pygame.event.get():
                running = self.handle_event(event) and running
            self.update(dt)
            self.draw()
        pygame.quit()


def main():
    CatDash().run()


if __name__ == "__main__":
    main()

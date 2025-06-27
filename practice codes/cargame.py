"""
Advanced Car Racing Simulator Game using Pygame
- 2D top-down perspective racing on a curved track
- Smooth car physics: acceleration, braking, turning, friction
- Lap timing system
- High graphical quality for 2D pygame standards
- Keyboard controls: arrows or WASD

Ensure pygame is installed: pip install pygame
Run the game: python car_racing_simulator.py
"""

import pygame
import math
import time
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600  # Window size
FPS = 60

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARKGRAY = (50, 50, 50)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (70, 130, 180)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Car Racing Simulator")

# Load font
font = pygame.font.SysFont("Arial", 20, bold=True)
big_font = pygame.font.SysFont("Arial", 40, bold=True)

# Clock
clock = pygame.time.Clock()

# Helper Functions
def blit_rotate_center(surf, image, top_left, angle):
    rotated_image = pygame.transform.rotozoom(image, -angle, 1)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    surf.blit(rotated_image, new_rect.topleft)
    return new_rect

# Car class
class Car:
    def __init__(self, x, y):
        # Create a car surface programmatically
        self.original_image = pygame.Surface((64, 32), pygame.SRCALPHA)
        pygame.draw.polygon(self.original_image, BLUE, [(0, 0), (64, 8), (64, 24), (0, 32)])
        pygame.draw.rect(self.original_image, WHITE, (0, 8, 64, 16), 2)

        # Car properties
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.max_speed = 7
        self.acceleration = 0.15
        self.deceleration = 0.3
        self.friction = 0.05
        self.turn_speed = 4
        self.length = 64
        self.width = 32

    def update(self, keys):
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed += self.acceleration
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed -= self.deceleration
        else:
            if self.speed > 0:
                self.speed -= self.friction
            elif self.speed < 0:
                self.speed += self.friction

        self.speed = max(min(self.speed, self.max_speed), -self.max_speed / 2)

        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.speed != 0:
            turn_direction = 1 if self.speed > 0 else -1
            self.angle += self.turn_speed * turn_direction

        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.speed != 0:
            turn_direction = -1 if self.speed > 0 else 1
            self.angle += self.turn_speed * turn_direction

        rad = math.radians(self.angle)
        self.x += -math.sin(rad) * self.speed
        self.y += -math.cos(rad) * self.speed

        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, min(HEIGHT, self.y))

    def draw(self, surface):
        blit_rotate_center(surface, self.original_image, (self.x - self.length // 2, self.y - self.width // 2), self.angle)

# Track class
class Track:
    def __init__(self):
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        self.surface.fill(GREEN)
        self.track_color = GRAY
        self.road_width = 180

        self.center_path = [
            (WIDTH // 2, HEIGHT // 4), (WIDTH // 2 + 160, HEIGHT // 2 - 100),
            (WIDTH // 2 + 180, HEIGHT // 2 + 50), (WIDTH // 2 + 140, HEIGHT // 2 + 150),
            (WIDTH // 2, HEIGHT // 2 + 210), (WIDTH // 2 - 130, HEIGHT // 2 + 180),
            (WIDTH // 2 - 160, HEIGHT // 2 + 100), (WIDTH // 2 - 110, HEIGHT // 2 - 30)
        ]
        self.center_path.append(self.center_path[0])

        self._draw_track()
        self.finish_line = pygame.Rect(WIDTH // 2 - 5, HEIGHT // 4 - self.road_width // 2, 10, self.road_width)
        self.finish_line_color = RED

    def _draw_track(self):
        self.surface.fill(GREEN)
        points_left = []
        points_right = []

        for i in range(len(self.center_path) - 1):
            cx, cy = self.center_path[i]
            nx, ny = self.center_path[i + 1]
            dx, dy = nx - cx, ny - cy
            length = math.hypot(dx, dy) or 1
            dx /= length
            dy /= length
            plx = -dy * (self.road_width / 2)
            ply = dx * (self.road_width / 2)

            points_left.append((cx + plx, cy + ply))
            points_right.append((cx - plx, cy - ply))

        cx, cy = self.center_path[-1]
        nx, ny = self.center_path[0]
        dx, dy = nx - cx, ny - cy
        length = math.hypot(dx, dy) or 1
        dx /= length
        dy /= length
        plx = -dy * (self.road_width / 2)
        ply = dx * (self.road_width / 2)
        points_left.append((cx + plx, cy + ply))
        points_right.append((cx - plx, cy - ply))

        track_poly = points_left + points_right[::-1]
        pygame.draw.polygon(self.surface, self.track_color, track_poly)

        for i in range(len(self.center_path) - 1):
            start = self.center_path[i]
            end = self.center_path[i + 1]
            self._draw_dashed_line(self.surface, WHITE, start, end, 15, 10, 3)

        pygame.draw.rect(self.surface, self.finish_line_color, self.finish_line)

    def _draw_dashed_line(self, surface, color, start_pos, end_pos, dash_length=10, space_length=5, width=2):
        x1, y1 = start_pos
        x2, y2 = end_pos
        length = math.hypot(x2 - x1, y2 - y1)
        dash_count = int(length / (dash_length + space_length))
        dash_dx = (x2 - x1) / length * dash_length
        dash_dy = (y2 - y1) / length * dash_length
        space_dx = (x2 - x1) / length * space_length
        space_dy = (y2 - y1) / length * space_length

        for i in range(dash_count):
            start_x = x1 + (dash_dx + space_dx) * i
            start_y = y1 + (dash_dy + space_dy) * i
            end_x = start_x + dash_dx
            end_y = start_y + dash_dy
            pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), width)

    def draw(self, surface):
        surface.blit(self.surface, (0, 0))

    def is_on_track(self, x, y):
        try:
            color = self.surface.get_at((int(x), int(y)))[:3]
            def color_close(c1, c2, tol=30):
                return all(abs(c1[i] - c2[i]) < tol for i in range(3))
            return color_close(color, self.track_color) or color_close(color, WHITE)
        except IndexError:
            return False

    def check_finish_line_cross(self, rect, prev_rect):
        return self.finish_line.colliderect(rect) and not self.finish_line.colliderect(prev_rect)

# Game class
class Game:
    def __init__(self):
        self.track = Track()
        start_x, start_y = self.track.center_path[0]
        self.car = Car(start_x, start_y + 50)
        self.start_time = None
        self.lap_time = 0
        self.best_lap_time = None
        self.laps_completed = 0
        self.prev_car_rect = pygame.Rect(self.car.x, self.car.y, self.car.length, self.car.width)
        self.game_over = False
        self.sound_accel = None
        self.sound_brake = None

    def display_text(self, surface, text, x, y, color=WHITE, font_obj=None):
        font_obj = font_obj or font
        textobj = font_obj.render(text, True, color)
        surface.blit(textobj, (x, y))

    def update(self):
        keys = pygame.key.get_pressed()
        self.car.update(keys)

        car_rect = pygame.Rect(self.car.x - self.car.length // 2, self.car.y - self.car.width // 2, self.car.length, self.car.width)

        if not self.track.is_on_track(self.car.x, self.car.y):
            self.car.speed *= 0.95

        if self.track.check_finish_line_cross(car_rect, self.prev_car_rect) and self.car.speed > 0:
            now = time.time()
            if self.start_time is None:
                self.start_time = now
            else:
                lap = now - self.start_time
                self.best_lap_time = min(self.best_lap_time or lap, lap)
                self.lap_time = lap
                self.start_time = now
                self.laps_completed += 1

        self.prev_car_rect = car_rect.copy()

    def draw(self, surface):
        surface.fill(GREEN)
        self.track.draw(surface)
        self.car.draw(surface)

        self.display_text(surface, f"Speed: {int(self.car.speed * 20)} km/h", 10, 10)
        self.display_text(surface, f"Laps Completed: {self.laps_completed}", 10, 40)

        if self.lap_time > 0:
            self.display_text(surface, f"Last Lap Time: {self.lap_time:.2f} s", 10, 70)
        if self.best_lap_time:
            self.display_text(surface, f"Best Lap Time: {self.best_lap_time:.2f} s", 10, 100)

        self.display_text(surface, "Controls: Arrow Keys / WASD to drive | ESC to quit", 10, HEIGHT - 30, YELLOW)

    def run(self):
        running = True
        while running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False

            self.update()
            self.draw(screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()

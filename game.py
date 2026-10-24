from pathlib import Path

import pygame
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

GAME_DURATION_SECONDS = 30
DIFFICULTY_OBSTACLE_COUNTS = {
    "easy": 3,
    "normal": 4,
    "hard": 5,
    "veryhard": 10,
}

icon_dir = Path(__file__).resolve().parent / "icon"
target_types = [
    (pygame.image.load(str(icon_dir / "icons8-ahiru.png")), 5, 1),
    (pygame.image.load(str(icon_dir / "icons8-キツツキ-48.png")), 10, 2),
    (pygame.image.load(str(icon_dir / "icons8-flamingo-48.png")), 30, 3),
    (pygame.image.load(str(icon_dir / "icons8-ハチドリ-48.png")), 50, 5),
    (pygame.image.load(str(icon_dir / "icons8-cute-hamster-48.png")), 60, 7),
    (pygame.image.load(str(icon_dir / "icons8-owl-48.png")), 70, 9),
    (pygame.image.load(str(icon_dir / "icons8-phoenix-48.png")), 100, 12),
]
obstacle_dir = icon_dir / "Obstacle"
obstacle_images = [
    pygame.image.load(str(obstacle_dir / filename))
    for filename in (
        "icons8-雲-100.png",
        "icons8-建物-100.png",
        "icons8-森-100.png",
        "icons8-湖-96.png",
        "icons8-鉄道車-96.png",
    )
]
obstacles = []
scope = pygame.image.load(str(icon_dir / "icons8-scope.png"))
score_font = pygame.font.Font(None, 36)
count_font = pygame.font.Font(None, 26)
title_font = pygame.font.Font(None, 64)
message_font = pygame.font.Font(None, 32)
button_font = pygame.font.Font(None, 36)
difficulty_buttons = {
    "easy": pygame.Rect(120, 330, 250, 65),
    "normal": pygame.Rect(430, 330, 250, 65),
    "hard": pygame.Rect(120, 420, 250, 65),
    "veryhard": pygame.Rect(430, 420, 250, 65),
}
restart_difficulty_buttons = {
    "easy": pygame.Rect(10, 500, 185, 60),
    "normal": pygame.Rect(205, 500, 185, 60),
    "hard": pygame.Rect(400, 500, 185, 60),
    "veryhard": pygame.Rect(595, 500, 195, 60),
}


def create_target():
    type_index = random.randrange(len(target_types))
    image, points, speed = target_types[type_index]
    width = screen.get_width()
    height = screen.get_height()
    direction = random.choice(("left", "right", "top", "bottom"))
    if direction == "left":
        x = -image.get_width()
        y = random.randint(100, height - image.get_height())
        dx, dy = speed, 0
    elif direction == "right":
        x = width
        y = random.randint(100, height - image.get_height())
        dx, dy = -speed, 0
    elif direction == "top":
        x = random.randint(0, width - image.get_width())
        y = -image.get_height()
        dx, dy = 0, speed
    else:
        x = random.randint(0, width - image.get_width())
        y = height
        dx, dy = 0, -speed

    return {
        "image": image,
        "points": points,
        "speed": speed,
        "dx": dx,
        "dy": dy,
        "type_index": type_index,
        "x": x,
        "y": y,
    }


def create_wave():
    return [create_target() for _ in range(random.randint(2, 5))]


def create_obstacles(count):
    grid_positions = [
        (x, y)
        for y in range(100, screen.get_height(), 100)
        for x in range(0, screen.get_width(), 100)
    ]
    positions = random.sample(grid_positions, count)
    selected_obstacles = []
    for position in positions:
        image = random.choice(obstacle_images)
        selected_obstacles.append((image, image.get_rect(topleft=position)))
    return selected_obstacles


def target_rect(target):
    return target["image"].get_rect(topleft=(target["x"], target["y"]))


def is_obstructed(target):
    rect = target_rect(target)
    return any(rect.colliderect(obstacle_rect) for _, obstacle_rect in obstacles)


def start_game(difficulty):
    global active_targets, obstacles, score, click_counts
    global game_started_at, game_state, selected_difficulty
    global finish_reason
    selected_difficulty = difficulty
    obstacles = create_obstacles(DIFFICULTY_OBSTACLE_COUNTS[difficulty])
    active_targets = create_wave()
    score = 0
    click_counts = [0] * len(target_types)
    game_started_at = pygame.time.get_ticks()
    finish_reason = None
    game_state = "playing"


game_state = "start"
selected_difficulty = "easy"
active_targets = []
score = 0
click_counts = [0] * len(target_types)
game_started_at = 0
finish_reason = None

running = True
while running:
    screen.fill((135, 206, 235))  # 空色

    if (
        game_state == "playing"
        and pygame.time.get_ticks() - game_started_at
        >= GAME_DURATION_SECONDS * 1000
    ):
        finish_reason = "time_up"
        game_state = "finished"

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if game_state == "playing":
                finish_reason = "interrupted"
                game_state = "finished"
            else:
                running = False
        elif game_state == "start" and event.type == pygame.MOUSEBUTTONDOWN:
            for difficulty, button_rect in difficulty_buttons.items():
                if button_rect.collidepoint(event.pos):
                    start_game(difficulty)
                    break
        elif game_state == "finished" and event.type == pygame.MOUSEBUTTONDOWN:
            for difficulty, button_rect in restart_difficulty_buttons.items():
                if button_rect.collidepoint(event.pos):
                    start_game(difficulty)
                    break
        elif game_state == "playing" and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            scope_hitbox = pygame.Rect(mx - 50, my - 50, 100, 100)
            for index, target in enumerate(active_targets):
                if (
                    not is_obstructed(target)
                    and target_rect(target).colliderect(scope_hitbox)
                ):
                    score += target["points"]
                    click_counts[target["type_index"]] += 1
                    active_targets.pop(index)
                    break

    if game_state == "playing":
        elapsed_ms = pygame.time.get_ticks() - game_started_at
        for target in active_targets:
            target["x"] += target["dx"]
            target["y"] += target["dy"]
        active_targets = [
            target
            for target in active_targets
            if target_rect(target).colliderect(screen.get_rect())
        ]
        if not active_targets:
            active_targets = create_wave()

        for target in active_targets:
            if not is_obstructed(target):
                screen.blit(target["image"], (target["x"], target["y"]))
        for obstacle_image, obstacle_rect in obstacles:
            screen.blit(obstacle_image, obstacle_rect)

        remaining = GAME_DURATION_SECONDS - elapsed_ms // 1000
        score_text = score_font.render(f"Score: {score}", True, (0, 0, 0))
        time_text = score_font.render(f"Time: {remaining}", True, (0, 0, 0))
        difficulty_text = score_font.render(selected_difficulty, True, (0, 0, 0))
        screen.blit(score_text, (10, 8))
        screen.blit(time_text, (690, 8))
        screen.blit(difficulty_text, (350, 8))

        for index, (image, _, _) in enumerate(target_types):
            x = 10 + index * 112
            small_image = pygame.transform.scale(image, (32, 32))
            screen.blit(small_image, (x, 42))
            count_text = count_font.render(
                f"x {click_counts[index]}", True, (0, 0, 0)
            )
            screen.blit(count_text, (x + 38, 48))

        mx, my = pygame.mouse.get_pos()
        screen.blit(scope, (mx - 50, my - 50))

    if game_state == "start":
        title = title_font.render("Target Game", True, (0, 0, 0))
        instruction = message_font.render("Select difficulty", True, (0, 0, 0))
        screen.blit(title, title.get_rect(center=(400, 170)))
        screen.blit(instruction, instruction.get_rect(center=(400, 255)))
        for difficulty, button_rect in difficulty_buttons.items():
            button_color = (
                (60, 150, 80)
                if button_rect.collidepoint(pygame.mouse.get_pos())
                else (80, 170, 100)
            )
            pygame.draw.rect(screen, button_color, button_rect, border_radius=8)
            obstacle_count = DIFFICULTY_OBSTACLE_COUNTS[difficulty]
            label = button_font.render(
                f"{difficulty} ({obstacle_count})", True, (255, 255, 255)
            )
            screen.blit(label, label.get_rect(center=button_rect.center))
        duration = message_font.render("Time limit: 30 seconds", True, (0, 0, 0))
        screen.blit(duration, duration.get_rect(center=(400, 535)))
    elif game_state == "finished":
        title_text = "Game Ended" if finish_reason == "interrupted" else "Time's Up!"
        title = title_font.render(title_text, True, (0, 0, 0))
        final_score = message_font.render(f"Final Score: {score}", True, (0, 0, 0))
        screen.blit(title, title.get_rect(center=(400, 200)))
        screen.blit(final_score, final_score.get_rect(center=(400, 270)))
        for index, (image, _, _) in enumerate(target_types):
            x = 80 + (index % 4) * 170
            y = 340 + (index // 4) * 80
            small_image = pygame.transform.scale(image, (32, 32))
            screen.blit(small_image, (x, y))
            count_text = message_font.render(
                f"x {click_counts[index]}", True, (0, 0, 0)
            )
            screen.blit(count_text, (x + 42, y + 4))
        restart_prompt = count_font.render(
            "Select difficulty to restart", True, (0, 0, 0)
        )
        screen.blit(restart_prompt, restart_prompt.get_rect(center=(400, 475)))
        for difficulty, button_rect in restart_difficulty_buttons.items():
            button_color = (
                (60, 150, 80)
                if button_rect.collidepoint(pygame.mouse.get_pos())
                else (80, 170, 100)
            )
            pygame.draw.rect(screen, button_color, button_rect, border_radius=8)
            obstacle_count = DIFFICULTY_OBSTACLE_COUNTS[difficulty]
            label = button_font.render(
                f"{difficulty} ({obstacle_count})", True, (255, 255, 255)
            )
            screen.blit(label, label.get_rect(center=button_rect.center))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
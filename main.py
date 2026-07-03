import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 64)


class Player:
    def __init__(self):
        self.original_player = pygame.image.load('img/player.png')
        self.original_player = pygame.transform.scale(self.original_player, (100, 100))
        self.player = self.original_player
        self.rect = self.player.get_rect()
        self.rect.center = (400, 800)

        self.velocity_y = 0
        self.gravity = 0.5
        self.on_ground = False
        self.move_dir = 0
        self.facing_right = True

        self.speed = 5
        self.jump_power = -14

    def move(self, obstacles, enemies):
        self.rect.x += self.move_dir * self.speed
        self.check_collision_x(obstacles)

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        self.check_collision_y(obstacles)

        if self.move_dir > 0:
            self.facing_right = True
        elif self.move_dir < 0:
            self.facing_right = False

        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                self.respawn()

    def check_collision_x(self, obstacles):
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect) and obstacle.type != "финиш":
                if self.move_dir > 0:
                    self.rect.right = obstacle.rect.left
                elif self.move_dir < 0:
                    self.rect.left = obstacle.rect.right

    def check_collision_y(self, obstacles):
        self.on_ground = False
        on_special_platform = False
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if obstacle.type == "финиш":
                    continue

                if self.velocity_y > 0:
                    self.rect.bottom = obstacle.rect.top
                    self.velocity_y = 0
                    self.on_ground = True

                    on_special_platform = True
                    if obstacle.type == "ускорение":
                        self.speed = 9
                        self.jump_power = -17
                    else:
                        self.speed = 5
                        self.jump_power = -14

                elif self.velocity_y < 0:
                    self.rect.top = obstacle.rect.bottom
                    self.velocity_y = 0

        if not on_special_platform and self.on_ground == False:
            self.speed = 5

    def jump(self):
        if self.on_ground:
            self.velocity_y = self.jump_power

    def respawn(self):
        self.rect.center = (400, 800)
        self.velocity_y = 0

    def draw(self, camera_x, camera_y):
        if self.facing_right:
            self.player = self.original_player
        else:
            self.player = pygame.transform.flip(self.original_player, True, False)

        screen.blit(self.player, (self.rect.x - camera_x, self.rect.y - camera_y))


class Obstacle:
    def __init__(self, x, y, width, height, obs_type):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = obs_type

        if self.type == "ускорение":
            self.color = (0, 0, 255)
        elif self.type == "платформа":
            self.color = (150, 150, 150)
        elif self.type == "финиш":
            self.image = pygame.image.load('img/cup.png')
            self.image = pygame.transform.scale(self.image, (width, height))


class Enemy:
    def __init__(self, x, y, start_bound, end_bound):
        self.image = pygame.image.load('img/enemy.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.start_bound = start_bound
        self.end_bound = end_bound
        self.speed = 2

    def update(self):
        self.rect.x += self.speed
        if self.rect.right >= self.end_bound or self.rect.left <= self.start_bound:
            self.speed *= -1

    def draw(self, camera_x, camera_y):
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))


player = Player()

obstacles = [
    Obstacle(0, -1000, 40, 2000, "платформа"),
    Obstacle(760, -1000, 40, 2000, "платформа"),

    Obstacle(40, 860, 720, 40, "платформа"),

    Obstacle(100, 720, 250, 20, "платформа"),
    Obstacle(450, 580, 250, 20, "платформа"),
    Obstacle(100, 440, 250, 20, "ускорение"),
    Obstacle(450, 300, 250, 20, "платформа"),
    Obstacle(100, 160, 250, 20, "платформа"),
    Obstacle(450, 20, 250, 20, "ускорение"),
    Obstacle(100, -120, 250, 20, "платформа"),
    Obstacle(200, -260, 400, 20, "платформа"),

    Obstacle(365, -340, 70, 80, "финиш")
]

enemies = [
    Enemy(120, 670, 100, 350),
    Enemy(470, 530, 450, 700),
    Enemy(470, 250, 450, 700),
    Enemy(120, -170, 100, 350)
]

camera_x = 0
camera_y = 0
game_over = False

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                player.respawn()
                game_over = False

            if not game_over:
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_d or event.unicode in ('в', 'В'):
                    player.move_dir = 1
                if event.key == pygame.K_a or event.unicode in ('ф', 'Ф'):
                    player.move_dir = -1

        if event.type == pygame.KEYUP and not game_over:
            if event.key == pygame.K_d or event.unicode in ('в', 'В'):
                if player.move_dir == 1:
                    player.move_dir = 0
            if event.key == pygame.K_a or event.unicode in ('ф', 'Ф'):
                if player.move_dir == -1:
                    player.move_dir = 0

    if not game_over:
        player.move(obstacles, enemies)

        for enemy in enemies:
            enemy.update()

        camera_x += (player.rect.centerx - 400 - camera_x) * 0.1
        camera_y += (player.rect.centery - 300 - camera_y) * 0.1

        if player.rect.y > 950:
            player.respawn()

        for obstacle in obstacles:
            if obstacle.type == "финиш" and player.rect.colliderect(obstacle.rect):
                game_over = True

    screen.fill((0, 0, 0))

    for obstacle in obstacles:
        screen_x = obstacle.rect.x - camera_x
        screen_y = obstacle.rect.y - camera_y
        if obstacle.type == "финиш":
            screen.blit(obstacle.image, (screen_x, screen_y))
        else:
            pygame.draw.rect(screen, obstacle.color, (screen_x, screen_y, obstacle.rect.width, obstacle.rect.height))

    for enemy in enemies:
        enemy.draw(camera_x, camera_y)

    player.draw(camera_x, camera_y)

    if game_over:
        text_surface = font.render("Ты прошёл!", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(400, 260))
        screen.blit(text_surface, text_rect)

        hint_surface = pygame.font.SysFont("Arial", 24).render("Нажми R для перезапуска", True, (200, 200, 200))
        hint_rect = hint_surface.get_rect(center=(400, 340))
        screen.blit(hint_surface, hint_rect)

    pygame.display.flip()

pygame.quit()
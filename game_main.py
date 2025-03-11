import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY = (200, 200, 200)

# Game variables
lives = 20
money = 100
level = 1
towers = []
enemies = []
projectiles = []

# Tower types
TOWER_TYPES = {
    'Basic': {'cost': 50, 'damage': 2, 'range': 100, 'color': BLUE, 'fire_rate': 30},
    'Sniper': {'cost': 100, 'damage': 6, 'range': 200, 'color': GREEN, 'fire_rate': 60},
    'Cannon': {'cost': 150, 'damage': 10, 'range': 150, 'color': RED, 'fire_rate': 90}
}

# Track
TRACK = [
    (0, 300), (200, 300), (200, 100), (400, 100), 
    (400, 500), (600, 500), (600, 300), (800, 300)
]

class Tower:
    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.type = tower_type
        self.damage = TOWER_TYPES[tower_type]['damage']
        self.range = TOWER_TYPES[tower_type]['range']
        self.color = TOWER_TYPES[tower_type]['color']
        self.fire_rate = TOWER_TYPES[tower_type]['fire_rate']
        self.fire_cooldown = 0
        self.selected = False

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 20)
        if self.selected:
            pygame.draw.circle(screen, GREY, (self.x, self.y), self.range, 1)

    def fire(self, target):
        if self.fire_cooldown == 0:
            dx = target.x - self.x
            dy = target.y - self.y
            angle = math.atan2(dy, dx)
            projectiles.append(Projectile(self.x, self.y, angle, self.damage, self.color))
            self.fire_cooldown = self.fire_rate

    def update(self):
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

class Enemy:
    def __init__(self, enemy_type):
        self.x, self.y = TRACK[0]
        self.type = enemy_type
        if enemy_type == 'blue':
            self.health = 10
            self.value = 10
        elif enemy_type == 'green':
            self.health = 30
            self.value = 20
        else:  # red
            self.health = 150
            self.value = 50
        self.max_health = self.health
        self.speed = 1.5
        self.track_index = 0

    def move(self):
        target_x, target_y = TRACK[self.track_index + 1]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.speed:
            self.track_index += 1
            if self.track_index >= len(TRACK) - 1:
                return True
        else:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
        return False

    def draw(self):
        pygame.draw.circle(screen, self.type, (int(self.x), int(self.y)), 10)
        
        # Health bar
        pygame.draw.rect(screen, BLACK, (self.x - 15, self.y - 20, 30, 5))
        pygame.draw.rect(screen, GREEN, (self.x - 15, self.y - 20, 30 * (self.health / self.max_health), 5))

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            if self.type == 'red':
                return Enemy('green'), self.value
            elif self.type == 'green':
                return Enemy('blue'), self.value
            else:  # blue
                return None, self.value
        return self, 0

class Projectile:
    def __init__(self, x, y, angle, damage, color):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 15
        self.damage = damage
        self.color = color

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 5)

def draw_game():
    screen.fill(WHITE)
    
    # Draw track
    pygame.draw.lines(screen, GREEN, False, TRACK, 2)
    
    for tower in towers:
        tower.draw()
    for enemy in enemies:
        enemy.draw()
    for projectile in projectiles:
        projectile.draw()
    
    # Draw tower selection icons
    for i, tower_type in enumerate(TOWER_TYPES):
        pygame.draw.rect(screen, TOWER_TYPES[tower_type]['color'], (10 + i * 60, HEIGHT - 60, 50, 50))
        font = pygame.font.Font(None, 24)
        cost_text = font.render(str(TOWER_TYPES[tower_type]['cost']), True, BLACK)
        screen.blit(cost_text, (15 + i * 60, HEIGHT - 30))
    
    font = pygame.font.Font(None, 36)
    lives_text = font.render(f"Lives: {lives}", True, BLACK)
    money_text = font.render(f"Money: ${money}", True, BLACK)
    level_text = font.render(f"Level: {level}", True, BLACK)
    screen.blit(lives_text, (10, 10))
    screen.blit(money_text, (10, 50))
    screen.blit(level_text, (10, 90))
    pygame.display.flip()

def spawn_enemy(enemy_type):
    enemy = Enemy(enemy_type)
    enemies.append(enemy)

def get_wave():
    if level <= 5:
        return ['blue'] * (level * 5)
    elif level <= 10:
        return ['blue'] * (level * 3) + ['green'] * (level - 5)
    else:
        return ['blue'] * (level * 2) + ['green'] * (level - 5) + ['red'] * (level - 10)

def draw_menu(text, button_text):
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    text = font.render(text, True, BLACK)
    text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
    screen.blit(text, text_rect)

    button_font = pygame.font.Font(None, 50)
    button_text = button_font.render(button_text, True, BLACK)
    button_rect = button_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 50))
    pygame.draw.rect(screen, GREEN, (button_rect.x - 10, button_rect.y - 10, button_rect.width + 20, button_rect.height + 20))
    screen.blit(button_text, button_rect)

    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    waiting = False
                    return True
    return True

def game_loop():
    global lives, money, level, towers, enemies, projectiles

    clock = pygame.time.Clock()
    enemy_spawn_timer = 0
    running = True
    selected_tower = None
    wave = get_wave()
    wave_index = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    x, y = pygame.mouse.get_pos()
                    if y > HEIGHT - 60:
                        # Tower selection
                        selected_index = (x - 10) // 60
                        if 0 <= selected_index < len(TOWER_TYPES):
                            selected_tower = list(TOWER_TYPES.keys())[selected_index]
                    else:
                        # Place tower or select existing tower
                        tower_clicked = None
                        for tower in towers:
                            if math.sqrt((tower.x - x)**2 + (tower.y - y)**2) < 20:
                                tower_clicked = tower
                                break
                        
                        if tower_clicked:
                            for t in towers:
                                t.selected = False
                            tower_clicked.selected = True
                        elif selected_tower and money >= TOWER_TYPES[selected_tower]['cost']:
                            towers.append(Tower(x, y, selected_tower))
                            money -= TOWER_TYPES[selected_tower]['cost']
                            selected_tower = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    # Sell selected tower
                    for tower in towers:
                        if tower.selected:
                            money += int(TOWER_TYPES[tower.type]['cost'] * 0.8)
                            towers.remove(tower)
                            break

        # Spawn enemies
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= 60 and wave_index < len(wave):  # Spawn every second
            spawn_enemy(wave[wave_index])
            wave_index += 1
            enemy_spawn_timer = 0

        # Move enemies
        for enemy in enemies[:]:
            if enemy.move():
                enemies.remove(enemy)
                lives -= 1
                if lives <= 0:
                    return "game_over"

        # Update towers and fire projectiles
        for tower in towers:
            tower.update()
            for enemy in enemies:
                distance = math.sqrt((tower.x - enemy.x)**2 + (tower.y - enemy.y)**2)
                if distance <= tower.range:
                    tower.fire(enemy)
                    break

        # Move projectiles and check for hits
        for projectile in projectiles[:]:
            projectile.move()
            for enemy in enemies[:]:
                distance = math.sqrt((projectile.x - enemy.x)**2 + (projectile.y - enemy.y)**2)
                if distance < 15:  # Hit detection
                    new_enemy, value = enemy.take_damage(projectile.damage)
                    if new_enemy:
                        enemies[enemies.index(enemy)] = new_enemy
                    else:
                        enemies.remove(enemy)
                    money += value
                    projectiles.remove(projectile)
                    break
            else:
                if (projectile.x < 0 or projectile.x > WIDTH or
                    projectile.y < 0 or projectile.y > HEIGHT):
                    projectiles.remove(projectile)

        # Check for level completion
        if len(enemies) == 0 and wave_index >= len(wave):
            level += 1
            money += 50
            wave = get_wave()
            wave_index = 0
            if level > 20:  # Win condition
                return "victory"

        draw_game()
        clock.tick(60)

def main():
    global lives, money, level, towers, enemies, projectiles

    while True:
        # Show start menu
        if not draw_menu("Tower Defense", "Start Game"):
            return

        # Initialize game variables
        lives = 20
        money = 100
        level = 1
        towers = []
        enemies = []
        projectiles = []

        # Start game loop
        result = game_loop()

        if result == "quit":
            return
        elif result == "game_over":
            if not draw_menu("Game Over", "Play Again"):
                return
        elif result == "victory":
            if not draw_menu("Victory!", "Play Again"):
                return

if __name__ == "__main__":
    main()
    pygame.quit()
import random

WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
SKY = (135, 206, 235)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GROUND_Y = 500
frame_delay = 0.1
speed = 4
gravity = 0.5
jump_strength = -10

# Globais
game_state = "menu"
sound_on = True
boss_warning_timer = 0
boss_spawned = False

buttons = {
    "Jogar": Rect((300, 200), (200, 50)),
    "Som:": Rect((300, 280), (200, 50)),
    "Sair do jogo": Rect((300, 360), (200, 50)),
}

end_buttons = {
    "Continuar": Rect((300, 200), (200, 50)),
    "Sair do jogo": Rect((300, 280), (200, 50)),
}

# Sons
music.play('bg_music')
music.set_volume(0.12)
sfx_jump = sounds.jump
sfx_jump.set_volume(0.3)
sfx_punch = sounds.punch
sfx_punch.set_volume(0.05)
sfx_button = sounds.button
sfx_button.set_volume(0.2)

# Player
pink_monster = Actor('pink_monster_idle_0')
pink_monster.x = 100
pink_monster.y = GROUND_Y
pink_monster.vx = 0
pink_monster.vy = 0
pink_monster.on_ground = True
pink_monster.direction = 1
pink_monster.state = "idle"
pink_monster.frame_index = 0
pink_monster.frame_timer = 0
pink_monster.health = 20
pink_monster.scale = 2.5
PINK_MONSTER_MAX_HEALTH = 20

score = 0  # Score do jogador

zombies = []
boss = None

# Cooldown de ataque para zumbis em segundos
ZOMBIE_ATTACK_COOLDOWN = 1.0

animations = {
    "idle": [f"pink_monster_idle_{i}" for i in range(4)],
    "run": [f"pink_monster_run_{i}" for i in range(6)],
    "jump": [f"pink_monster_jump_0", f"pink_monster_jump_1"],
    "attack": [f"pink_monster_attack1_{i}" for i in range(4)],
    "zombie": [f"zombie_{i}" for i in range(3)],
    "boss": [f"boss_{i}" for i in range(3)]
}

def spawn_zombie():
    zombie = Actor('zombie_0')
    zombie.x = WIDTH + 50
    zombie.y = GROUND_Y
    zombie.vx = -1
    zombie.frame_index = 0
    zombie.frame_timer = 0
    zombie.health = 2
    zombie.last_attack_time = 0
    zombies.append(zombie)

def spawn_boss():
    global boss
    boss = Actor('boss_0')
    boss.x = WIDTH + 100
    boss.y = GROUND_Y
    boss.vx = -0.5
    boss.frame_index = 0
    boss.frame_timer = 0
    boss.health = 20
    boss.scale = 7
    boss.flip_x = True

def draw():
    screen.clear()
    if game_state == "menu":
        draw_menu()
    elif game_state == "jogo":
        draw_game()
    elif game_state == "fim":
        draw_end_game()
    elif game_state == "vitoria":
        draw_victory()

def draw_menu():
    # Fundo igual ao do jogo (ceu, sol, nuvens)
    screen.fill(SKY)
    screen.draw.filled_rect(Rect((WIDTH-100, 30), (60, 60)), (255, 255, 0))  # Sol
    for cloud in clouds:
        screen.draw.filled_rect(Rect((cloud["x"], cloud["y"]), (80, 30)), (255, 255, 255))
    # Titulo e botoes
    draw_text_outline("Aventuras de PinkMonster", (WIDTH // 2, 100), 60, WHITE, center=True)
    for name, rect in buttons.items():
        screen.draw.filled_rect(rect, DARK_GRAY)
        label = "Som: ON" if name == "Som:" and sound_on else name if name != "Som:" else "Som: OFF"
        draw_text_outline(label, rect.center, 36, WHITE, center=True)

def draw_end_game():
    screen.fill((30, 30, 30))
    screen.draw.text("Game Over!", center=(WIDTH // 2, 100), fontsize=60, color=RED)
    for name, rect in end_buttons.items():
        screen.draw.filled_rect(rect, DARK_GRAY)
        screen.draw.text(name, center=rect.center, fontsize=36, color=WHITE)

def draw_victory():
    # Fundo igual ao do jogo (ceu, sol, nuvens)
    screen.fill(SKY)
    screen.draw.filled_rect(Rect((WIDTH-100, 30), (60, 60)), (255, 255, 0))  # Sol
    for cloud in clouds:
        screen.draw.filled_rect(Rect((cloud["x"], cloud["y"]), (80, 30)), (255, 255, 255))
    # Texto e botao
    draw_text_outline("Parabens, voce ganhou!", (WIDTH // 2, 100), 60, GREEN, center=True)
    rect = Rect((300, 300), (200, 50))
    screen.draw.filled_rect(rect, DARK_GRAY)
    draw_text_outline("Voltar ao menu", rect.center, 36, WHITE, center=True)

def draw_health_bar(actor, max_health):
    # Barra de HP do Pink Monster e do Boss (maior para identificar o boss)
    if actor == pink_monster:
        bar_width = 60
    elif actor == boss:
        bar_width = 120
    else:
        bar_width = 50

    bar_height = 5
    health_ratio = actor.health / max_health
    x = actor.x - bar_width // 2
    y = actor.y - actor.height // 2 - 20
    # Borda preta
    screen.draw.rect(Rect((x-1, y-1), (bar_width+2, bar_height+2)), (0,0,0))
    # Barra vermelha (fundo)
    screen.draw.filled_rect(Rect((x, y), (bar_width, bar_height)), RED)
    # Barra verde (vida)
    screen.draw.filled_rect(Rect((x, y), (bar_width * health_ratio, bar_height)), GREEN)

def draw_game():
    screen.fill(SKY)
    screen.draw.filled_rect(Rect((0, GROUND_Y), (WIDTH, HEIGHT - GROUND_Y)), (34, 139, 34))

    screen.draw.filled_rect(Rect((WIDTH-100, 30), (60, 60)), (255, 255, 0))

    for cloud in clouds:
        screen.draw.filled_rect(Rect((cloud["x"], cloud["y"]), (80, 30)), (255, 255, 255))

    # Controles e score
    draw_text_outline("Controles: Atacar - Q | Movimentar: Setinhas.", (10, 10), 32, WHITE)
    draw_text_outline(f"Score: {score}", (10, 50), 32, WHITE)

    pink_monster.flip_x = pink_monster.direction == -1
    pink_monster.draw()
    draw_health_bar(pink_monster, PINK_MONSTER_MAX_HEALTH)

    for zombie in zombies:
        zombie.flip_x = zombie.vx > 0
        zombie.draw()
        draw_health_bar(zombie, 2)

    if boss:
        boss.flip_x = True
        boss.x = int(boss.x)
        boss.y = int(boss.y)
        boss.draw()
        draw_health_bar(boss, 20)

    # Texto de aviso do chefe
    if boss_warning_timer > 0:
        import math, time
        t = time.time()
        pulse = 1 + 0.15 * math.sin(t * 4)
        font_size = int(48 * pulse)
        draw_text_outline("O Chefe esta vindo!", (WIDTH // 2, 80), font_size, RED, center=True)

# Função util para desenhar texto com outline preto (obrigada copilot :) )
def draw_text_outline(text, pos, fontsize, color, center=False):
    offsets = [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,-2),(-2,2),(2,2)]
    for dx, dy in offsets:
        if center:
            screen.draw.text(text, center=(pos[0]+dx, pos[1]+dy), fontsize=fontsize, color=(0,0,0))
        else:
            screen.draw.text(text, topleft=(pos[0]+dx, pos[1]+dy), fontsize=fontsize, color=(0,0,0))
    if center:
        screen.draw.text(text, center=pos, fontsize=fontsize, color=color)
    else:
        screen.draw.text(text, topleft=pos, fontsize=fontsize, color=color)

def on_mouse_down(pos):
    global game_state, sound_on, score, boss, boss_spawned, boss_warning_timer
    if game_state == "menu":
        if buttons["Jogar"].collidepoint(pos):
            if sound_on:
                sfx_button.play()
            game_state = "jogo"
            pink_monster.health = PINK_MONSTER_MAX_HEALTH
            pink_monster.x = 100
            pink_monster.y = GROUND_Y
            pink_monster.vx = 0
            pink_monster.vy = 0
            zombies.clear()
            score = 0  # Reinicia a pontuação
            music.play('bg_music')
        elif buttons["Som:"].collidepoint(pos):
            if sound_on:
                sfx_button.play()
            sound_on = not sound_on
            if sound_on:
                music.unpause()
            else:
                music.pause()
        elif buttons["Sair do jogo"].collidepoint(pos):
            if sound_on:
                sfx_button.play()
            quit()
    elif game_state == "fim":
        if end_buttons["Continuar"].collidepoint(pos):
            if sound_on:
                sfx_button.play()
            # Reinicia o jogo completamente
            game_state = "menu"
            pink_monster.health = PINK_MONSTER_MAX_HEALTH
            pink_monster.x = 100
            pink_monster.y = GROUND_Y
            pink_monster.vx = 0
            pink_monster.vy = 0
            pink_monster.on_ground = True
            pink_monster.direction = 1
            pink_monster.state = "idle"
            pink_monster.frame_index = 0
            pink_monster.frame_timer = 0
            zombies.clear()
            score = 0
            boss = None
            boss_spawned = False
            boss_warning_timer = 0
            music.play('bg_music')
        elif end_buttons["Sair do jogo"].collidepoint(pos):
            if sound_on:
                sfx_button.play()
            quit()
    elif game_state == "vitoria":
        rect = Rect((300, 300), (200, 50))
        if rect.collidepoint(pos):
            if sound_on:
                sfx_button.play()
            game_state = "menu"
            score = 0
            pink_monster.health = PINK_MONSTER_MAX_HEALTH
            pink_monster.x = 100
            pink_monster.y = GROUND_Y
            pink_monster.vx = 0
            pink_monster.vy = 0
            zombies.clear()
            boss = None
            boss_spawned = False
            boss_warning_timer = 0
            music.play('bg_music')

def on_key_down(key):
    global game_state
    if game_state == "jogo" and key == keys.ESCAPE:
        game_state = "menu"
        music.pause()
    # Toca o som do soco apenas quando Q é pressionado
    if game_state == "jogo" and key == keys.Q:
        pink_monster.state = "attack"
        if sound_on:
            sfx_punch.play()

def update():
    if game_state == "jogo":
        update_pink_monster()
        update_zombies()
        update_boss()
        update_spawn()
        check_collisions()
        for cloud in clouds:
            cloud["x"] += cloud["speed"]
            if cloud["x"] > WIDTH + 40:
                cloud["x"] = -80
                cloud["y"] = random.randint(30, 120)
                cloud["speed"] = random.uniform(0.3, 0.7)

def update_pink_monster():
    pink_monster.vx = 0
    if keyboard.left or keyboard.a:
        pink_monster.vx = -speed
        pink_monster.direction = -1
    if keyboard.right or keyboard.d:
        pink_monster.vx = speed
        pink_monster.direction = 1
    if (keyboard.space or keyboard.w or keyboard.up) and pink_monster.on_ground:
        pink_monster.vy = jump_strength
        pink_monster.on_ground = False
        if sound_on:
            sfx_jump.play()

    if keyboard.q:
        pink_monster.state = "attack"
    elif not pink_monster.on_ground:
        pink_monster.state = "jump"
    elif pink_monster.vx != 0:
        pink_monster.state = "run"
    else:
        pink_monster.state = "idle"

    pink_monster.x += pink_monster.vx
    pink_monster.vy += gravity
    pink_monster.y += pink_monster.vy

    # Limita o movimento do Pink Monster (impede que ele saia da tela)
    min_x = 30
    max_x = WIDTH - 30
    if pink_monster.x < min_x:
        pink_monster.x = min_x
    if pink_monster.x > max_x:
        pink_monster.x = max_x

    if pink_monster.y >= GROUND_Y:
        pink_monster.y = GROUND_Y
        pink_monster.vy = 0
        pink_monster.on_ground = True

    pink_monster.frame_timer += 1 / 60
    if pink_monster.frame_timer >= frame_delay:
        pink_monster.frame_timer = 0
        pink_monster.frame_index = (pink_monster.frame_index + 1) % len(animations[pink_monster.state])
        pink_monster.image = animations[pink_monster.state][pink_monster.frame_index]

def update_zombies():
    for zombie in zombies:
        zombie.x += zombie.vx
        zombie.frame_timer += 1 / 60
        if zombie.frame_timer >= frame_delay:
            zombie.frame_timer = 0
            zombie.frame_index = (zombie.frame_index + 1) % len(animations["zombie"])
            zombie.image = animations["zombie"][zombie.frame_index]

    zombies[:] = [z for z in zombies if z.health > 0 and z.x > -50]

def update_boss():
    global boss_warning_timer, boss_spawned
    if not boss_spawned and random.random() < 0.001:
        boss_warning_timer = 3
        boss_spawned = True
    elif boss_warning_timer > 0:
        boss_warning_timer -= 1 / 60
        if boss_warning_timer <= 0:
            spawn_boss()
    if boss:
        boss.x += boss.vx
        boss.frame_timer += 1 / 60
        if boss.frame_timer >= frame_delay:
            boss.frame_timer = 0
            boss.frame_index = (boss.frame_index + 1) % len(animations["boss"])
            boss.image = animations["boss"][boss.frame_index]

def check_collisions():
    global game_state, boss, boss_spawned, score
    import time
    now = time.time()
    for zombie in zombies:
        # Range do soco
        distance = abs(pink_monster.x - zombie.x)
        attack_range = 75
        if pink_monster.state == "attack" and distance < attack_range and abs(pink_monster.y - zombie.y) < 40:
            zombie.health -= 0.5
            if pink_monster.health < PINK_MONSTER_MAX_HEALTH:
                pink_monster.health += 2
                if pink_monster.health > PINK_MONSTER_MAX_HEALTH:
                    pink_monster.health = PINK_MONSTER_MAX_HEALTH
            # Score aumenta quando mata um zumbi
            if zombie.health <= 0:
                score += 1
                if score >= 50:
                    game_state = "vitoria"
                    music.stop()
        elif pink_monster.colliderect(zombie):
            if not hasattr(zombie, 'last_attack_time'):
                zombie.last_attack_time = 0
            if now - zombie.last_attack_time > ZOMBIE_ATTACK_COOLDOWN:
                pink_monster.health -= 0.25
                zombie.last_attack_time = now

    if boss:
        if pink_monster.colliderect(boss):
            if pink_monster.state == "attack":
                boss.health -= 0.5
            else:
                pink_monster.health -= 0.5
        if boss.health <= 0:
            boss = None
            boss_spawned = False

    if pink_monster.health <= 0:
        game_state = "fim"
        music.stop()


clouds = [
    {"x": random.randint(0, WIDTH), "y": random.randint(30, 120), "speed": random.uniform(0.3, 0.7)}
    for _ in range(4)
]

def update_spawn():
    if random.random() < 0.03:
        spawn_zombie()

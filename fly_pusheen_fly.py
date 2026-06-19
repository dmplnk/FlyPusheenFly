import os
import random
import sys
import pygame

pygame.init()

# ---------- НАСТРОЙКИ ----------
FPS = 60

BASE_INTERVAL = 1500
MIN_INTERVAL = 300

WIDTH, HEIGHT = 500, 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fly, Pusheen, fly !")

clock = pygame.time.Clock()

# ---------- ПУТИ ----------
def path(p):
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.abspath(".")
    return  os.path.join(base, p)

appdata = os.getenv("APPDATA")
game_folder = os.path.join(appdata, "PusheenFly")
os.makedirs(game_folder, exist_ok=True)

best_score_file = os.path.join(game_folder, "bestscore.txt")

# ---------- РЕСУРСЫ ----------
cats_game = {
    "pusheen": pygame.image.load(path("data/baloons_pusheen_game.png")),
    "dark_cat": pygame.image.load(path("data/dark_cat_game.png")),
    "light_cat": pygame.image.load(path("data/light_cat_game.png"))
}

cats_menu = {
    "pusheen": pygame.image.load(path("data/baloons_pusheen.png")),
    "dark_cat": pygame.image.load(path("data/dark_cat.png")),
    "light_cat": pygame.image.load(path("data/light_cat.png"))
}

cloud_imgs = [pygame.image.load(path("data/cloud_1.png")), pygame.image.load(path("data/cloud_2.png"))]
cat_cloud = pygame.image.load(path("data/cat_cloud.png"))

menu_bg = pygame.image.load(path("data/background_menu.png"))

icon = pygame.image.load(path("data/icon.png"))
pygame.display.set_icon(icon)

# ---------- ЗВУКИ ----------
try:
    sounds = {
        "hit": pygame.mixer.Sound(path("data/miu.mp3")),
        "choose": pygame.mixer.Sound(path("data/choose_miu.mp3")),
        "button": pygame.mixer.Sound(path("data/button.mp3")),
        "cloud_cat": pygame.mixer.Sound(path("data/cloudmiu.mp3"))
    }

    pygame.mixer.music.load(path("data/back.mp3"))
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)
except:
    sounds = {}

# ---------- КЛАССЫ ----------
class Player:
    def __init__(self):
        self.rect = cats_game["pusheen"].get_rect(center=(250, 425))
        self.speed = 5

    def update(self, cat):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

        screen.blit(cats_game[cat],self.rect)

class Cloud(pygame.sprite.Sprite):
    def __init__(self, group, score):
        super().__init__()
        if score % 14 == 0 and score != 0:
            self.image = cat_cloud
            self.speed = 1
            if "cloud_cat" in sounds:
                sounds["cloud_cat"].play()
        else:
            self.image = random.choice(cloud_imgs)
            self.speed = 2
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), -50))
        self.add(group)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# ---------- ДАННЫЕ ----------
player = Player()
clouds = pygame.sprite.Group()

cat = "pusheen"
mode = "menu"
score = 0
interval = BASE_INTERVAL

font20 = pygame.font.SysFont("verdana", 20)
font50 = pygame.font.SysFont("verdana", 50)

pygame.time.set_timer(pygame.USEREVENT, interval)

try:
    best = int(open(best_score_file).read())
except:
    best = 0

# ---------- ФУНКЦИИ РЕЖИМОВ ----------
def menu(events):
    global  cat, mode, score

    screen.blit(menu_bg, (0, 0))

    positions = {"dark_cat": 177, "pusheen": 250, "light_cat": 318}

    for name, x in positions.items():

        rect = cats_game[name].get_rect(center=(x, 425))
        screen.blit(cats_game[name], rect)

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(e.pos):
                cat = name
                if "button" in sounds:
                    sounds["button"].play()

        rect = cats_menu[cat].get_rect(center=(150, 150))
        screen.blit(cats_menu[cat], rect)

        btn = pygame.Rect(150, 300, 200, 50)
        col = "#efd2d2" if btn.collidepoint(pygame.mouse.get_pos()) else "#fcdcdd"

        pygame.draw.rect(screen, col, btn)
        screen.blit(font20.render("PLAY", 1, "white"), font20.render("PLAY", 1, "white").get_rect(center=btn.center))


        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and btn.collidepoint(e.pos):
                if "choose" in sounds:
                    sounds["choose"].play()
                pygame.mouse.set_visible(False)
                mode = "game"
                score = 0
                clouds.empty()

def game():
    global mode

    screen.fill("#b6daf0")

    clouds.update()

    if pygame.sprite.spritecollide(player, clouds, False):
        if "hit" in sounds:
            sounds["hit"].play()
            pygame.mouse.set_visible(True)
            clouds.empty()
            mode = "gameover"

    clouds.draw(screen)
    player.update(cat)

    screen.blit(font20.render(str(score), 1, "#6c5c4b"), (WIDTH//2, 30))

def gameover(events):
    global best, mode

    screen.fill("#b6daf0")

    screen.blit(font50.render(f"score: {score}", 1, "white"), (120, 150))

    if score > best:
        best = score
        open(best_score_file, "w").write(str(best))

    screen.blit(font20.render(f"best score: {best}", 1, "white"), (160, 250))
    screen.blit(font20.render("press SPACE", 1, "white"), (180, 320))

    for e in events:
        if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
            if "button" in sounds:
                sounds["button"].play()
            mode = "menu"

# ---------- MAIN LOOP ----------
running = True

while running:
    events = pygame.event.get()

    for e in events:
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.USEREVENT and mode == "game":
            score += 1

            if score % 7 == 0:
                interval = max(MIN_INTERVAL, interval - 80)
                pygame.time.set_timer(pygame.USEREVENT, interval)

            Cloud(clouds, score)

            if score % 2 == 0:
                player.rect.y += 5
            else:
                player.rect.y -= 5

    if mode == "menu": menu(events)
    elif mode == "game": game()
    elif mode == "gameover": gameover(events)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()






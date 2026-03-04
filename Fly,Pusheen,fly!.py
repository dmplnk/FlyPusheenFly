import os
import random
import sys

import pygame
pygame.init()

FPS = 60
clock = pygame.time.Clock()

base_interval = 1500  # начальный интервал в мс (1.5 секунды)
min_interval = 300    # минимальная задержка — не меньше 300 мс (0.3 с)
cloud_multiplier = 1 # начальное количество облаков за раз

pygame.time.set_timer(pygame.USEREVENT, base_interval)

appdata_path = os.getenv("APPDATA")
game_folder = os.path.join(appdata_path, "PusheenFly")
os.makedirs(game_folder, exist_ok=True)

def resource_path(relative_path):
    try:
        # При работе с PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # При обычной работе
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# создание окна
width = 500
height = 500

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Fly, Pusheen, fly !")
try:
    icon_path = resource_path('data/icon.png')
    if os.path.exists(icon_path):
        pygame.display.set_icon(pygame.image.load(icon_path))
    else:
        print(f"Иконка не найдена по пути: {icon_path}")
except Exception as e:
    print(f"Ошибка при загрузке иконки: {e}")

try:
    collusionsound = pygame.mixer.Sound(resource_path("data/miu.mp3"))
    choosesound = pygame.mixer.Sound(resource_path("data/choose_miu.mp3"))
    buttonsound = pygame.mixer.Sound(resource_path("data/button.mp3"))
    cloudcatcaound = pygame.mixer.Sound(resource_path("data/cloudmiu.mp3"))
    backmusic = pygame.mixer.music.load(resource_path("data/back.mp3"))
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Ошибка при загрузке звуков: {e}")

def get_cloud_count(score):
    """Возвращает количество облаков для создания на основе счёта"""
    return 1 + score // 10  # +1 облако каждые 10 очков


# класс игрока
class Player():
    def __init__(self, cat):
        self.image = pygame.image.load(resource_path("data/baloons_pusheen_game.png"))
        self.rect = self.image.get_rect(center=(250, 425))
        self.speed = 5

    def update(self):
        if cat == "pusheen":
            self.image = pygame.image.load(resource_path("data//baloons_pusheen_game.png"))
        elif cat == "dark":
            self.image = pygame.image.load(resource_path("data//dark_cat_game.png"))
        elif cat == "light":
            self.image = pygame.image.load(resource_path("data//light_cat_game.png"))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < width:
            self.rect.x += self.speed

# класс облаков
class Cloud(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__()
        global score
        if score % 14 == 0 and score != 0:
            self.image = pygame.image.load(resource_path("data//cat_cloud.png"))
            self.speed = 1
            cloudcatcaound.play()
        else:
            self.image = random.choice((pygame.image.load(resource_path("data//cloud_1.png")) , pygame.image.load(resource_path("data//cloud_2.png"))))
            self.speed = 2
        x_center = random.randint(0, width)
        self.rect = self.image.get_rect(center=(x_center, -50))


        self.add(group)

    def update(self):
        if self.rect.top <= height:
            self.rect.y += self.speed
        else:
            self.kill()

# режим меню
def Menu(events):

    #выбор котика
    class Cat_choose:
        def __init__(self, image, x, y, name):
            self.serf = image
            self.rect = image.get_rect(center=(x, y))
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.serf = pygame.transform.scale(self.serf, (self.serf.get_width() * 0.9, self.serf.get_height() * 0.9))
            screen.blit(self.serf, self.rect)
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.rect.collidepoint(event.pos):
                        global cat
                        if cat != name:
                            buttonsound.play()
                            cat = name

    # создание фона
    background = pygame.image.load(resource_path("data//backgound_menu.png"))
    screen.blit(background, background.get_rect())



    # добавление котика
    Cat_choose(pygame.image.load(resource_path("data//baloons_pusheen_game.png")), 250, 425, "pusheen")
    Cat_choose(pygame.image.load(resource_path("data//dark_cat_game.png")), 177, 425, "dark")
    Cat_choose(pygame.image.load(resource_path("data//light_cat_game.png")), 318, 425, "light")

    if cat == "pusheen":
        cat_serf = pygame.image.load(resource_path("data//baloons_pusheen.png"))
    elif cat == "dark":
        cat_serf = pygame.image.load(resource_path("data//dark_cat.png"))
    elif cat == "light":
        cat_serf = pygame.image.load(resource_path("data//light_cat.png"))
    cat_rect = cat_serf.get_rect(center=(150, 155))
    screen.blit(cat_serf, cat_rect)

    # добавление кнопки PLAY
    button = pygame.draw.rect(screen, "#fcdcdd", (150, 300, 200, 50))
    if button.collidepoint(pygame.mouse.get_pos()):
        button = pygame.draw.rect(screen, "#efd2d2", (150, 300, 200, 50))
    font = pygame.font.SysFont("verdana", 20)
    text = font.render(("PLAY"), True, "white")
    text_rect = text.get_rect(center=(250, 325))
    screen.blit(text, text_rect)
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if button.collidepoint(event.pos):
            choosesound.play()
            global wind, score
            pygame.mouse.set_visible(False)
            wind = "game"
            score = 0

# режим игры
def Game():

    clouds.update()

    # прооверка столкновения котика сс облаком
    gameover = pygame.sprite.spritecollide(player, clouds, False)
    if gameover:
        cloudcatcaound.stop()
        collusionsound.play()
        global wind
        pygame.mouse.set_visible(True)
        wind = "gameover"
        clouds.remove(clouds)

    # отрисовка
    clouds.draw(screen)

    player.update()
    screen.blit(player.image, player.rect)

    font = pygame.font.SysFont("verdana", 20)
    text = font.render(str(score), True, "#6c5c4b")
    text_rect = text.get_rect(center=(width // 2, 30))
    screen.blit(text, text_rect)

# режим проигрыша
def Gameover():
    global best_score

    # счет игры
    font = pygame.font.SysFont("verdana", 50)
    text = font.render("score: " + str(score), True, "white")
    text_rect = text.get_rect(center=(width // 2, height // 2 - 100))
    screen.blit(text, text_rect)

    # лучший счет
    if score > int(best_score):
        try:
            with open(best_score_file_path, "w") as file:
                file.write(str(score))
            best_score = score
        except Exception as e:
            print(f"Ошибка при записи bestscore.txt: {e}")
    font = pygame.font.SysFont("verdana", 20)
    text = font.render("best score: " + str(best_score), True, "white")
    text_rect = text.get_rect(center=(width // 2, height // 2 - 50))
    screen.blit(text, text_rect)

    # возвращение в меню
    font = pygame.font.SysFont("verdana", 20)
    text = font.render(("press SPACE"), True, "white")
    text_rect = text.get_rect(center=(250, 325))
    screen.blit(text, text_rect)


# переменные
running = True
wind = "menu"

score = 0
best_score_file_path = os.path.join(game_folder, "bestscore.txt")

try:
    # Пытаемся открыть файл для чтения
    with open(best_score_file_path, "r") as file:
        best_score = int(file.read().strip())  # Добавляем strip() для очистки от пробелов
except FileNotFoundError:
    # Если файл не найден, создаем его с начальным значением
    best_score = 0
    with open(best_score_file_path, "w") as file:
        file.write(str(best_score))


cat = "pusheen"
player = Player(cat)
clouds = pygame.sprite.Group()
Cloud(clouds)

# игровой цикл
while running:
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.USEREVENT and wind == "game":
            score += 1
            # Увеличиваем частоту появления облаков (уменьшаем интервал)
            # Каждые 7 очков уменьшаем интервал на 80 мс, но не ниже min_interval
            if score % 7 == 0:
                base_interval = max(min_interval, base_interval - 80)
                pygame.time.set_timer(pygame.USEREVENT, base_interval)

            # Создаём облака — количество зависит от cloud_multiplier
            Cloud(clouds)

            # Движение игрока (каждые 2 очка)
            if score % 2 == 0:
                player.rect.y += 5
            else:
                player.rect.y -= 5
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and wind == "gameover":
            buttonsound.play()
            wind = "menu"

    # проверка режима
    if wind == "menu":
        Menu(events)
    if wind == "game":
        screen.fill("#b6daf0")
        Game()
    if wind == "gameover":
        screen.fill("#b6daf0")
        Gameover()

    pygame.display.flip()
    clock.tick(FPS)

import random
import pygame

###############################################################
# 기본 초기화
pygame.init()

# 화면 크기 설정
screen_width = 1000  # 가로
screen_height = 800  # 세로
screen = pygame.display.set_mode((screen_width, screen_height))

# 타이틀
pygame.display.set_caption("python crazy arcade")

# FPS
clock = pygame.time.Clock()
###############################################################
# 폰트
title_font = pygame.font.Font(None, 120)
menu_font = pygame.font.Font(None, 70)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

#bgm
bgm = pygame.mixer.Sound("./sounds/bgm.wav")
bgm.set_volume(0.2)
bgm.play(-1)

clear_sound = pygame.mixer.Sound("./sounds/clear.wav")
gameover_sound = pygame.mixer.Sound("./sounds/gameover.wav")

# 배경
background = pygame.image.load("./images/background.png")

class Enemy:
    enemy = pygame.image.load("./images/enemy.png")
    enemy_caught = pygame.image.load("./images/enemy_caught.png")

    kill_enemy = pygame.mixer.Sound("./sounds/kill_enemy.wav")

    kill_enemy.set_volume(0.5)

    size = enemy.get_rect().size
    width = size[0]
    height = size[1]

    x = None    # x 좌표
    y = None    # y 좌표

    speed = 3  # 적 이동 속도

    isAlive = True  # False면 없어짐
    isCaught = False  # 물줄기에 닿으면 True가 되고 없앨 수 있는 상태가 됨

    time = 5  # 물풍선에 잡혀있는 시간
    elapsed_time = 0
    start_ticks = None

    def __init__(self):
        # 처음 이동할 방향을 랜덤하게 설정
        self.x_direction = random.randrange(-1, 2, 2)  # -1부터 2까지 2씩 증가 -> x_direction = -1, 1
        self.y_direction = random.randrange(-1, 2, 2)

    def setPosition(self, x, y):
        self.x = x
        self.y = y

    # 충돌이 너무 민감해서 살짝 포개지면 충돌 판정이 생기도록 rect 범위를 줄여서 return
    def get_rect(self):
        rect_x = self.x + self.width / 8
        rect_y = self.y + self.width / 8
        rect_width = self.width - self.width / 4

        rect = pygame.Rect(rect_x, rect_y, rect_width, rect_width)

        return rect

    def displayEnemy(self):
        if not self.isCaught:
            screen.blit(self.enemy, (self.x, self.y))
        else:
            screen.blit(self.enemy_caught, (self.x, self.y))

    def moveEnemy(self):
        if not self.isCaught:  # 물에 잡히면 안 움직임
            # 1/70의 확률로 진행 방향 변경
            if random.randrange(70) == 0:
                self.x_direction *= -1
            if random.randrange(70) == 0:
                self.y_direction *= -1

            self.x += self.speed * self.x_direction
            self.y += self.speed * self.y_direction

            # 화면 밖으로 못 나가게
            if self.x < 0 or self.x > screen_width - self.width:
                self.x_direction *= -1
            if self.y < 0 or self.y > screen_height - self.height:
                self.y_direction *= -1

    # 물풍선에 닿으면 반대 방향으로 진행
    def reachBalloon(self):
        self.x_direction *= -1
        self.y_direction *= -1

    # 물풍선에 갇혀있는 시간을 측정하기 위해 start_ticks를 설정
    def setStartTicks(self):
        if not self.isCaught:
            self.start_ticks = pygame.time.get_ticks()

    # 적이 물풍선에 맞으면 일정 시간동안만 갇혀있게 하는 함수
    def countdown(self):
        if self.isCaught:
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000
            timer = self.time - self.elapsed_time
            if timer < 0:
                self.isCaught = False

    # 적을 없애는 함수
    def killEnemy(self):
        self.kill_enemy.play()
        self.isAlive = False

    # 물줄기와 닿았을 때
    def beCaught(self):
        self.setStartTicks()
        self.isCaught = True

    def showEnemy(self):
        self.displayEnemy()
        self.moveEnemy()
        self.countdown()

class Balloon:
    # 풍선 만들기
    balloon = pygame.image.load("./images/waterballoon.png")

    water_center = pygame.image.load("./images/water_center.png")
    water_left = pygame.image.load("./images/water_left.png")
    water_right = pygame.image.load("./images/water_right.png")
    water_top = pygame.image.load("./images/water_top.png")
    water_bottom = pygame.image.load("./images/water_bottom.png")

    balloon_sound = pygame.mixer.Sound("./sounds/balloon.wav")
    water_sound = pygame.mixer.Sound("./sounds/water.wav")

    balloon_sound.set_volume(0.5)

    waters = [water_center, water_left, water_right, water_top, water_bottom]

    water_size = water_center.get_rect().size
    water_width = water_size[0]

    time = 3  # 물풍선 터지는 시간
    elapsed_time = 0
    isRemaining = True  # False면 없어짐
    isWater = False  # 풍선이 터졌는지 (현재 물줄기인지)

    # 최초에 캐릭터가 물풍선을 놓으면 충돌처리가 되기 때문에 처음엔 충돌이 돼도 물풍선 위를 지나가게 하고
    # 그 다음에 물풍선과 캐릭터가 충돌하면 물풍선 위를 지나가지 못하게 하는 변수
    inCharacter = True

    def __init__(self, player):
        self.x = player.x  # 물풍선이 놓아지는 자리는 캐릭터의 자리와 같음
        self.y = player.y
        self.start_ticks = pygame.time.get_ticks()
        self.player = player

        self.balloon_sound.play()   # 물풍선 놓이는 효과음

    def get_rect(self):
        rect = self.balloon.get_rect()
        rect.left = self.x
        rect.top = self.y

        return rect

    def displayBalloon(self):
        screen.blit(self.balloon, (self.x, self.y))

    # 물풍선을 일정 시간만 존재하게
    def countdown(self):
        self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000
        timer = self.time - self.elapsed_time

        if timer < 0:
            if not self.isWater:
                self.water_sound.play()
            self.isWater = True
            self.spreadWater()  # 설정해둔 time이 지나면 풍선이 터짐

        if timer < -0.2:  # 물줄기가 0.2초동안 유지됨
            self.isRemaining = False    # 사라짐
            self.player.count_balloons += 1

    # 물줄기 뻗어나가게
    def spreadWater(self):
        screen.blit(self.waters[0], (self.x, self.y))
        for i in range(1, self.player.water_length + 1):
            screen.blit(self.waters[1], (self.x - self.water_width * i, self.y))
            screen.blit(self.waters[2], (self.x + self.water_width * i, self.y))
            screen.blit(self.waters[3], (self.x, self.y - self.water_width * i))
            screen.blit(self.waters[4], (self.x, self.y + self.water_width * i))

    # 물줄기 영역 return
    def getWaterRect(self):
        water_pos_x_hor = self.x - self.water_width * self.player.water_length
        water_pos_y_hor = self.y
        water_pos_x_ver = self.x
        water_pos_y_ver = self.y - self.water_width * self.player.water_length

        # 가로가 긴 물줄기
        water_rect_hor = pygame.Rect(water_pos_x_hor, water_pos_y_hor,
                                     self.water_width + self.water_width * 2 * self.player.water_length,
                                     self.water_width)
        # 세로가 긴 물줄기
        water_rect_ver = pygame.Rect(water_pos_x_ver, water_pos_y_ver, self.water_width,
                                     self.water_width + self.water_width * 2 * self.player.water_length)

        return [water_rect_hor, water_rect_ver]

    def showBalloon(self):
        self.displayBalloon()
        self.countdown()

class Character:
    # 캐릭터 만들기
    character = pygame.image.load("./images/character.png")
    character_caught = pygame.image.load("./images/character_caught.png")

    size = character.get_rect().size
    width = size[0]
    height = size[1]

    x = None    # 캐릭터 x 좌표
    y = None    # 캐릭터 y 좌표

    # 캐릭터 이동 방향
    to_x_l = 0
    to_x_r = 0
    to_y_u = 0
    to_y_d = 0

    # 캐릭터 이동 속도
    speed = 5

    water_length = 1  # 물줄기 길이
    count_balloons = 2  # 물풍선 개수
    balloons = []   # 풍선은 여러발 발사 가능

    isCaught = False # 캐릭터가 물풍선에 맞으면 True

    def setPosition(self, x, y):
        self.x = x
        self.y = y

    # 충돌이 너무 민감해서 살짝 포개지면 충돌 판정이 생기도록 rect 범위를 줄여서 return
    def get_rect(self):
        rect_x = self.x + self.width / 8
        rect_y = self.y + self.width / 8
        rect_width = self.width - self.width / 4

        rect = pygame.Rect(rect_x, rect_y, rect_width, rect_width)

        return rect

    def displayCharacter(self):
        if not self.isCaught:
            screen.blit(self.character, (self.x, self.y))
        else:
            screen.blit(self.character_caught, (self.x, self.y))

    # 캐릭터 키 이벤트 처리
    def characterKeyEvent(self):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  # 캐릭터를 왼쪽으로
                self.to_x_l -= self.speed
            elif event.key == pygame.K_RIGHT:  # 캐릭터를 오른쪽으로
                self.to_x_r += self.speed
            elif event.key == pygame.K_UP:  # 캐릭터를 위로
                self.to_y_u -= self.speed
            elif event.key == pygame.K_DOWN:  # 캐릭터를 아래로
                self.to_y_d += self.speed
            elif event.key == pygame.K_SPACE and self.count_balloons > 0:  # 물풍선 발사
                self.balloons.append(Balloon(self))
                self.count_balloons -= 1

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.to_x_l = 0
            elif event.key == pygame.K_RIGHT:
                self.to_x_r = 0
            elif event.key == pygame.K_UP:
                self.to_y_u = 0
            elif event.key == pygame.K_DOWN:
                self.to_y_d = 0

    # 캐릭터 위치 설정
    def characterMove(self):
        self.x = self.x + self.to_x_l + self.to_x_r
        self.y = self.y + self.to_y_u + self.to_y_d

        # 화면 벗어나지 못하게
        if self.x < 0:
            self.x = 0
        elif self.x > screen_width - self.width:
            self.x = screen_width - self.width

        if self.y < 0:
            self.y = 0
        elif self.y > screen_height - self.height:
            self.y = screen_height - self.height

    # 물풍선에 닿았을 때 물풍선을 통과하지 못하게
    def reachBalloon(self, balloon):
        self.to_x_l -= self.to_x_l
        self.to_x_r -= self.to_x_r
        self.to_y_u -= self.to_y_u
        self.to_y_d -= self.to_y_d
        self.characterMove()
        balloon.inCharacter = True

class Item:
    item_balloon = pygame.image.load("./images/item_balloon.png")
    item_length = pygame.image.load("./images/item_length.png")
    item_speed = pygame.image.load("./images/item_speed.png")

    items = [item_balloon, item_length, item_speed]

    item_size = item_balloon.get_rect().size
    width = item_size[0]

    time = 10  # time이 지나면 아이템이 사라짐
    elapsed_time = 0

    isRemaining = True  # False면 아이템 사라짐

    def __init__(self):
        self.x = random.randrange(screen_width - self.width)
        self.y = random.randrange(screen_height - self.width)
        self.item = random.randrange(3)  # 0: balloon, 1: length, 2: speed
        self.start_ticks = pygame.time.get_ticks()

    # 충돌이 너무 민감해서 살짝 포개지면 충돌 판정이 생기도록 rect 범위를 줄여서 return
    def get_rect(self):
        rect_x = self.x + self.width / 8
        rect_y = self.y + self.width / 8
        rect_width = self.width - self.width / 4

        rect = pygame.Rect(rect_x, rect_y, rect_width, rect_width)

        return rect

    def displayItem(self):
        screen.blit(self.items[self.item], (self.x, self.y))

    # 아이템을 일정 시간동안만 존재하게 하는 함수
    def countdown(self):
        self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000
        timer = self.time - self.elapsed_time
        if timer < 0:
            self.isRemaining = False  # 설정해둔 time이 지나면 아이템이 사라짐

    # 캐릭터가 아이템을 먹었을 때
    def upgradePlayer(self, player):
        self.isRemaining = False
        if self.item == 0:
            player.count_balloons += 1
        elif self.item == 1:
            player.water_length += 1
        elif self.item == 2:
            player.speed += 2

    def showItem(self):
        self.displayItem()
        self.countdown()

# 시작 메뉴 보여주는 함수 -> 난이도 return
def startMenu():
    # stage = 0 -> EASY, 1 -> NORMAL, 2 -> HARD
    menuString = ['EASY', 'NORMAL', 'HARD']
    stage = 0   # default: EASY

    # 제목 설정
    title = title_font.render("Python CrazyArcade", True, WHITE)
    title_rect = title.get_rect(center=(screen_width / 2, screen_height / 2 - 150))

    while True:
        screen.fill(BLACK)  # 배경

        for event in pygame.event.get():
            if event.type == pygame.QUIT:   # 종료
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:    # 난이도 선택
                    stage -= 1
                elif event.key == pygame.K_DOWN:
                    stage += 1
                elif event.key == pygame.K_SPACE:   # 선택 완료
                    print("select")
                    return stage % 3

        for idx, str in enumerate(menuString):  # 메뉴 출력
            if stage % 3 == idx:  # 현재 선택한 메뉴는 글씨를 노랗게
                font_render = menu_font.render(f"{str}", True, YELLOW)
            else:
                font_render = menu_font.render(f"{str}", True, WHITE)

            font_rect = font_render.get_rect(center=(screen_width / 2, screen_height / 2 + 100 + 80 * idx))

            screen.blit(font_render, font_rect)

        screen.blit(title, title_rect)  # 제목

        pygame.display.update()

# 적 위치 세팅하는 함수
def setEnemy(stage, player):
    # 캐릭터로부터 일정 거리 주변으로는 적 생성 안 되게
    rect_x = player.x - player.width
    rect_y = player.y - player.height
    rect = pygame.Rect(rect_x, rect_y, player.width * 3, player.width * 3)

    enemies = []

    amount = 4 + stage * 4  # 적의 수. easy: 4, normal: 8, hard: 12

    while amount > 0:
        enemy = Enemy()
        enemy_x = random.randrange(screen_width - enemy.width)  # 적 위치 랜덤 지정
        enemy_y = random.randrange(screen_height - enemy.height)
        enemy.setPosition(enemy_x, enemy_y)

        if rect.colliderect(enemy.get_rect()):  # rect 설정한 범위 안에 적 생성됨
            print("재설정")
        else:
            amount -= 1
            enemies.append(enemy)

    return enemies

# 게임이 종료됐을 때 화면에 메세지 출력하는 함수
def gameover(msg):
    text = title_font.render(f"{msg}", True, RED)
    text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2))

    pygame.time.delay(500)

    if msg == "Clear!":
        clear_sound.play()
    else:
        gameover_sound.play()

    screen.fill(BLACK)  # 배경
    screen.blit(text, text_rect)  # gameover 메세지

    pygame.display.update()

    pygame.time.delay(2000)

while True:
    stage = startMenu() # 시작 메뉴 -> 난이도 선택
    if stage == None:   # 시작 메뉴에서 종료했으면
        break

    running = True

    player = Character()    # 캐릭터
    player.setPosition((screen_width - player.width) / 2, (screen_height - player.height) / 2)  # 캐릭터 초기 좌표 설정

    enemies = setEnemy(stage, player)   # 적 위치 설정

    items = []  # 화면에 있는 아이템

    total_time = 100  # 제한 시간
    start_ticks = pygame.time.get_ticks()  # 시작 시간

    gameover_msg = None

    while running:
        dt = clock.tick(30)

        # 2. 이벤트 처리 (키보드, 마우스 등)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            player.characterKeyEvent()

        player.characterMove()

        # 1%의 확률로 아이템 추가
        if random.randrange(100) == 0:
            items.append(Item())

        # 충돌 처리
        for e in enemies:
            player_rect = player.get_rect()  # 캐릭터
            enemy_rect = e.get_rect()  # 적
            # 캐릭터가 적과 닿으면
            if enemy_rect.colliderect(player_rect):
                if e.isCaught:
                    print("적 죽임")
                    e.killEnemy()
                else:
                    print("캐릭터가 적과 충돌")
                    running = False
                    gameover_msg = "Game Over"

            for i in items:
                item_rect = i.get_rect()
                # 적과 아이템이 닿으면
                if item_rect.colliderect(enemy_rect):
                    i.isRemaining = False

            for b in player.balloons:
                balloon_rect = b.get_rect()
                water_rect = b.getWaterRect()

                # 최초에 물풍선을 놓고 그 이후에 물풍선과 캐릭터가 충돌하면 캐릭터가 물풍선 위로 지나가지 못하게
                if balloon_rect.colliderect(player_rect) and not b.inCharacter:
                    player.reachBalloon(b)

                # 최초에 물풍선을 놓은 이후에 캐릭터가 물풍선을 벗어났는지
                if not balloon_rect.colliderect(player_rect):
                    b.inCharacter = False

                # 물줄기와 캐릭터가 닿으면
                if (player_rect.colliderect(water_rect[0]) or player_rect.colliderect(water_rect[1])) and b.isWater:
                    print("캐릭터가 물줄기와 충돌")
                    player.isCaught = True
                    gameover_msg = "Game Over"
                    running = False

                # 물줄기와 적이 닿으면
                if (enemy_rect.colliderect(water_rect[0]) or enemy_rect.colliderect(water_rect[1])) and b.isWater:
                    e.beCaught()
                    print("적이 물줄기와 충돌")

                # 적이 물풍선과 닿음
                if enemy_rect.colliderect(balloon_rect):
                    e.reachBalloon()

                for i in items:
                    item_rect = i.get_rect()
                    # 물줄기와 아이템이 닿으면
                    if (item_rect.colliderect(water_rect[0]) or item_rect.colliderect(water_rect[1])) and b.isWater:
                        i.isRemaining = False

        for i in items:
            player_rect = player.get_rect()
            item_rect = i.get_rect()
            # 캐릭터와 아이템이 닿으면
            if item_rect.colliderect(player_rect):
                i.upgradePlayer(player)

        if len(enemies) == 0:  # 모든 적을 다 죽이면 성공
            gameover_msg = "Clear!"
            running = False

        # 터진 물풍선 없애기
        player.balloons = [b for b in player.balloons if b.isRemaining]

        # 적 없애기
        enemies = [e for e in enemies if e.isAlive]

        # 아이템 없애기
        items = [i for i in items if i.isRemaining]

        # 5. 화면에 그리기
        screen.blit(background, (0, 0))  # 배경

        for e in enemies:  # 적
            e.showEnemy()

        for i in items: # 아이템
            i.showItem()

        for b in player.balloons:  # 물풍선
            b.showBalloon()

        player.displayCharacter()   # 플레이어

        # 경과 시간 계산
        elpased_time = (pygame.time.get_ticks() - start_ticks) / 1000  # ms -> s
        timer = menu_font.render("{}".format(int(total_time - elpased_time)), True, (255, 255, 255))
        timer_rect = timer.get_rect(center=(screen_width / 2, 40))

        screen.blit(timer, timer_rect)  # 남은 시간

        # 시간 초과했다면
        if total_time - elpased_time <= 0:
            gameover_msg = "Time Over"
            running = False

        if not running: # 시작 메뉴로 돌아가기
            if gameover_msg != None:
                pygame.display.update()
                gameover(gameover_msg)
            break

        pygame.display.update()

pygame.quit()
import logging
import time

import pygame

from colors import colors
from tetris import Tetris


# TODO 接下来的几个块的展示
# TODO 碰到一个块之后，即使移开了活动块，仍然会强制下落


class TetrisMain:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(lineno)d - %(message)s')

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    QING = (52, 233, 191)

    size = (400, 500)

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tetris")

        pygame.mixer.init()

        pygame.mixer.music.load(r'./resource/GameTheme.ogg')
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1, 0.0)
        # se_gameover = pygame.mixer.Sound(r'./resource/me_gameover.wav')
        se_start = pygame.mixer.Sound(r'./resource/ready.wav')
        self.se_go = pygame.mixer.Sound(r'./resource/go.wav')

        self.screen = pygame.display.set_mode(self.size)
        self.game = Tetris(10, 20, self)

        self.pressing_down = False
        self.pressing_down_lock = False
        self.endgame = False

        self.fps = 60

        self.at_bottom_moveable_time = 1
        self.tic = None
        self.at_bottom = False

    def run(self):
        clock = pygame.time.Clock()
        counter = 0

        # se_start.play()

        self.se_go.play()

        while not self.endgame:
            # only for the first tetromino
            if self.game.tetromino is None:
                self.game.new_figure()

            counter += 1
            if counter > 100000:
                counter = 0

            # controls the speed of down fall, changing game.level can change the speed

            if counter % (self.fps // self.game.level) == 0 or self.pressing_down:
                """
                game.go_down逻辑：
                尝试下落
                if 下落之后遇到阻挡
                    返回下落之前位置，并触发冻结延迟功能（在下落确认之前有短暂的时间让玩家仍可以进行移动和翻转）
                    确认之前可以移动的时间由movable_counter函数负责：
                        if counter可以使用(默认值)：
                            开始计时
                            counter状态置为不可使用
                        else（代表已经有一个conter在计时了）
                            测量已经经过的触底自由移动时间
                            if 时间未到限定值
                                return True（返回值为True时，调用freeze_delay,可以自由活动）
                            else
                                counter状态设为可以使用
                                return False（返回值为false时，不可以自由活动了，直接hard_drop)
                """
                if self.game.state == "start":
                    if self.game.go_down():
                        # start to count when first hit the ground or fixed tetromino
                        if not self.at_bottom:
                            self.tic = time.time()
                        self.at_bottom = True

            if self.tic is not None:
                if time.time() - self.tic > self.at_bottom_moveable_time:
                    self.game.hard_drop()
                    self.at_bottom = False
                    self.tic = None

            self.keyboard_event_handler()

            self.draw_field()

            self.draw_tetromino_shadow()

            self.draw_tetromino()

            self.draw_holden_tetetromino()

            self.draw_next_tetrominoes()

            self.draw_outerbound()

            font = pygame.font.SysFont('Calibri', 25, True, False)
            font1 = pygame.font.SysFont('Calibri', 65, True, False)
            text = font.render("Score: " + str(self.game.score), True, self.BLACK)
            text_game_over = font1.render("    YOU DIED", True, (200, 20, 20))

            self.screen.blit(text, [0, 0])
            if self.game.state == "gameover":
                self.screen.blit(text_game_over, [10, 200])
                pygame.mixer.music.stop()

            pygame.display.flip()
            clock.tick(self.fps)

        pygame.quit()

    def draw_outerbound(self):
        pygame.draw.rect(self.screen, self.BLACK, [self.game.x, self.game.y, self.game.grid_size * self.game.width,
                                                   self.game.grid_size * self.game.height], 3)

        pygame.draw.rect(self.screen, self.BLACK, [40, 60, 61, 60], 3)
        pygame.draw.rect(self.screen, self.BLACK, [299, 60, 50, 250], 3)

    def draw_holden_tetetromino(self):
        if self.game.holden_tetromino is not None:

            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in self.game.holden_tetromino.image():
                        pygame.draw.rect(self.screen, colors[self.game.holden_tetromino.color],
                                         [int(50 + self.game.grid_size * j * 0.5),
                                          int(80 + self.game.grid_size * i * 0.5),
                                          int(self.game.grid_size * 0.5),
                                          int(self.game.grid_size * 0.5)])

    def draw_next_tetrominoes(self):
        if self.game.state == 'start':
            for counter, tetromino_obj in enumerate(self.game.next_tetromino_obj):
                for i in range(4):
                    for j in range(4):
                        p = i * 4 + j
                        if p in tetromino_obj.image():
                            pygame.draw.rect(self.screen, colors[tetromino_obj.color],
                                             [int(305 + self.game.grid_size*0.5 * j),
                                              int(70 + counter*40 + self.game.grid_size*0.5 * i),
                                              int(self.game.grid_size*0.5),
                                              int(self.game.grid_size*0.5)])

    def draw_tetromino(self):
        if self.game.tetromino is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in self.game.tetromino.image():
                        pygame.draw.rect(self.screen, colors[self.game.tetromino.color],
                                         [self.game.x + self.game.grid_size * (j + self.game.tetromino.pos_x) + 1,
                                          self.game.y + self.game.grid_size * (i + self.game.tetromino.pos_y) + 1,
                                          self.game.grid_size - 2, self.game.grid_size - 2])

    def draw_tetromino_shadow(self):
        if self.game.tetromino_shadow is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in self.game.tetromino_shadow.image():
                        pygame.draw.rect(self.screen, colors[self.game.tetromino_shadow.color],
                                         [self.game.x + self.game.grid_size * (
                                                 j + self.game.tetromino_shadow.pos_x) + 1,
                                          self.game.y + self.game.grid_size * (
                                                  i + self.game.tetromino_shadow.pos_y) + 1,
                                          self.game.grid_size - 2, self.game.grid_size - 2], 3)

    def draw_field(self):
        self.screen.fill(self.WHITE)

        for i in range(self.game.height):
            for j in range(self.game.width):
                pygame.draw.rect(self.screen, self.GRAY,
                                 [self.game.x + self.game.grid_size * j, self.game.y + self.game.grid_size * i,
                                  self.game.grid_size, self.game.grid_size], 1)

                if self.game.field[i][j] > -1:
                    pygame.draw.rect(self.screen, colors[self.game.field[i][j]],
                                     [self.game.x + self.game.grid_size * j + 1,
                                      self.game.y + self.game.grid_size * i + 1,
                                      self.game.grid_size - 2,
                                      self.game.grid_size - 1])

    def keyboard_event_handler(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.endgame = True
            if event.type == pygame.KEYDOWN and self.game.state == 'start':
                if event.key == pygame.K_j or event.key == pygame.K_UP:
                    self.game.rotate(True)
                if event.key == pygame.K_k:
                    self.game.rotate(False)
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.pressing_down = True
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.game.go_side(-1)
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.game.go_side(1)
                if event.key == pygame.K_SPACE:
                    self.game.hard_drop()
                if event.key == pygame.K_f:
                    self.game.hold_tetromino()
            if event.type == pygame.KEYUP and self.game.state == 'start':
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.pressing_down = False

    def bgm(self):
        """
        on/off and volume
        """
        return True

    def se(self):
        """
        on/off and volume
        """
        return True

    def console_mode(self):
        pass


if __name__ == '__main__':
    main = TetrisMain()
    main.run()

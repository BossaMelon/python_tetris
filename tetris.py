import copy
import random
import time

import pygame

from rotate_system.rotate_srs import SRS
from tetromino import Tetromino

pygame.mixer.init()

se_tetris = pygame.mixer.Sound(r'./resource/se_tetris.wav')
se_single = pygame.mixer.Sound(r'./resource/se_single.wav')
se_double = pygame.mixer.Sound(r'./resource/se_double.wav')
se_triple = pygame.mixer.Sound(r'./resource/se_triple.wav')

se_harddrop = pygame.mixer.Sound(r'./resource/se_harddrop.wav')
se_freeze = pygame.mixer.Sound(r'./resource/se_freeze.wav')
se_rotate = pygame.mixer.Sound(r'./resource/se_rotate.wav')
se_move = pygame.mixer.Sound(r'./resource/se_move.wav')
se_hold = pygame.mixer.Sound(r'./resource/se_hold.wav')


class Tetris:

    def __init__(self, width, height, game_main):
        """
        Create a Tetris game instance which contains the game rule and logic.
        Construct with the height and width of the field
        """
        # better set from 1 to 20
        self.level = 1
        self.score = 0
        self.state = "start"
        self.field = []
        # x coordinate of the left upper corner
        self.x = 100
        # y coordinate of the left upper corner
        self.y = 60
        self.grid_size = 20

        self.height = height
        self.width = width

        # maintain a list that determines what tetromino comes next
        self._next_tetromino_list = random.sample(range(0, 7), 7)

        # tetromino comes in group of 7 with random order
        self._backup_tetromino_list = []

        self.next_tetromino_obj = None

        self._game_main = game_main

        # field of tetris game, here 20x10
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(-1)
            self.field.append(new_line)

        self.tetromino = None
        self.tetromino_shadow = None
        self.rotate_system = None

        self.can_hold = True
        self.holden_tetromino = None

    def new_figure(self):
        """
        bring the next tetromino into the field
        """
        self.tetromino = Tetromino(3, 0, self.get_next_tetromino_index())
        self.update_next()
        self.can_hold = True
        self.update_shadow()

    def update_next(self):
        self.next_tetromino_obj = [Tetromino(None, None, i) for i in self._next_tetromino_list]
        self.next_tetromino_obj.reverse()
        self.next_tetromino_obj = self.next_tetromino_obj[0:6]

    def hold_tetromino(self):
        if self.can_hold:
            if self.holden_tetromino is None:
                self.holden_tetromino = self.tetromino
                self.holden_tetromino.rotation = 0
                self.tetromino = Tetromino(3, 0, self.get_next_tetromino_index())
                self.update_next()
            else:
                self.holden_tetromino, self.tetromino = self.tetromino, self.holden_tetromino
                self.holden_tetromino.rotation = 0

            self.holden_tetromino.pos_y = 0
            self.tetromino.pos_y = 0
            self.update_shadow()
            se_hold.play()
            self.can_hold = False

    def _tetrimino_index_to_name(self, index_list):
        tetrimino_name_list = ['I', 'J', 'L', 'T', 'S', 'Z', 'O']
        return [tetrimino_name_list[i] for i in index_list][0:6]

    def check_intersect(self, shadow=False):
        """
        check whether the tetromoni hits the ground or intersected by another one
        :return: true/false
        """

        check_object = self.tetromino_shadow if shadow else self.tetromino

        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in check_object.image():
                    outbound_bottom = (i + check_object.pos_y) - (self.height - 1)
                    outbound_right = (j + check_object.pos_x) - (self.width - 1)
                    outbound_left = j + check_object.pos_x
                    if outbound_bottom > 0 or outbound_right > 0 or outbound_left < 0 or \
                            self.field[i + check_object.pos_y][j + check_object.pos_x] > -1:
                        intersection = True
                        break
        return intersection

    def levelup(self):
        if self.score > 5:
            self.level = 2

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            holes = 0
            for j in range(self.width):
                if self.field[i][j] == -1:
                    holes += 1
            if holes == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score += lines
        self.levelup()
        if lines == 1:
            se_single.play()
        elif lines == 2:
            se_double.play()
        elif lines == 3:
            se_triple.play()
        elif lines == 4:
            se_tetris.play()

    def hard_drop(self, sound=True):
        """
        when press hard drop, first check intersect then drop
        :return:
        """
        while not self.check_intersect():
            self.tetromino.pos_y += 1
        self.tetromino.pos_y -= 1
        self.freeze()
        if sound:
            se_harddrop.play()

    def go_down(self):
        self.tetromino.pos_y += 1

        if self.check_intersect():
            self.tetromino.pos_y -= 1
            return True
        return False

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.tetromino.image():
                    self.field[i + self.tetromino.pos_y][j + self.tetromino.pos_x] = self.tetromino.color
        self.break_lines()
        self.new_figure()
        se_freeze.play()
        if self.check_intersect():
            self.state = "gameover"
        self._game_main.pressing_down_lock = False

    def go_side(self, dx):
        old_x = self.tetromino.pos_x
        self.tetromino.pos_x += dx
        if self.check_intersect():
            self.tetromino.pos_x = old_x
        else:
            se_move.play()
            self.update_shadow()

    def update_shadow(self):
        self.tetromino_shadow = copy.deepcopy(self.tetromino)
        # self.tetromino_shadow.color = 7
        while not self.check_intersect(shadow=True):
            self.tetromino_shadow.pos_y += 1
        self.tetromino_shadow.pos_y -= 1

    def rotate(self, clockwise=True):
        old_rotation = self.tetromino.rotation
        old_pos_x = self.tetromino.pos_x
        old_pos_y = self.tetromino.pos_y

        srs = SRS(self.tetromino, clockwise=clockwise)
        rotatelist = srs.check_rotate()

        for rotate_bias in rotatelist:
            # print(rotate_bias)
            # print(self.tetromino.name)

            self.tetromino.rotate_clockwise() if clockwise else self.tetromino.rotate_anticlockwise()
            self.tetromino.pos_x += rotate_bias[0]
            self.tetromino.pos_y += rotate_bias[1]
            if not self.check_intersect():
                se_rotate.play()
                self.update_shadow()
                return
            self.tetromino.rotation = old_rotation
            self.tetromino.pos_x = old_pos_x
            self.tetromino.pos_y = old_pos_y

    def get_next_tetromino_index(self):
        if not self._backup_tetromino_list:
            self._backup_tetromino_list = list(range(7))
            random.shuffle(self._backup_tetromino_list)
        self._next_tetromino_list.insert(0, self._backup_tetromino_list.pop())
        return self._next_tetromino_list.pop()


if __name__ == '__main__':
    dgame = Tetris(10, 20)
    print()
    tic = time.time()

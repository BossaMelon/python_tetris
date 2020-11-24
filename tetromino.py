from colors import colors
import random


class Tetromino:
    tetrimino_name_list = ['I', 'J', 'L', 'T', 'S', 'Z', 'O']
    figures = [
        # shape I: light blue
        [[4, 5, 6, 7], [2, 6, 10, 14], [8, 9, 10, 11], [1, 5, 9, 13]],

        # shape J: blue
        [[0, 4, 5, 6], [1, 2, 5, 9], [4, 5, 6, 10], [1, 5, 8, 9]],

        # shape L: orange
        [[2, 4, 5, 6], [1, 5, 9, 10], [4, 5, 6, 8], [0, 1, 5, 9]],

        # shape T: purple
        [[1, 4, 5, 6], [1, 5, 6, 9], [4, 5, 6, 9], [1, 4, 5, 9]],

        # shape S: green
        [[1, 2, 4, 5], [1, 5, 6, 10], [5, 6, 8, 9], [0, 4, 5, 9]],

        # shape Z: red
        [[0, 1, 5, 6], [2, 5, 6, 9], [4, 5, 9, 10], [1, 4, 5, 8]],

        # shape O: yellow
        [[1, 2, 5, 6], [1, 2, 5, 6], [1, 2, 5, 6], [1, 2, 5, 6]],

    ]

    def __init__(self, x, y, tetromino_index):
        """
        init with start position of the screen
        :param x: leftup corner x coordinate
        :param y: left-up corner y coordinate
        :param tetromino_index: 0-7 stands for 7 tetrominoes
        """
        self.pos_x = x
        self.pos_y = y

        self.index = tetromino_index
        self.color = tetromino_index
        self.rotation = 0
        self.name = self.tetrimino_name_list[tetromino_index]

    def image(self):
        return self.figures[self.index][self.rotation % 4]

    def rotate_clockwise(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.index])

    def rotate_anticlockwise(self):
        self.rotation = (self.rotation - 1) % len(self.figures[self.index])

    def __str__(self):
        return self.name


if __name__ == '__main__':
    f = Tetromino(1, 2, 6)

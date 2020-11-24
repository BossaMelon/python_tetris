from tetromino import Tetromino


class SRS:
    # TODO anti clockwise
    # coordinate origin in left up corner
    wall_kick_JLSTZ_clockwise = (((0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)),
                                 ((0, 0), (1, 0), (1, 1), (0, -2), (1, -2)),
                                 ((0, 0), (1, 0), (1, -1), (0, 2), (1, 2)),
                                 ((0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)))

    wall_kick_I_clockwise = (((0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)),
                             ((0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)),
                             ((0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)),
                             ((0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)))

    wall_kick_JLSTZ = {'clockwise': wall_kick_JLSTZ_clockwise, 'anticlockwise': wall_kick_JLSTZ_clockwise}
    wall_kick_I = {'clockwise': wall_kick_I_clockwise, 'anticlockwise': wall_kick_I_clockwise}

    wall_kick_table = {'J': wall_kick_JLSTZ,
                       'L': wall_kick_JLSTZ,
                       'S': wall_kick_JLSTZ,
                       'T': wall_kick_JLSTZ,
                       'Z': wall_kick_JLSTZ,
                       'I': wall_kick_I}

    def __init__(self, tetromino, clockwise=True):
        self.tetromino = tetromino
        # clockwise or anticlockwise
        self.rotate_direction = 'clockwise' if clockwise is True else 'anticlockwise'

    def check_rotate(self):
        if self.tetromino.name == 'O':
            return (0, 0),
        return self.wall_kick_table[self.tetromino.name][self.rotate_direction][self.tetromino.rotation]


if __name__ == '__main__':
    s = SRS(tetromino=Tetromino(3, 0, 2))
    a = s.check_rotate()
    print(a)

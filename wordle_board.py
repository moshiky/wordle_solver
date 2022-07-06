from log_utils import log


class WordleBoard:

    def __init__(self):
        self._game_board = list()

    def init(self):
        self.__init__()

    def update(self, player_guess: str, judgment: str):
        self._game_board.append(judgment)
        self._game_board.append(player_guess)

    def visualize(self):
        log('--- Current board state ---')
        for idx in range(int(len(self._game_board) / 2)):
            log(self._game_board[2 * idx])
            log(self._game_board[2 * idx + 1])
            log('')

    def is_game_over(self):
        if len(self._game_board) == 0:
            return False

        return (len(self._game_board) >= 12) or self.is_it_a_win()

    def is_it_a_win(self):
        return self._game_board[-2] == 'VVVVV'

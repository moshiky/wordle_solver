from utils import log
from wordle_board import WordleBoard
from wordle_player import WordlePlayer
from wordle_judge import WordleJudge


class GameManager:

    def __init__(self, word_list: list, player: WordlePlayer, judge: WordleJudge, game_board: WordleBoard):
        self._player = player
        self._judge = judge
        self._game_board = game_board
        self._word_list = word_list

        self.init_game()

    def init_game(self):
        self._player.init(self._word_list)
        self._judge.init(self._word_list)
        self._game_board.init()

    def run(self):

        while not self._game_board.is_game_over():
            player_guess = self._player.guess()
            judgment = self._judge.judge(player_guess)
            self._player.update(judgment)
            self._game_board.update(player_guess, judgment)
            self._game_board.visualize()

        if self._game_board.is_it_a_win():
            log('You WON!!')
        else:
            log('Maybe next time..')
            log(self._judge.get_reveal_message())

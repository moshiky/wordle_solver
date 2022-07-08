from log_utils import log
from wordle_board import WordleBoard
from wordle_player import WordlePlayer
from wordle_judge import WordleJudge
from wordle_solver import WordleSolver


class GameManager:

    def __init__(self, word_list: list, player: WordlePlayer, judge: WordleJudge, solver: WordleSolver,
                 game_board: WordleBoard):

        self._word_list = word_list

        self._player = player
        self._judge = judge
        self._game_board = game_board
        self._solver = solver

    def init_game(self):
        self._player.init()
        self._judge.init()
        self._game_board.init()
        self._solver.init()

    def run(self):

        while not self._game_board.is_game_over():
            solver_tip = self._solver.get_tip()
            player_guess = self._player.guess(solver_tip)

            judgment = self._judge.judge(player_guess)

            self._player.update(judgment)
            self._solver.update(player_guess, judgment)

            self._game_board.update(player_guess, judgment)
            self._game_board.visualize()

        if self._game_board.is_it_a_win():
            guesses_to_win = self._game_board.count_turns_so_far()
            log(f'You WON!! it took {guesses_to_win} guesses to win')
            return guesses_to_win

        else:
            log('Maybe next time..')
            log(self._judge.get_reveal_message())
            return 0

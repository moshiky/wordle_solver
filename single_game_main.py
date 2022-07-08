
import sys
import matplotlib.pyplot as plt

from game_manager import GameManager
from factory import get_player, get_judge, get_solver
from log_utils import log
from utils import load_word_list
from wordle_board import WordleBoard


def main(word_list_file_path: str, player_type: str, judge_type: str, solver_type: str, num_runs_param: str):

    # load word list
    word_list = load_word_list(word_list_file_path)

    # construct player
    player = get_player(player_type, word_list)

    # construct judge
    judge = get_judge(judge_type, word_list)

    # construct solver
    solver = get_solver(solver_type, word_list)

    # construct game board
    game_board = WordleBoard()

    # construct game manager
    game_manager = GameManager(word_list, player, judge, solver, game_board)

    # start game
    num_runs = int(num_runs_param.split('=')[1])

    game_stats_list = list()
    for game_id in range(num_runs):
        log(f'### Start game: {game_id+1}/{num_runs}')
        game_manager.init_game()
        game_stats_list.append(game_manager.run())

    # visualize results
    plt.hist(game_stats_list)
    plt.show()


if __name__ == '__main__':
    main(*sys.argv[1:])

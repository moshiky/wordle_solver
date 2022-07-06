
import sys

from game_manager import GameManager
from utils import load_word_list, get_player, get_judge
from wordle_board import WordleBoard


def main(word_list_file_path: str, player_type: str, judge_type: str):

    # load word list
    word_list = load_word_list(word_list_file_path)

    # construct player
    player = get_player(player_type, word_list)

    # construct judge
    judge = get_judge(judge_type, word_list)

    # construct game board
    game_board = WordleBoard()

    # construct game manager
    game_manager = GameManager(word_list, player, judge, game_board)

    # start game
    game_manager.run()


if __name__ == '__main__':
    main(*sys.argv[1:])


from online_game_judge import OnlineGameJudge
from simulated_game_judge import SimulatedGameJudge
from user_player import UserPlayer
from wordle_judge import WordleJudge
from wordle_player import WordlePlayer


def get_player(player_type: str, word_list: list) -> WordlePlayer:
    if player_type == 'user':
        return UserPlayer(word_list)
    else:
        raise Exception(f'Unknown player type: {player_type}')


def get_judge(judge_type: str, word_list: list) -> WordleJudge:
    if judge_type == 'online_game':
        return OnlineGameJudge(word_list)
    elif judge_type == 'simulated_game':
        return SimulatedGameJudge(word_list)
    else:
        raise Exception(f'Unknown judge type: {judge_type}')

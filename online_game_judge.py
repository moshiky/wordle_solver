from log_utils import log
from wordle_judge import WordleJudge


class OnlineGameJudge(WordleJudge):

    def init(self):
        # do nothing
        pass

    def judge(self, player_guess: str):
        log('Please enter game judgment:')
        game_judgment = input()
        while not self._is_input_valid(game_judgment):
            log('Input invalid, please try again.')
            game_judgment = input()
        return game_judgment

    @staticmethod
    def _is_input_valid(input_string: str):
        return (input_string.replace('*', '').replace('V', '').replace('~', '')) == ''

    def get_reveal_message(self):
        return 'Check online game to see hidden word.'

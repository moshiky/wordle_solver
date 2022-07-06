from utils import log
from wordle_player import WordlePlayer


class UserPlayer(WordlePlayer):

    def guess(self):
        log('Please enter your guess:')
        user_guess = input()
        while not self._is_input_valid(user_guess):
            log('Input invalid, please try again.')
            user_guess = input()
        return user_guess.upper()

    @staticmethod
    def _is_input_valid(user_input: str):
        return user_input.isalpha() and len(user_input) == 5

    def update(self, judgment: str):
        # nothing to do
        pass

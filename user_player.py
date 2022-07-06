from log_utils import log
from wordle_player import WordlePlayer


class UserPlayer(WordlePlayer):

    def guess(self):
        log('Please enter your guess:')
        user_guess = input()
        while not self._is_input_valid(user_guess) or not self._is_valid_word(user_guess):
            if not self._is_input_valid(user_guess):
                log('Input invalid, please try again.')

            if not self._is_valid_word(user_guess):
                log('Word not in word list, please try again.')

            user_guess = input()

        return user_guess.upper()

    def init(self):
        pass

    @staticmethod
    def _is_input_valid(user_input: str):
        return user_input.isalpha() and len(user_input) == 5

    def _is_valid_word(self, user_input: str):
        return user_input in self._word_list

    def update(self, judgment: str):
        # nothing to do
        pass

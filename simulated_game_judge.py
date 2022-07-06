import numpy as np

from utils import find_all
from wordle_judge import WordleJudge


class SimulatedGameJudge(WordleJudge):

    def __init__(self, word_list: list):
        super().__init__(word_list)
        self._hidden_word = None
        self.init()

    def init(self):
        # select random hidden word
        self._hidden_word = np.random.choice(self._word_list)

    def judge(self, player_guess: str):
        return SimulatedGameJudge.judge_for_hidden_word(player_guess, self._hidden_word)

    @staticmethod
    def judge_for_hidden_word(player_guess: str, hidden_word: str) -> str:
        # init state
        judgment_str_list = [''] * len(hidden_word)
        letters_to_find = [l for l in hidden_word]
        found_idxs = list()

        # look for letters in place
        for letter_idx, letter in enumerate(player_guess):
            valid_letter_idxs = find_all(hidden_word, letter)
            if letter_idx in valid_letter_idxs:
                judgment_str_list[letter_idx] = 'V'
                letters_to_find.remove(letter)
                found_idxs.append(letter_idx)

        # look for other letters
        for letter_idx, letter in enumerate(player_guess):
            if letter_idx in found_idxs:
                continue

            elif letter in letters_to_find:
                judgment_str_list[letter_idx] = '~'

            else:
                judgment_str_list[letter_idx] = '*'

        return ''.join(judgment_str_list)

    def get_reveal_message(self):
        return f'The hidden word was: {self._hidden_word}'

import os
import time
from multiprocessing import Pool

import numpy as np
from tqdm import tqdm

from log_utils import log
from simulated_game_judge import SimulatedGameJudge
from utils import find_all
from wordle_solver import WordleSolver


class ValidWordsStatsSolver(WordleSolver):

    def __init__(self, word_list: list, use_pool: bool = True, log_run_time: bool = False):
        super().__init__(word_list)

        self._valid_words = None
        self._found_letter_idxs = None
        self._letter_min_count = None
        self._letters_to_filter = None
        self._letter_idx_filter = None
        self._guess_history = None

        self._use_pool = use_pool
        self._log_run_time = log_run_time

        self.init()

    def init(self):
        # init members
        self._valid_words = self._word_list.copy()
        self._found_letter_idxs = list()
        self._letter_min_count = dict()
        self._letters_to_filter = list()
        self._letter_idx_filter = list()
        self._guess_history = set()

    def get_tip(self) -> str:

        # get best guess
        log('Computing tip..')
        start_time = time.time()
        best_guess = self._get_best_guess()
        if self._log_run_time:
            log(f'compute time: {time.time() - start_time:.2f} seconds')

        return best_guess

    def update(self, player_guess: str, judgment: str):
        # update clues
        ValidWordsStatsSolver.update_clues(
            player_guess,
            judgment,
            self._found_letter_idxs,
            self._letter_min_count,
            self._letters_to_filter,
            self._letter_idx_filter,
            self._guess_history
        )

        # update valid words
        self._valid_words = \
            ValidWordsStatsSolver._filter_words_by_hints(
                self._valid_words,
                self._found_letter_idxs,
                self._letter_min_count,
                self._letters_to_filter,
                self._letter_idx_filter,
                self._guess_history
            )

    @staticmethod
    def update_clues(player_guess: str, judgment: str, found_letter_idxs: list, letter_min_count: dict,
                     letters_to_filter: list, letter_idx_filter: list, guess_history: set):

        # join current guess to guess history
        guess_history.add(player_guess)

        # use judgment string to update the clues
        letter_counter = dict()
        for marking_idx, marking in enumerate(judgment):
            curr_letter = player_guess[marking_idx]
            if marking == 'V':
                info_tuple = (curr_letter, marking_idx)
                if info_tuple not in found_letter_idxs:
                    found_letter_idxs.append(info_tuple)

                letter_counter[curr_letter] = \
                    1 if curr_letter not in letter_counter.keys() else letter_counter[curr_letter] + 1

        marked_letters = list()
        for marking_idx, marking in enumerate(judgment):
            curr_letter = player_guess[marking_idx]
            if marking == '~':
                info_tuple = (curr_letter, marking_idx)
                if info_tuple not in letter_idx_filter:
                    letter_idx_filter.append(info_tuple)

                if curr_letter not in marked_letters:
                    letter_counter[curr_letter] = \
                        1 if curr_letter not in letter_counter.keys() else letter_counter[curr_letter] + 1
                    marked_letters.append(curr_letter)

            elif marking == '*':
                if curr_letter not in letters_to_filter and curr_letter not in set([x[0] for x in found_letter_idxs]):
                    letters_to_filter.append(curr_letter)

        # update letter counters
        for letter, letter_count in letter_counter.items():
            if letter not in letter_min_count.keys():
                letter_min_count[letter] = 0
            letter_min_count[letter] = max(letter_min_count[letter], letter_count)

    @staticmethod
    def _filter_words_by_hints(word_list: list, found_letter_idxs: list, letter_min_count: dict,
                               letters_to_filter: list, letter_idx_filter: list, guess_history: set):

        # duplicate input word list
        new_word_list = list()

        # iterate words
        for word in set(word_list) - set(guess_history):

            # enforce filter hints
            is_valid_word = True
            for letter in letters_to_filter:
                if letter in word:
                    is_valid_word = False
                    break

            if not is_valid_word:
                continue

            # enforce letter idx filter hints
            for letter, investigated_idx in letter_idx_filter:
                if word[investigated_idx] == letter:
                    is_valid_word = False
                    break

            if not is_valid_word:
                continue

            # enforce found letters hints
            for letter, expected_idx in found_letter_idxs:
                if word[expected_idx] != letter:
                    is_valid_word = False
                    break

            if not is_valid_word:
                continue

            # enforce letter count hints
            for letter, expected_min_count in letter_min_count.items():
                if len(find_all(word, letter)) < expected_min_count:
                    is_valid_word = False
                    break

            if not is_valid_word:
                continue
            else:
                # in case got here - this word is valid
                new_word_list.append(word)

        return new_word_list

    @staticmethod
    def thread_func__test_single_word(guess_word, valid_words, found_letter_idxs: list, letter_min_count: dict,
                                      letters_to_filter: list, letter_idx_filter: list, guess_history: set):
        # init statistics list
        stats_list = list()

        # iterate all possible hidden words
        curr_guess_history = guess_history.copy()
        for hidden_word in valid_words:

            # produce judgment - given the guess_word and assuming hidden word is hidden_word
            judgment = SimulatedGameJudge.judge_for_hidden_word(guess_word, hidden_word)

            # duplicate clues
            curr_found_letter_idxs = found_letter_idxs.copy()
            curr_letter_min_count = letter_min_count.copy()
            curr_letters_to_filter = letters_to_filter.copy()
            curr_letter_idx_filter = letter_idx_filter.copy()

            # update clues according to judgment
            ValidWordsStatsSolver.update_clues(
                guess_word,
                judgment,
                curr_found_letter_idxs,
                curr_letter_min_count,
                curr_letters_to_filter,
                curr_letter_idx_filter,
                curr_guess_history
            )

            # calculate left valid words
            curr_valid_words = \
                ValidWordsStatsSolver._filter_words_by_hints(
                    valid_words, curr_found_letter_idxs, curr_letter_min_count, curr_letters_to_filter,
                    curr_letter_idx_filter, curr_guess_history
                )

            stats_list.append(len(curr_valid_words))

        return guess_word, np.mean(stats_list)

    def _get_best_guess(self):
        if len(self._valid_words) == len(self._word_list):
            # {'ARISE': 63.47, 'AROSE': 65.76, 'IRATE': 63.46, 'RAISE': 60.69}
            best_initial_words = ['ARISE', 'RAISE', 'AROSE', 'IRATE']
            return np.random.choice(best_initial_words)

        elif len(self._valid_words) == 1:
            return self._valid_words[0]

        # prepare params for parallel execution
        thread_param_list = [
            [
                word,
                self._valid_words.copy(),
                self._found_letter_idxs,
                self._letter_min_count,
                self._letters_to_filter,
                self._letter_idx_filter,
                self._guess_history
            ]
            for word in self._valid_words
        ]

        # create pool
        if self._use_pool:
            pool = Pool(processes=os.cpu_count() - 2)
            word_stats_items = pool.starmap(ValidWordsStatsSolver.thread_func__test_single_word, thread_param_list)
            pool.close()
            pool.join()

        else:
            pool = None
            word_stats_items = list()
            for param_arr in tqdm(thread_param_list):
                word_stats_items.append(ValidWordsStatsSolver.thread_func__test_single_word(*param_arr))

        # sort results
        sorted_words = sorted(word_stats_items, key=lambda item: item[1])

        if self._use_pool:
            pool.terminate()
            del pool

        # look for optimal word to suggest
        best_score = sorted_words[0][1]
        similar_scored_words = [word for word, score in word_stats_items if score <= (best_score * 1.1)]
        if len(similar_scored_words) == 1:
            return similar_scored_words[0]

        # test against valid words
        sim_words_set = set(similar_scored_words)
        valid_words_set = set(self._valid_words)
        set_intersection = sim_words_set & valid_words_set
        if len(set_intersection) > 0:
            log(dict([x for x in word_stats_items if x[0] in set_intersection]))
            return np.random.choice(list(set_intersection))

        # otherwise, just return first word
        return sorted_words[0][0]

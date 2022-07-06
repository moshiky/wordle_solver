import os
import time
import numpy as np
import pandas as pd
import re
from multiprocessing import Pool
from tqdm import tqdm

IS_REAL = False
USE_POOL = True


def log(msg: str):
    print(f'[{time.ctime()}] >> {msg}')


def print_board(game_board):
    for idx in range(int(len(game_board) / 2)):
        log(game_board[2 * idx])
        log(game_board[2 * idx + 1])
        log(' ')


def find_all(long_str, ch):
    return [m.start() for m in re.finditer(ch, long_str)]


def update_board_and_hints(hidden_word, last_input_word, game_board, found_letter_idxs: list, letter_min_count: dict,
                           letters_to_filter: list, letter_idx_filter: list, hint_str: str = None):

    # calculate hint string
    if hint_str is None:
        hint_str_list = [''] * len(hidden_word)
        letters_to_find = [l for l in hidden_word]
        found_idxs = list()
        for letter_idx, letter in enumerate(last_input_word):
            valid_letter_idxs = find_all(hidden_word, letter)
            if letter_idx in valid_letter_idxs:
                hint_str_list[letter_idx] = 'V'
                letters_to_find.remove(letter)
                found_idxs.append(letter_idx)

        for letter_idx, letter in enumerate(last_input_word):
            if letter_idx in found_idxs:
                continue

            elif letter in letters_to_find:
                hint_str_list[letter_idx] = '~'

            else:
                hint_str_list[letter_idx] = '*'

        hint_str = ''.join(hint_str_list)

    # use hint string to update the hints
    letter_counter = dict()
    for marking_idx, marking in enumerate(hint_str):
        curr_letter = last_input_word[marking_idx]
        if marking == 'V':
            info_tuple = (curr_letter, marking_idx)
            if info_tuple not in found_letter_idxs:
                found_letter_idxs.append(info_tuple)

            letter_counter[curr_letter] = \
                1 if curr_letter not in letter_counter.keys() else letter_counter[curr_letter] + 1

    marked_letters = list()
    for marking_idx, marking in enumerate(hint_str):
        curr_letter = last_input_word[marking_idx]
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

    # update game board
    game_board.append(hint_str)
    game_board.append(last_input_word)


def thread_func__test_single_word(guess_word, valid_words, found_letter_idxs: list, letter_min_count: dict,
                                  letters_to_filter: list, letter_idx_filter: list):
    stats_list = list()
    for hidden_word in valid_words:

        curr_found_letter_idxs = found_letter_idxs.copy()
        curr_letter_min_count = letter_min_count.copy()
        curr_letters_to_filter = letters_to_filter.copy()
        curr_letter_idx_filter = letter_idx_filter.copy()

        update_board_and_hints(
            hidden_word, guess_word, list(), curr_found_letter_idxs, curr_letter_min_count, curr_letters_to_filter,
            curr_letter_idx_filter)

        curr_valid_words = \
            filter_words_by_hints(valid_words, curr_found_letter_idxs, curr_letter_min_count, curr_letters_to_filter,
                                  curr_letter_idx_filter)

        stats_list.append(len(curr_valid_words))

    return guess_word, np.mean(stats_list)


def get_best_guess(word_list, valid_words, found_letter_idxs: list, letter_min_count: dict, letters_to_filter: list,
                   letter_idx_filter: list):
    if len(valid_words) == len(word_list):
        return 'RAISE'

    elif len(valid_words) == 1:
        return valid_words[0]

    # prepare params for parallel execution
    thread_param_list = [
        [
            word,
            valid_words.copy(),
            found_letter_idxs,
            letter_min_count,
            letters_to_filter,
            letter_idx_filter
        ]
        for word in word_list
    ]

    # create pool
    if USE_POOL:
        pool = Pool(processes=os.cpu_count() - 2)
        word_stats_items = pool.starmap(thread_func__test_single_word, thread_param_list)
        pool.close()
        pool.join()

    else:
        word_stats_items = list()
        for param_arr in tqdm(thread_param_list):
            word_stats_items.append(thread_func__test_single_word(*param_arr))

    # sort results
    sorted_words = sorted(word_stats_items, key=lambda item: item[1])

    if USE_POOL:
        pool.terminate()
        del pool

    # look for optimal word to suggest
    best_score = sorted_words[0][1]
    similar_scored_words = [word for word, score in word_stats_items if score <= (best_score * 1.1)]
    if len(similar_scored_words) == 1:
        return similar_scored_words[0]

    # test against valid words
    sim_words_set = set(similar_scored_words)
    valid_words_set = set(valid_words)
    set_intersection = sim_words_set & valid_words_set
    if len(set_intersection) > 0:
        return dict([x for x in word_stats_items if x[0] in set_intersection])

    # otherwise, just return first word
    return sorted_words[0][0]


def filter_words_by_hints(word_list: list, found_letter_idxs: list, letter_min_count: dict, letters_to_filter: list,
                          letter_idx_filter: list):

    # duplicate input word list
    new_word_list = list()

    # iterate words
    for word in word_list:

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


def main():
    # load all words
    words_df = pd.read_csv('wordle_words.csv')
    word_list = words_df[words_df.columns[0]].values.tolist()
    word_list = [x.upper() for x in word_list]
    log(f'loaded {len(word_list)} words')

    # prepare wordle board
    game_board = list()
    found_letter_idxs = list()
    letter_min_count = dict()
    letters_to_filter = list()
    letter_idx_filter = list()

    # iterate
    if not IS_REAL:
        hidden_word = word_list[np.random.randint(0, len(word_list))]
        hidden_word = hidden_word.upper()
        log(f'The selected word is: {hidden_word}')
    else:
        hidden_word = 'N/A'

    valid_words = word_list.copy()
    last_input_word = None
    while len(game_board) == 0 or (len(game_board) < 12 and game_board[-2] != 'VVVVV'):

        # update valid words
        valid_words = \
            filter_words_by_hints(
                valid_words, found_letter_idxs, letter_min_count, letters_to_filter, letter_idx_filter)
        log(f'Total valid words: {len(valid_words)}')

        # suggest best word
        log('Calculating best guess..')
        start_time = time.time()
        best_word = \
            get_best_guess(
                word_list, valid_words, found_letter_idxs, letter_min_count, letters_to_filter, letter_idx_filter)
        log(f'compute time: {time.time() - start_time:.2f} seconds')

        # print suggestion
        log(f'I suggest: {best_word}')

        # receive input
        last_input_word = input('Your guess:  ').upper()
        while last_input_word not in word_list:
            if len(last_input_word) != 5:
                log('ERROR >> input word must be of 5 letters exactly')
            else:
                log('ERROR >> unknown word')
            last_input_word = input('Your guess: ').upper()

        # update board and hints
        if IS_REAL:
            log('Please provide game output:')
            game_output = input()

        else:
            game_output = None

        update_board_and_hints(hidden_word, last_input_word, game_board, found_letter_idxs, letter_min_count,
                               letters_to_filter, letter_idx_filter, game_output)

        # print board
        log('Current board state:')
        log('')
        print_board(game_board)

        log('-----------------------------------------')

    if game_board[-2] == 'VVVVV':
        log('YOU WON!!')
    elif not IS_REAL:
        log(f'Hidden word is: {hidden_word}')
    else:
        log('Check game to see hidden word')


if __name__ == '__main__':
    main()

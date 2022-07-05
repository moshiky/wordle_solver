import os
import numpy as np
import pandas as pd
import re
from tqdm import tqdm
from multiprocessing import Pool


is_real = False


def print_board(game_board):
    for idx in range(int(len(game_board) / 2)):
        print(game_board[2 * idx])
        print(game_board[2 * idx + 1])
        print(' ')


def find_all(long_str, ch):
    return [m.start() for m in re.finditer(ch, long_str)]


def update_board_and_hints(hidden_word, last_input_word, game_board, letter_hints):
    hint_str_list = [''] * len(hidden_word)
    letters_to_find = [l for l in hidden_word]
    found_idxs = list()
    for letter_idx, letter in enumerate(last_input_word):
        valid_letter_idxs = find_all(hidden_word, letter)
        if letter_idx in valid_letter_idxs:
            hint_str_list[letter_idx] = 'V'
            letter_hints[letter] = f'idx={letter_idx}'
            letters_to_find.remove(letter)
            found_idxs.append(letter_idx)

    for letter_idx, letter in enumerate(last_input_word):
        if letter in letter_hints.keys():
            existing_hint = letter_hints[letter]
        else:
            existing_hint = ''

        if letter_idx in found_idxs:
            continue

        elif letter in letters_to_find:
            hint_str_list[letter_idx] = '~'

            if existing_hint == '':
                letter_hints[letter] = f'exists'

        else:
            hint_str_list[letter_idx] = '*'

            if existing_hint == '':
                letter_hints[letter] = f'filter'

    game_board.append(''.join(hint_str_list))
    game_board.append(last_input_word)


def thread_func__test_single_word(guess_word, valid_words, letter_hints):
    stats_list = list()
    for hidden_word in valid_words:
        curr_letter_hints = letter_hints.copy()
        update_board_and_hints(hidden_word, guess_word, list(), curr_letter_hints)
        curr_valid_words = filter_words_by_hints(valid_words, curr_letter_hints)
        stats_list.append(len(curr_valid_words))

    return guess_word, np.mean(stats_list)


def get_best_guess(word_list, valid_words, letter_hints: dict):
    if len(letter_hints.keys()) == 0:
        return 'RAISE'
    elif len(valid_words) == 1:
        return valid_words[0]

    # prepare params for parallel execution
    thread_param_list = [
        [
            word,
            valid_words.copy(),
            letter_hints
        ]
        for word in word_list
    ]

    # create pool
    pool = Pool(processes=os.cpu_count() - 2)
    word_stats_items = pool.starmap(thread_func__test_single_word, thread_param_list)
    pool.close()
    pool.join()

    # sort results
    sorted_words = sorted(word_stats_items, key=lambda item: item[1])
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
        return set_intersection

    # otherwise, just return first word
    return sorted_words[0][0]


def filter_words_by_hints(word_list: list, letter_hint_dict: dict):

    word_list = word_list.copy()
    for letter, hint in letter_hint_dict.items():
        if hint.startswith('idx'):
            expected_letter_idx = int(hint.split('=')[1])
            word_list = [w for w in word_list if w[expected_letter_idx] == letter]

        elif hint == 'exists':
            word_list = [w for w in word_list if letter in w]

        else:
            word_list = [w for w in word_list if letter not in w]

    return word_list


def main():
    # load all words
    words_df = pd.read_csv('wordle_words.csv')
    word_list = words_df[words_df.columns[0]].values.tolist()
    word_list = [x.upper() for x in word_list]
    print(f'loaded {len(word_list)} words')

    # prepare wordle board
    game_board = list()
    letter_hints = dict()   # one record for each letter. possible values: filter | exists | idx={#}

    # iterate
    if not is_real:
        hidden_word = word_list[np.random.randint(0, len(word_list))]
        hidden_word = hidden_word.upper()
    else:
        hidden_word = 'N/A'

    valid_words = word_list.copy()
    last_input_word = ''
    while len(game_board) == 0 or (len(game_board) < 12 and game_board[-2] != 'VVVVV'):

        # update valid words
        valid_words = filter_words_by_hints(valid_words, letter_hints)
        print(f'Total valid words: {len(valid_words)}')

        # suggest best word
        print('Calculating best guess..')
        best_word = get_best_guess(word_list, valid_words, letter_hints)

        # print suggestion
        print(f'I suggest: {best_word}')

        # receive input
        last_input_word = input('Your guess:  ').upper()
        while last_input_word not in word_list:
            if len(last_input_word) != 5:
                print('ERROR >> input word must be of 5 letters exactly')
            else:
                print('ERROR >> unknown word')
            last_input_word = input('Your guess: ').upper()

        # update board and hints
        if is_real:
            print('Please provide game output:')
            game_output = input()
            for idx, marking in enumerate(game_output):
                if marking == 'V':
                    letter_hints[last_input_word[idx]] = f'idx={idx}'

            for idx, marking in enumerate(game_output):
                letter = last_input_word[idx]
                curr_hint = letter_hints[letter] if letter in letter_hints.keys() else ''
                if marking == '~' and curr_hint == '':
                    letter_hints[letter] = 'exists'
                elif marking == '*' and curr_hint == '':
                    letter_hints[letter] = 'filter'

            game_board.append(game_output)
            game_board.append(last_input_word)

        else:
            update_board_and_hints(hidden_word, last_input_word, game_board, letter_hints)

        # print board
        print('Current board state:')
        print('')
        print_board(game_board)

        print('-----------------------------------------')

    if game_board[-2] == 'VVVVV':
        print('YOU WON!!')
    elif not is_real:
        print(f'Hidden word is: {hidden_word}')
    else:
        print('Check game to see hidden word')


if __name__ == '__main__':
    main()

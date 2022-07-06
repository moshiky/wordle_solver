import re
import pandas as pd

from log_utils import log


def load_word_list(file_path: str) -> list:
    words_df = pd.read_csv(file_path)
    word_list = words_df[words_df.columns[0]].values.tolist()
    word_list = [x.upper() for x in word_list]
    log(f'loaded {len(word_list)} words')
    return word_list


def find_all(long_str, ch):
    return [m.start() for m in re.finditer(ch, long_str)]

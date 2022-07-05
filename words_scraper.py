
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm


def main():

    word_list = list()
    url = 'https://www.wordunscrambler.net/word-list/wordle-word-list'
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    all_a_tags = soup.findAll('a')
    for a_tag in tqdm(all_a_tags):
        if not a_tag.attrs['href'].startswith('/unscramble'):
            continue
        word_list.append(a_tag.text)

    name_df = pd.DataFrame({'word': word_list})
    name_df.to_csv('wordle_words_2.csv', index=False)


if __name__ == '__main__':
    main()

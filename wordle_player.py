
class WordlePlayer:

    def __init__(self, word_list: list):
        self._word_list = word_list

    def init(self):
        raise NotImplementedError()

    def guess(self):
        raise NotImplementedError()

    def update(self, judgment: str):
        raise NotImplementedError()

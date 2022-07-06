
class WordlePlayer:

    def __init__(self, word_list: list = None):
        self._is_ready = word_list is None
        self._word_list = word_list
        self._last_guess = None

    def init(self, word_list: list):
        self.__init__(word_list)

    def guess(self):
        raise NotImplementedError()

    def update(self, judgment: str):
        raise NotImplementedError()

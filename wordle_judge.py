
class WordleJudge:

    def __init__(self, word_list: list = None):
        self._is_ready = word_list is None
        self._word_list = word_list

    def init(self, word_list: list):
        self.__init__(word_list)

    def judge(self, player_guess: str):
        raise NotImplementedError()

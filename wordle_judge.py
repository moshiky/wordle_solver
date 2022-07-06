
class WordleJudge:

    def __init__(self, word_list: list = None):
        self._is_ready = word_list is None
        self._word_list = word_list

    def init(self):
        raise NotImplementedError()

    def judge(self, player_guess: str):
        raise NotImplementedError()

    def get_reveal_message(self):
        raise NotImplementedError()

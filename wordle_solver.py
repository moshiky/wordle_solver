
class WordleSolver:

    def __init__(self, word_list: list):
        self._word_list = word_list

    def init(self):
        raise NotImplementedError()

    def get_tip(self) -> str:
        raise NotImplementedError()

    def update(self, player_guess: str, judgment: str):
        raise NotImplementedError()

from log_utils import log
from wordle_player import WordlePlayer


class AutoPlayer(WordlePlayer):

    def guess(self, solver_tip: str = None):
        log(f'My guess is: {solver_tip}')
        return solver_tip

    def init(self):
        pass

    def update(self, judgment: str):
        # nothing to do
        pass

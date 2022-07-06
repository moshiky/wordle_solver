from wordle_solver import WordleSolver


class EmptySolver(WordleSolver):

    def init(self):
        pass

    def get_tip(self) -> str:
        return None

    def update(self, player_guess: str, judgment: str):
        pass

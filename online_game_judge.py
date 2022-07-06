from wordle_judge import WordleJudge


class OnlineGameJudge(WordleJudge):

    def judge(self, player_guess: str):
        print('Please enter game judgment:')
        game_judgment = input()
        while not self._is_input_valid(game_judgment):
            print('Input invalid, please try again.')
            game_judgment = input()
        return game_judgment

    @staticmethod
    def _is_input_valid(input_string: str):
        return (input_string.replace('*', '').replace('V', '').replace('~', '')) == ''

from modes.base_mode import BaseMode

class Dev(BaseMode):
    def mode_start(self, **kwargs):
        super().mode_start(**kwargs)
        self.add_mode_event_handler('dev_display_letters_awarded', self.display_letters_awarded)

    def display_letters_awarded(self, **kwargs):
        DEVOLVED = 'DEVOLVED'
        num_letters = self.machine.game.player['letters']

        row_one = 'LETTER!COLLECTED'.center(16, "!")
        row_two = (DEVOLVED[0:num_letters] + '_'*(len(DEVOLVED) - num_letters)).center(16, "!")
        self.display.set_vars(r1=row_one, r2=row_two)

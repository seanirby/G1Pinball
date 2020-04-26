from mpf.core.mode import Mode
from modes.display import Display

class Drops(Mode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mode_start(self, **kwargs):
        print('starting drops')
        self.printer = Display(self.machine, 'd_drops_1', 'd_drops_2')

    def mode_stop(self, **kwargs):
        print('stopping drops')

from mpf.core.mode import Mode
from modes.display import Display

class Drops(Mode):
    def __init__(self, *args, **kwargs):
        """Initialize bonus mode."""
        super().__init__(*args, **kwargs)
        # convenience for unit testing
        self._testing = False

    @property
    def testing(self):
        return self._testing

    @testing.setter
    def testing(self, x):
        self._testing = x

    def mode_start(self, **kwargs):
        self.printer = Display(self.machine, 'd_drops_1', 'd_drops_2')

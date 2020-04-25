from mpf.core.mode import Mode
from modes.display import Display

ROLLOVER_SHOT = 'sh_drops_rollover_button'
EVENT_HURRY_UP_ACTIVE_STARTED = 'drops_state_hurry_up_active_started'
EVENT_HURRY_UP_ACTIVE_STOPPED = 'drops_state_hurry_up_active_stopped'
STATE = 'drops'
STATE_HURRY_UP_ACTIVE = 'hurry_up_active'
STATE_HURRY_UP_INACTIVE = 'hurry_up_inactive'
ROLLOVER_SHOT_UNLIT_INDEX = 0
ROLLOVER_SHOT_LIT_INDEX = 1

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

        # state handlers
        self.add_mode_event_handler(EVENT_HURRY_UP_ACTIVE_STARTED, self.handle_hurry_up_active_started)
        self.add_mode_event_handler(EVENT_HURRY_UP_ACTIVE_STOPPED, self.handle_hurry_up_active_stopped)

    def handle_hurry_up_active_started(self, **kwargs):
        self.machine.shots[ROLLOVER_SHOT].jump(ROLLOVER_SHOT_LIT_INDEX)


    def handle_hurry_up_active_stopped(self, **kwargs):
        self.machine.shots[ROLLOVER_SHOT].jump(ROLLOVER_SHOT_UNLIT_INDEX)

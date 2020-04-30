from mpf.core.mode import Mode
from modes.display import Display

class BaseMode(Mode):
    def __init__(self, *args, **kwargs):
        super(BaseMode, self).__init__(*args, **kwargs)

    def mode_start(self, **kwargs):
        self.display = Display(self.machine, self.name)
        self.add_mode_event_handler('{}_display_flash'.format(self.name), self.display.flash)

        self.add_mode_event_handler('{0}_display_set_vars'.format(self.name), self.display.set_vars)
        self.add_mode_event_handler('{0}_display_set_vars_format'.format(self.name), self.display.set_vars_format)

    def mode_stop(self, **kwargs):
        pass


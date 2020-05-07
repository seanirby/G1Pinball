from mpf.core.mode import Mode
from modes.display import Display

class BaseMode(Mode):
    def __init__(self, *args, **kwargs):
        super(BaseMode, self).__init__(*args, **kwargs)

    def mode_start(self, **kwargs):
        super().mode_start(**kwargs)
        self.display = Display(self.machine, self.name)
        self.add_mode_event_handler('{}_display_flash'.format(self.name), self.display.flash)

        self.add_mode_event_handler('{0}_display_set_vars'.format(self.name), self.display.set_vars)
        self.add_mode_event_handler('{0}_display_set_vars_format'.format(self.name), self.display.set_vars_format)
        self.add_mode_event_handler('{0}_display_transition'.format(self.name), self.display_transition)
        self.add_mode_event_handler('{0}_display_set_masked'.format(self.name), self.display.set_masked)

    def mode_stop(self, **kwargs):
        super().mode_stop(**kwargs)

    def display_transition(self, **kwargs):
        # assign tick handler
        key = self.machine.events.add_handler('timer_base_transition_tick', self.display.transition_tick, self.priority, mode=self)

        # initialize our segment display manager
        self.display.transition_init(kwargs.get('r1'), kwargs.get('r2'), key)

        # kick things off
        self.machine.timers.base_transition.restart()
        # add in a fallback for removing our transition tick handler
        self.delay.add(2000, self.remove_transition_handler_fallback, None, transition_handler_key=key)

    def remove_transition_handler_fallback(self, **kwargs):
        key = kwargs.get('transition_handler_key')
        self.machine.events.remove_handler_by_key(key)

    
    

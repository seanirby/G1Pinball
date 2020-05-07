from mpf.core.mode import Mode

# we need a hardcoded list of all the things that can draw
# slides, that way we can listen for when they become active

ACTIVE_MODE_VAR = "d_active_mode"

SLIDES = [
    "base",
    "dev",
    "drops",
    "mball",
    "mystery",
    "song_award",
    "urge",
    ]

class SlideListener(Mode):
    def mode_start(self, **kwargs):
        self.add_mode_event_handler('timer_slide_listener_init_complete', self.save_active_display, slide="base")
        for slide in SLIDES:
            event = "slide_{}_active".format(slide)
            self.add_mode_event_handler(event, self.save_active_display, slide=slide)

    def save_active_display(self, **kwargs):
        slide = kwargs['slide']

        row_one_name = "d_{}_1".format(slide)
        row_two_name = "d_{}_2".format(slide)
        row_one = self.machine.variables.get_machine_var(row_one_name)
        row_two = self.machine.variables.get_machine_var(row_two_name)

        if bool(row_one) and bool(row_two):
            self.machine.variables.set_machine_var(ACTIVE_MODE_VAR, slide)
        else:
            self.machine.variables.set_machine_var(ACTIVE_MODE_VAR, 'base')
        

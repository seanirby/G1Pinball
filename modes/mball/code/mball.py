from modes.base_mode import BaseMode

class Multiball(BaseMode):
    def mode_start(self, **kwargs):
        super().mode_start(**kwargs)
        self.add_mode_event_handler('mball_display_ball_locked', self.display_ball_locked)
        self.add_mode_event_handler('mball_display_ball_added', self.display_ball_added)

    def display_ball_locked(self, **kwargs):
        pass
        # mysteries = [SCORE, ENERGY]

        # # TODO: conditionally add lock or adda ball award here based
        # # on whether or not im in multiball
        # if True:
        #     mysteries.append(BALL_LOCKED)
        # elif False:
        #     mysteries.append(ADDA_BALL)

        # award_type, display_text = random.choice(mysteries)
        # row_one = 'MYSTERY!AWARD'.center(16, "!")
        # row_two = display_text.center(16, "!")
        # self.display.set_vars(r1=row_one, r2=row_two)
        # self.award(award_type)

    def display_ball_added(self, **kwargs):
        pass




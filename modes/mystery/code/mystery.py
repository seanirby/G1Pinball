import random
from modes.base_mode import BaseMode

SCORE = ("mystery_score_awarded", "+500,000")
ENERGY = ("mystery_type_energy_awarded", "+3!NRG")
BALL_LOCKED = ("mystery_type_balllock_awarded", "BALL!LOCKED")
ADDA_BALL = ("mystery_type_addaball_awarded", "ADD-A-BALL")

class Mystery(BaseMode):
    def mode_start(self, **kwargs):
        super().mode_start(**kwargs)
        self.add_mode_event_handler('mystery_display_mystery', self.display_mystery)

    def display_mystery(self, **kwargs):
        mysteries = [SCORE, ENERGY]

        # TODO: conditionally add lock or adda ball award here based
        # on whether or not im in multiball
        if True:
            mysteries.append(BALL_LOCKED)
        elif False:
            mysteries.append(ADDA_BALL)

        award_type, display_text = random.choice(mysteries)
        row_one = 'MYSTERY!AWARD'.center(16, "!")
        row_two = display_text.center(16, "!")
        self.display.set_vars(r1=row_one, r2=row_two)
        self.award(award_type)

    def award(self, award_type):
        if award_type == SCORE[0]:
            self.player['score'] += 500000
        elif award_type == ENERGY[0]:
            # doing it this way so the charged flips logic can handle
            # overflow since max energy value is defined there
            self.machine.events.post('mystery_code_inc_energy')
            self.machine.events.post('mystery_code_inc_energy')
            self.machine.events.post('mystery_code_inc_energy')
        elif award_type == BALL_LOCKED[0]:
            pass
        elif award_type == ADDA_BALL[0]:
            pass



from mpf.core.mode import Mode
from modes.display import Display, ROW_LENGTH, TOTAL_LENGTH

SCORE_LENGTH = 10

class Base(Mode, Display):
    def __init__(self, *args, **kwargs):
        """Initialize bonus mode."""
        Mode.__init__(self, *args, **kwargs)
        Display.__init__(self, 'd_base_1', 'd_base_2')

    def mode_start(self, **kwargs):
        self.update_energy_display(self.player.energy)
        self.update_score_display(self.player.score)
        self.update_ball_display()

        self.add_mode_event_handler('player_score', self.handle_score_update)
        self.add_mode_event_handler('player_energy', self.handle_energy_update)
    
    def handle_score_update(self, **kwargs):
        change = kwargs['change']

        if change > 0:
            self.update_score_display(self.player.score)

    def handle_energy_update(self, **kwargs):
        change = kwargs['change']

        if abs(change) > 0:
            self.update_energy_display(self.player.energy)

    def update_score_display(self, score):
        # TODO: will probably need some formatting here, to include
        # commas if scores go over a 100mil etc...

        player_label = 'P{}!'.format(self.player.number)
        label_and_score = player_label + str(score).rjust(ROW_LENGTH-len(player_label), '!')
        self.prnt(label_and_score, 0, 0, ROW_LENGTH)

    def update_energy_display(self, energy):
        label_and_energy = 'NRG!{}'.format(str(energy))
        self.prnt(label_and_energy, ROW_LENGTH, ROW_LENGTH, TOTAL_LENGTH) 

    def update_ball_display(self):
        ball = self.machine.game.player.ball
        label_and_ball = 'BALL!{}'.format(str(ball))
        self.prnt(label_and_ball, TOTAL_LENGTH - len(label_and_ball), ROW_LENGTH, TOTAL_LENGTH) 


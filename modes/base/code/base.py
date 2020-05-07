from modes.base_mode import BaseMode
from modes.display import Display, ROW_LENGTH, TOTAL_LENGTH

SCORE_LENGTH = 10

class Base(BaseMode):
    def mode_start(self, **kwargs):
        super().mode_start(**kwargs)
        self.update_energy_display(self.player.energy)
        self.update_score_display(self.player.score)
        self.update_ball_display()

        self.add_mode_event_handler('player_score', self.handle_score_update)
        self.add_mode_event_handler('player_energy', self.handle_energy_update)
        self.add_mode_event_handler('timer_song_countdown_tick', self.update_countdown_display)
        self.add_mode_event_handler('timer_song_countdown_complete', self.remove_countdown_display)
        self.add_mode_event_handler('timer_song_countdown_complete', self.remove_countdown_display)

    
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
        self.display.prnt(label_and_score, 0, 0, ROW_LENGTH)

    def update_energy_display(self, energy):
        label_and_energy = 'NRG!{}'.format(str(energy))
        self.display.prnt(label_and_energy, ROW_LENGTH, ROW_LENGTH, TOTAL_LENGTH) 

    def update_ball_display(self):
        ball = self.machine.game.player.ball
        label_and_ball = 'BALL!{}'.format(str(ball))
        self.display.prnt(label_and_ball, TOTAL_LENGTH - len(label_and_ball), ROW_LENGTH, TOTAL_LENGTH) 

    def update_countdown_display(self, **kwargs):
        ticks = kwargs['ticks']
        self.display.prnt(str(ticks).rjust(2, '0'), ROW_LENGTH + 7, ROW_LENGTH, TOTAL_LENGTH) 

    def remove_countdown_display(self, **kwargs):
        self.display.prnt('!!', ROW_LENGTH + 7, ROW_LENGTH, TOTAL_LENGTH) 

from modes.base_mode import BaseMode

BASE_SHOTS = [
    "sh_ramp_left_lower",
    "sh_orbit_left",
    "sh_ramp_left_upper",
    "sh_gate_right",
    "sh_inner_loop",
    "sh_ramp_right",
    "sh_orbit_right",
]

SHOTS = [
    'sh_urge_ramp_left_lower',
    'sh_urge_orbit_left',
    'sh_urge_ramp_left_upper',
    'sh_urge_gate_right',
    'sh_urge_inner_loop',
    'sh_urge_ramp_right',
    'sh_urge_orbit_right',
]

# TODO: rename these to UNLIT_SHOT_STATE etc..
UNLIT_SHOT_INDEX = 0
LIT_SHOT_INDEX = 1
URGE_BASE_VALUE = 1000000
URGES_COLLECTED = 'urges_collected'
EVENT_CODE_COLLECTED_HURRY_UP = 'urge_code_collected'

class Urge(BaseMode):
    def mode_start(self, **kwargs):
        super().mode_start(**kwargs)
        self.last_urge_award = 0

        active_shot = self.machine.game.player[URGES_COLLECTED]

        self.machine.shots[SHOTS[active_shot]].jump(LIT_SHOT_INDEX)

        for i, shot in enumerate(BASE_SHOTS):
            self.add_mode_event_handler(shot + '_hit', self.handle_shot_hit, shot_index=i, lit_shot_index=active_shot)

        self.add_mode_event_handler('urge_display_urges_left', self.display_urges_left)
        self.add_mode_event_handler('urge_state_collected_started', self.award_score)
        self.add_mode_event_handler('urge_display_awarded_score', self.display_awarded_score)

    def mode_stop(self, **kwargs):
        pass

    def award_score(self, **kwargs):
        score = self.player['score']
        award = URGE_BASE_VALUE
        self.last_urge_award = award
        self.player['score'] += award

    def handle_shot_hit(self, **kwargs):
        state = self.machine.state_machines.urge.state

        # can only collect when hurry up is active
        if state != 'start':
            return

        lit_shot_index = kwargs['lit_shot_index']
        shot_index = kwargs['shot_index']
        num_shots = len(SHOTS) - 1

        # using the modulus in case player has already completed all shots
        if (lit_shot_index % (len(SHOTS) - 1)) == shot_index:
            self.collect_hurry_up(shot_index, lit_shot_index)

    def collect_hurry_up(self, shot_index, urges_collected):
        self.player[URGES_COLLECTED] = urges_collected + 1
        # disable shot so it cant be collected while the success show is playing
        self.machine.shots[SHOTS[shot_index]].disable()
        self.machine.events.post(EVENT_CODE_COLLECTED_HURRY_UP)

    def display_urges_left(self, **kwargs):
        urges = self.machine.game.player['urges_collected']
        row_one = '{}!MORE!FOR'.format(3 - urges).center(16, "!")
        row_two = 'DEVOLVED!LETTER'
        self.display.set_vars(r1=row_one, r2=row_two)

    def display_awarded_score(self, **kwargs):
        millions = int(self.last_urge_award/1000000)
        row_one = "{}!MILLION".format(millions).center(16, "!")
        row_two = "!!!!AWARDED!!!!!"
        self.display.set_vars(r1=row_one, r2=row_two)


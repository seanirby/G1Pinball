from mpf.core.mode import Mode
from modes.display import Display

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
URGES_COLLECTED = 'urges_collected'
EVENT_CODE_COLLECTED_HURRY_UP = 'urge_code_collected'

class Urge(Mode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mode_start(self, **kwargs):
        super().mode_start(**kwargs)
        active_shot = self.machine.game.player[URGES_COLLECTED]
        self.machine.shots[SHOTS[active_shot]].jump(LIT_SHOT_INDEX)

        for i, shot in enumerate(BASE_SHOTS):
            self.add_mode_event_handler(shot + '_hit', self.handle_shot_hit, shot_index=i, lit_shot_index=active_shot)

    def mode_stop(self, **kwargs):
        pass

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



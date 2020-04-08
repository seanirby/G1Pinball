from mpf.core.mode import Mode

BASE_SHOTS = [
    "sh_ramp_left_lower",
    "sh_orbit_left",
    "sh_ramp_left_upper",
    "seq_bash_left",
    "seq_bash_diagonal_left",
    "seq_bash_center",
    "seq_bash_diagonal_right",
    "seq_bash_right",
    "sh_zone_left",
    "sh_gate_right",
    "sh_inner_loop",
    "sh_ramp_right",
    "sh_orbit_right",
    ]

SHOTS = [
    "sh_ww_ramp_left_lower",
    "sh_ww_orbit_left",
    "sh_ww_ramp_left_upper",
    "sh_ww_bash_left",
    "sh_ww_bash_diagonal_left",
    "sh_ww_bash_center",
    "sh_ww_bash_diagonal_right",
    "sh_ww_bash_right",
    "sh_ww_zone_left",
    "sh_ww_gate_right",
    "sh_ww_inner_loop",
    "sh_ww_ramp_right",
    "sh_ww_orbit_right",
    ]

# the wiggler is the roving shot that needs to be hit
WIGGLER_SHOT_STATE_INDEX = 1

# this is just a lit shot that narrows the selections of shots the
# wiggler can be in
NORMAL_SHOT_STATE_INDEX = 0

UNLIT_SHOT_STATE_INDEX = 2

class WigglyWorld(Mode):
    def __init__(self, *args, **kwargs):
        """Initialize bonus mode."""
        super().__init__(*args, **kwargs)
        self._testing = False

    @property
    def testing(self):
        return self._testing

    @testing.setter
    def testing(self, x):
        self._testing = x

    def mode_start(self, **kwargs):

        self.reset_instance_vars()

        # state handlers
        self.add_mode_event_handler('ww_state_start_started', self.handle_state_start_started)
        self.add_mode_event_handler('ww_state_search_started', self.handle_state_search_started)
        self.add_mode_event_handler('ww_state_collected_started', self.handle_state_collected_started)
        self.add_mode_event_handler('ww_state_completed_started', self.handle_state_completed_started)

        # timer tick handler
        self.add_mode_event_handler('timer_ww_roving_shot_update_tick', self.handle_roving_shot_timer_tick)

        # shot hit event handler
        for i, shot_name in enumerate(BASE_SHOTS):
            hit_event = shot_name + '_hit'
            self.add_mode_event_handler(hit_event, self.handle_shot_hit, shot_name=SHOTS[i])

    def handle_roving_shot_timer_tick(self, **kwargs):
        force_tick = kwargs.get('force_tick')
        if self._testing and not force_tick:
            return

        curr_index = self.roving_shot_index
        curr_direction = self.roving_shot_direction
        next_direction = curr_direction

        # reverse direction if we're at one of our limits 
        if curr_index == self.roving_lower_bound and curr_direction < 0:
            next_direction = 1
        elif curr_index == self.roving_upper_bound and curr_direction > 0:
            next_direction = -1
            
        next_index = curr_index + next_direction

        if (next_index < self.roving_lower_bound) or (next_index > self.roving_upper_bound):
            return

        self.roving_shot_index = next_index
        self.roving_shot_direction = next_direction
        self.machine.shots[SHOTS[curr_index]].jump(NORMAL_SHOT_STATE_INDEX)
        self.machine.shots[SHOTS[next_index]].jump(WIGGLER_SHOT_STATE_INDEX)

    def handle_shot_hit(self, **kwargs):
        shot_name = kwargs['shot_name']
        shot = self.machine.shots[shot_name]
        shot_index = SHOTS.index(shot_name)
        shot_state = shot.state_name

        if shot_state == 'unlit':
            return

        elif shot_index == self.roving_shot_index:
            # just reset evefything for now
            self.roving_lower_bound = 0
            self.roving_upper_bound = len(SHOTS) - 1
            self.roving_shot_index = 0
            self.roving_shot_direction = 1

            for shot_name in SHOTS:
                self.machine.shots[shot_name].jump(NORMAL_SHOT_STATE_INDEX)

            self.machine.shots[SHOTS[0]].jump(WIGGLER_SHOT_STATE_INDEX)

        elif shot_index < self.roving_shot_index:
            for i in range(self.roving_lower_bound, shot_index + 1):
                shot_to_unlight = self.machine.shots[SHOTS[i]]
                shot_to_unlight.jump(UNLIT_SHOT_STATE_INDEX)

            self.roving_lower_bound = shot_index + 1 
        else:
            for i in range(shot_index, self.roving_upper_bound + 1):
                shot_to_unlight = self.machine.shots[SHOTS[i]]
                shot_to_unlight.jump(UNLIT_SHOT_STATE_INDEX)

            self.roving_upper_bound = shot_index - 1

    def handle_state_collected_started(self, **kwargs):
        pass

    def handle_state_completed_started(self, **kwargs):
        pass

    def handle_state_search_started(self, **kwargs):
        self.reset_instance_vars()

    def handle_state_start_started(self, **kwargs):
        pass

    def reset_instance_vars(self):
        self.roving_shot_index = 0
        self.roving_shot_direction = 1
        self.roving_lower_bound = 0
        self.roving_upper_bound = len(SHOTS) - 1
        self.machine.shots[SHOTS[self.roving_shot_index]].jump(WIGGLER_SHOT_STATE_INDEX)

        


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

NARROWED_SHOT_STATE_INDEX = 2
UNLIT_SHOT_STATE_INDEX = 3

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
        self.add_mode_event_handler('ww_state_restart_search', self.handle_state_restart_search)
        self.add_mode_event_handler('ww_state_collected_started', self.handle_state_collected_started)
        # self.add_mode_event_handler('ww_state_search_narrowed_started', self.handle_state_search_narrowed_started)
        # self.add_mode_event_handler('ww_state_search_narrowed_stopped', self.handle_state_search_narrowed_stopped)
        self.add_mode_event_handler('ww_state_completed_started', self.handle_state_completed_started)

        # timer tick handlers
        self.add_mode_event_handler('timer_ww_narrowed_tick', self.handle_narrowed_tick)
        self.add_mode_event_handler('timer_ww_roving_shot_update_tick', self.handle_roving_shot_timer_tick)

        # shot hit event handler
        for i, shot_name in enumerate(BASE_SHOTS):
            hit_event = shot_name + '_hit'
            self.add_mode_event_handler(hit_event, self.handle_shot_hit, shot_name=SHOTS[i])

    # todo: encapsulate this in an inherited songMode
    def mode_stop(self, **kwargs):
        self.machine.events.post('code_song_stopped')

    def handle_narrowed_tick(self, **kwargs):
        direction = 1 if self.narrow_start_index < self.narrow_end_index else -1
        next_index = self.narrow_curr_index + direction

        self.machine.shots[SHOTS[self.narrow_curr_index]].jump(UNLIT_SHOT_STATE_INDEX)

        if (direction == 1 and next_index > self.narrow_end_index) or (direction == -1 and next_index < self.narrow_end_index):
            self.machine.events.post('ww_code_narrowed_complete')
        else:
            self.narrow_curr_index = next_index
            
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
        if self.machine.state_machines.ww.state != 'search':
            return
        
        shot_name = kwargs['shot_name']
        shot = self.machine.shots[shot_name]
        shot_index = SHOTS.index(shot_name)

        # do nothing
        if (shot_index < self.roving_lower_bound) or (shot_index > self.roving_upper_bound):
            return

        # wiggler hit
        elif shot_index == self.roving_shot_index:
            # just reset evefything for now
            self.roving_lower_bound = 0
            self.roving_upper_bound = len(SHOTS) - 1
            self.roving_shot_index = 0
            self.roving_shot_direction = 1

            for shot_name in SHOTS:
                self.machine.shots[shot_name].jump(NORMAL_SHOT_STATE_INDEX)

            self.machine.shots[SHOTS[0]].jump(WIGGLER_SHOT_STATE_INDEX)

        # narrow the left side
        elif shot_index < self.roving_shot_index:
            self.start_narrowed(shot_index, 0)
            self.roving_lower_bound = shot_index + 1
        # narrow the right side
        else:
            self.start_narrowed(shot_index, len(SHOTS) - 1)
            self.roving_upper_bound = shot_index - 1

    def handle_state_collected_started(self, **kwargs):
        pass

    def handle_state_completed_started(self, **kwargs):
        pass

    def handle_state_restart_search(self, **kwargs):
        self.reset_instance_vars()

    def handle_state_narrowed_started(self, **kwargs):
        pass

    def handle_state_narrowed_stopped(self, **kwargs):
        pass

    def handle_state_start_started(self, **kwargs):
        pass

    def start_narrowed(self, start_index, end_index):
        self.machine.events.post('ww_code_narrowed_start')
        self.narrow_curr_index = start_index
        self.narrow_start_index = start_index
        self.narrow_end_index = end_index

    def reset_instance_vars(self):
        self.narrow_direction = 0
        self.roving_shot_index = 0
        self.roving_shot_direction = 1
        self.roving_lower_bound = 0
        self.roving_upper_bound = len(SHOTS) - 1
        self.machine.shots[SHOTS[self.roving_shot_index]].jump(WIGGLER_SHOT_STATE_INDEX)


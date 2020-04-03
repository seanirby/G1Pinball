from mpf.core.mode import Mode

class SongSelect(Mode):
    songs = ['foo', 'bar', 'baz', 'bap', 'bat']
    initial_shot_charge = [0, 0, 0, 0, 0]
    bash_left_shot = "sh_song_select_bash_left"
    bash_diagonal_left_shot = "sh_song_select_bash_diagonal_left"
    bash_center_shot = "sh_song_select_bash_center"
    bash_diagonal_right_shot = "sh_song_select_bash_diagonal_right"
    bash_right_shot = "sh_song_select_bash_right"
    bash_max_charge = 2
    bash_shots_arr = [
        bash_left_shot,
        bash_diagonal_left_shot,
        bash_center_shot,
        bash_diagonal_right_shot,
        bash_right_shot
        ]
        
    def __init__(self, *args, **kwargs):
        """Initialize bonus mode."""
        super().__init__(*args, **kwargs)
        self._bash_charge = [None] * 5
        self._bash_prox_profile = [None] * 5

    def mode_start(self, **kwargs):
        self._charge_bash_arr(self.initial_shot_charge)
        self._bash_prox_profile = [1, 2 ,1]

        # Todo: understand the lifecycle of this
        self.machine.events.post('song_select_state_skill_shot_start')

        # bash hit handlers
        # left
        self.add_mode_event_handler(self._shot_hit_event(0), self._handle_bash_hit, direction=0)
        # left diag
        self.add_mode_event_handler(self._shot_hit_event(1), self._handle_bash_hit, direction=1)
        # center
        self.add_mode_event_handler(self._shot_hit_event(2), self._handle_bash_hit, direction=2)
        # right diag
        self.add_mode_event_handler(self._shot_hit_event(3), self._handle_bash_hit, direction=3)
        # right
        self.add_mode_event_handler(self._shot_hit_event(4), self._handle_bash_hit, direction=4)

        # scoop hit handlers:
        self.add_mode_event_handler('sh_song_select_scoop_hit', self._handle_scoop_hit)

    def _handle_scoop_hit(self, **kwargs):
        if self.machine.state_machines.song_select.state == 'qualified':
            print('starting song')
            
    def _shot_hit_event(self, i):
        return self._get_shot_name(i) + "_hit"

    def _get_shot_name(self, i):
        return self.bash_shots_arr[i]

    def _charge_bash(self, i, amt):
        limited_charge = max(min(amt, self.bash_max_charge), 0)
        self._bash_charge[i] = limited_charge
        shot = self.machine.shots[self.bash_shots_arr[i]]
        # TODO - assumes order of shot profile states, this is bad
        shot.jump(limited_charge)

    def _charge_bash_arr(self, arr):
        for i, amt in enumerate(arr):
            self._charge_bash(i, amt)
            
    def _is_bash_fully_charged(self):
        for i, amt in enumerate(self._bash_charge):
            if amt < self.bash_max_charge:
                return False

        return True

    def _handle_bash_hit(self, **kwargs):
        state = self.machine.state_machines.song_select.state

        if state == 'qualifying':
            print('bash hit while in qualifying')
            # j is the direction on the bash we hit
            hit_shot_index = kwargs['direction']

            # this always works because _bash_prox_profile should always be an odd length
            prox_effect_center_index = int(len(self._bash_prox_profile)/2)

            # need to 'move' our proximity effect so the center is over hit_shot_index
            prox_effect_index_offset = -prox_effect_center_index + hit_shot_index

            for i, charge in enumerate(self._bash_charge):
                prox_effect_index = i - prox_effect_index_offset
                current_charge = self._bash_charge[i]

                if (prox_effect_index >= 0) and (prox_effect_index < len(self._bash_prox_profile)):
                    print("adding " + str(self._bash_prox_profile[prox_effect_index]) + " at " + str(i))
                    self._charge_bash(i, current_charge + self._bash_prox_profile[prox_effect_index])

            if self._is_bash_fully_charged():
                self.machine.events.post('song_select_state_qualified_start')
                for shot in self.bash_shots_arr:
                    self.machine.shots[shot].jump(3)
                self.machine.shots.sh_song_select_scoop.jump(1)

            print('checking if bash is fully charged, if so a song is qualified')

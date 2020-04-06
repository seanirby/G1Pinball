from mpf.core.mode import Mode

class SongSelect(Mode):
    # equivalent to number of chargeable bash directions
    num_songs = 5
    initial_shot_charge = [0, 0, 0, 0, 0]
    bash_max_charge = 2
    bash_shots_arr = [
        "sh_song_select_bash_left",
        "sh_song_select_bash_diagonal_left",
        "sh_song_select_bash_center",
        "sh_song_select_bash_diagonal_right",
        "sh_song_select_bash_right"
    ]
    bash_prox_profile = [1, 2, 1]
        
    def __init__(self, *args, **kwargs):
        """Initialize bonus mode."""
        super().__init__(*args, **kwargs)

    def mode_start(self, **kwargs):
        self._initialize_bash_charge()

        # update widgets
        self._update_widgets()
        self._initialize_state_machine()

        # bash hit handlers
        self.add_mode_event_handler("seq_bash_left_hit", self._handle_bash_hit, direction=0)
        self.add_mode_event_handler("seq_bash_diagonal_left_hit", self._handle_bash_hit, direction=1)
        self.add_mode_event_handler("seq_bash_center_hit", self._handle_bash_hit, direction=2)
        self.add_mode_event_handler("seq_bash_diagonal_right_hit", self._handle_bash_hit, direction=3)
        self.add_mode_event_handler("seq_bash_right_hit", self._handle_bash_hit, direction=4)

        # state transition handlers
        self.add_mode_event_handler('song_select_skill_shot_started', self._handle_skill_shot_started)
        self.add_mode_event_handler('song_select_qualifying_started', self._handle_qualifying_started)
        self.add_mode_event_handler('song_select_qualified_started', self._handle_qualified_started)

    def _initialize_state_machine(self):
        song_selected = self.machine.game.player['song_selected']

        if self._have_song_selected():
            self.machine.events.post('song_select_start_qualified')
        else: 
            self.machine.events.post('song_select_start_skill_shot')

    def _handle_skill_shot_started(self, **kwargs):
        pass

    def _handle_qualifying_started(self, **kwargs):
        pass

    def _handle_qualified_started(self, **kwargs):
        self.machine.shots.sh_song_select_scoop.jump(1)

        song_index = None

        if self._have_song_selected():
            song_index = self.machine.game.player["song_selected"]
        else:
            incomplete_songs =  []
            for i in range(0, self.num_songs):
                pvar_name = "song_{0}_completed".format(i)
                shot_name = self._get_shot_name(i)
                is_incomplete = self.machine.game.player[pvar_name] == 0
                if is_incomplete:
                    incomplete_songs.append(shot_name)

            centermost_index = int(len(incomplete_songs)/2)
            song_index = centermost_index

        # TODO - handle what happens when all are complete
        self._select_song(song_index)

    def _have_song_selected(self):
        return 0 <= self.machine.game.player['song_selected'] < self.num_songs

    def _select_song(self, i):
        for j in range(0, self.num_songs):
            shot_name = self._get_shot_name(j)
            if i == j:
                self.machine.game.player["song_selected"] = j
                # selected
                self.machine.shots[shot_name].jump(4)
                self.machine.events.post("song_select_{0}_status_selected".format(j))
            else:
                completed_status = self.machine.game.player["song_{0}_completed".format(j)]
                self.machine.shots[shot_name].jump(3)
                # for updating widgets
                if completed_status > 0:
                    self.machine.events.post("song_select_{0}_status_completed".format(j))
                else:
                    self.machine.events.post("song_select_{0}_status_unselected".format(j))



    def _update_widgets(self):
        # iterate through all available songs
        # check their status, if done post events
        pass

    def _handle_song_wait_started(self, **kwargs):
        self.machine.shots.sh_song_select_scoop.jump(0)

    def _handle_song_running_started(self, **kwargs):
        self.machine.events.post('bar_song_selected')

    def _shot_hit_event(self, i):
        return self._get_shot_name(i) + "_hit"

    def _get_shot_name(self, i):
        return self.bash_shots_arr[i]

    def _set_bash_charge(self, i, amt):
        limited_charge = max(min(amt, self.bash_max_charge), 0)
        self.machine.game.player["bash_{0}_charge".format(i)] = amt
        shot = self.machine.shots[self.bash_shots_arr[i]]
        # TODO - assumes order of shot profile states, this is bad
        shot.jump(limited_charge)

    def _initialize_bash_charge(self):
        for i in range(0, self.num_songs):
            amt = self.machine.game.player["bash_{0}_charge".format(i)]
            self._set_bash_charge(i, amt)
            
    def _is_bash_fully_charged(self):
        for i in range(0, self.num_songs):
            amt = self.machine.game.player["bash_{0}_charge".format(i)]
            if amt < self.bash_max_charge:
                return False

        return True

    def _get_bash_charge(self, i):
        return self.machine.game.player["bash_{0}_charge".format(i)]

    def _get_bash_charge(self, i):
        return self.machine.game.player["bash_{0}_charge".format(i)]

    def _handle_bash_hit(self, **kwargs):
        state = self.machine.state_machines.song_select.state
        hit_shot_index = kwargs['direction']

        if state == 'qualifying':
            self._handle_bash_hit_qualifying(hit_shot_index)
        elif state == 'qualified':
            self._handle_bash_hit_qualified(hit_shot_index)

    def _handle_bash_hit_qualifying(self, hit_shot_index):
        # this always works because bash_prox_profile should always be an odd length
        prox_effect_center_index = int(len(self.bash_prox_profile)/2)

        # need to 'move' our proximity effect so the center is over hit_shot_index
        prox_effect_index_offset = -prox_effect_center_index + hit_shot_index

        for i in range(0, self.num_songs):
            prox_effect_index = i - prox_effect_index_offset
            current_charge = self._get_bash_charge(i)

            if (prox_effect_index >= 0) and (prox_effect_index < len(self.bash_prox_profile)):
                self._set_bash_charge(i, current_charge + self.bash_prox_profile[prox_effect_index])

        if self._is_bash_fully_charged():
            self.machine.events.post('song_select_qualifying_complete')

    def _handle_bash_hit_qualified(self, hit_shot_index):
        current_selection = self.machine.game.player["song_selected"]

        if hit_shot_index == current_selection:
            return

        next_selection = None
        if hit_shot_index > current_selection:
            next_selection = current_selection + 1
        else:
            next_selection = current_selection - 1

        next_selection = min(max(next_selection, 0), 5)

        self._select_song(next_selection)
                

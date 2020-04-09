from mpf.core.mode import Mode

CODE_EVENT_START_QUALIFYING = 'code_song_select_start_qualifying'
CODE_EVENT_START_QUALIFIED = 'code_song_select_start_qualified'
CODE_EVENT_QUALIFYING_COMPLETED = 'code_song_select_qualifying_completed'
STATE_EVENT_QUALIFYING_STARTED = 'state_song_select_qualifying_started'
STATE_EVENT_QUALIFIED_STARTED = 'state_song_select_qualified_started'
STATE_EVENT_WAIT_STARTED = 'state_song_select_wait_started'

STATE_QUALIFYING = 'qualifying'
STATE_QUALIFIED = 'qualified'

BASH_PROX_PROFILE = [1,2,1]
INITIAL_BASH_CHARGES = [0, 0, 0, 0, 0]

MAX_BASH_CHARGE = 2
NUM_SONGS = 5
SCOOP_UNLIT_INDEX = 0
ZERO_CHARGE_SHOT_INDEX = 0

SHOT_NAMES = [
    "sh_song_select_bash_left",
    "sh_song_select_bash_diagonal_left",
    "sh_song_select_bash_center",
    "sh_song_select_bash_diagonal_right",
    "sh_song_select_bash_right"
]


class SongSelect(Mode):
    def _init__(self, *args, **kwargs):
        """Initialize bonus mode."""
        super().__init__(*args, **kwargs)

    def mode_start(self, **kwargs):
        self.initialize_bash_charges()
        self.initialize_state_machine()

        # bash hit handlers
        self.add_mode_event_handler("sh_bash_left_hit", self.handle_bash_hit, direction=0)
        self.add_mode_event_handler("sh_bash_diagonal_left_hit", self.handle_bash_hit, direction=1)
        self.add_mode_event_handler("sh_bash_center_hit", self.handle_bash_hit, direction=2)
        self.add_mode_event_handler("sh_bash_diagonal_right_hit", self.handle_bash_hit, direction=3)
        self.add_mode_event_handler("sh_bash_right_hit", self.handle_bash_hit, direction=4)

        # state transition handlers
        self.add_mode_event_handler(STATE_EVENT_QUALIFYING_STARTED, self.handle_qualifying_started)
        self.add_mode_event_handler(STATE_EVENT_QUALIFIED_STARTED, self.handle_qualified_started)
        self.add_mode_event_handler(STATE_EVENT_WAIT_STARTED, self.handle_wait_started)

    def get_bash_charge(self, i):
        return self.machine.game.player["bash_{0}_charge".format(i)]

    def get_shot_name(self, i):
        return SHOT_NAMES[i]

    def initialize_bash_charges(self):
        for i in range(0, NUM_SONGS):
            amt = self.get_bash_charge(i)
            self.set_bash_charge(i, amt)
            
    def is_bash_fully_charged(self):
        for i in range(0, NUM_SONGS):
            amt = self.get_bash_charge(i)
            if amt < MAX_BASH_CHARGE:
                return False
        return True

    def handle_bash_hit(self, **kwargs):
        state = self.machine.state_machines.song_select.state
        hit_shot_index = kwargs['direction']

        if state == STATE_QUALIFYING:
            self.handle_bash_hit_qualifying(hit_shot_index)
        elif state == STATE_QUALIFIED:
            self.handle_bash_hit_qualified(hit_shot_index)

    def handle_bash_hit_qualifying(self, hit_shot_index):
        # this always works because bash_prox_profile should always be an odd length
        prox_effect_center_index = int(len(BASH_PROX_PROFILE)/2)

        # need to 'move' our proximity effect so the center is over hit_shot_index
        prox_effect_index_offset = -prox_effect_center_index + hit_shot_index

        for i in range(0, NUM_SONGS):
            prox_effect_index = i - prox_effect_index_offset
            current_charge = self.get_bash_charge(i)

            if (prox_effect_index >= 0) and (prox_effect_index < len(BASH_PROX_PROFILE)):
                self.set_bash_charge(i, current_charge + BASH_PROX_PROFILE[prox_effect_index])

        if self.is_bash_fully_charged():
            self.machine.events.post(CODE_EVENT_QUALIFYING_COMPLETED)

    def handle_bash_hit_qualified(self, hit_shot_index):
        current_selection = self.machine.game.player["song_selected"]

        if hit_shot_index == current_selection:
            return

        next_selection = None
        if hit_shot_index > current_selection:
            next_selection = current_selection + 1
        else:
            next_selection = current_selection - 1

        next_selection = min(max(next_selection, 0), 5)

        self.select_song(next_selection)

    def handle_qualified_started(self, **kwargs):
        self.machine.shots.sh_song_select_scoop.jump(1)

        song_index = None

        if self.have_song_selected():
            song_index = self.machine.game.player["song_selected"]
        else:
            incomplete_songs =  []
            for i in range(0, NUM_SONGS):
                pvar_name = "song_{0}_completed".format(i)
                shot_name = self.get_shot_name(i)
                is_incomplete = self.machine.game.player[pvar_name] == 0
                if is_incomplete:
                    incomplete_songs.append(shot_name)

            centermost_index = int(len(incomplete_songs)/2)
            song_index = centermost_index

        # TODO - handle what happens when all are complete
        self.select_song(song_index)

    def handle_qualifying_started(self, **kwargs):
        self.machine.shots['sh_song_select_scoop'].jump(SCOOP_UNLIT_INDEX)
        for i, shot_name in enumerate(SHOT_NAMES):
            charge = self.get_bash_charge(i)
            self.machine.shots[shot_name].jump(charge)

    def handle_wait_started(self, **kwargs):
        # we are stopping the mode because the song has started
        selected_song = self.machine.game.player['song_selected']
        self.machine.events.post("song_select_{0}_status_running".format(selected_song))
        self.machine.game.player['song_selected'] = -1
        for i in range(0, NUM_SONGS):
            self.machine.game.player["bash_{0}_charge".format(i)] = 0

    def have_song_selected(self):
        return 0 <= self.machine.game.player['song_selected'] < NUM_SONGS

    def initialize_state_machine(self):
        song_selected = self.machine.game.player['song_selected']

        if self.have_song_selected():
            self.machine.events.post(CODE_EVENT_START_QUALIFIED)
        else: 
            self.machine.events.post(CODE_EVENT_START_QUALIFYING)

    def select_song(self, i):
        for j in range(0, NUM_SONGS):
            shot_name = self.get_shot_name(j)
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

    def set_bash_charge(self, i, amt):
        limited_charge = max(min(amt, MAX_BASH_CHARGE), 0)
        self.machine.game.player["bash_{0}_charge".format(i)] = amt
        shot = self.machine.shots[SHOT_NAMES[i]]
        # TODO - assumes order of shot profile states, this is bad
        shot.jump(limited_charge)

    def shot_hit_event(self, i):
        return self.get_shot_name(i) + "_hit"

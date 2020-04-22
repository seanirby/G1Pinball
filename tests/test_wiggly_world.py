from mode_test_case import ModeTestCase
from modes.wiggly_world.code.wiggly_world import BASE_SHOTS, SHOTS, WIGGLER_SHOT_STATE_INDEX

class TestWigglyWorld(ModeTestCase):
    def get_mode_instance(self):
        return self.machine.modes['wiggly_world']

    def get_wiggler_shot_index(self):
        for shot_name in SHOTS:
            if self.machine.shots[shot_name].state == WIGGLER_SHOT_STATE_INDEX:
                return SHOTS.index(shot_name)

    def move_wiggler_shot(self, times):
        mode = self.get_mode_instance()
        for i in range(0, times):
            mode.handle_roving_shot_timer_tick(force_tick=True)
            self.advance_time_and_run(1)
            

    def setup_wiggly_world(self):
        self.setup_game()
        self.qualify_song()
        song_selected = self.machine.game.player['song_selected']
        self.assertEqual(2, song_selected)
        self.get_mode_instance().testing = True
        self.hit_switch_and_run('s_scoop', 4)
        self.assertModeNotRunning('song_select')
        self.release_switch_and_run('s_scoop', 1)

    def test_is_selected_after_qualifying(self):
        """ This song is selected by default after qualifying for the first time """
        self.mock_event('ww_state_intro_started')
        self.mock_event('song_intro_played')
        self.mock_event('song_intro_complete')
        self.setup_wiggly_world()
        self.advance_time_and_run(5)
        self.assertModeRunning('wiggly_world')
        self.assertEventCalled('ww_state_intro_started', 1)
        self.assertEventCalled('song_intro_played', 1)
        self.advance_time_and_run(10)
        self.assertEventCalled('song_intro_complete', 1)

    def test_initial_shots(self):
        """ At first a number of shots are lit, and one shot is the 'wiggler' (the shot you are supposed to collect) """
        self.setup_wiggly_world()

        lit_shots = []
        lit_wiggler_shot = []
        
        for shot_name in SHOTS:
            state_name = self.machine.shots[shot_name].state_name
            if state_name == 'lit':
                lit_shots.append(shot_name)
            else:
                lit_wiggler_shot.append(shot_name)

        self.assertEqual(len(lit_wiggler_shot), 1)
        self.assertEqual(len(lit_shots), len(SHOTS) - 1)

    def test_hitting_the_wiggler_collects(self):
        self.setup_wiggly_world()
        # verify leftmost shot is lit
        self.assertEqual(self.get_wiggler_shot_index(), 0)

        # light the shot in the middle of the playfield and verify
        centerish_shot_index = 6
        self.move_wiggler_shot(centerish_shot_index)
        self.assertEqual(self.get_wiggler_shot_index(), centerish_shot_index)

        # hit a shot to the left and right of it and verify shots to
        # the left and right of those are respectively wiped out
        left_shot_index = centerish_shot_index - 2
        self.mock_event("ww_code_narrowed_start")
        self.mock_event("ww_state_narrowed_started")
        self.mock_event("ww_state_narrowed_stopped")
        self.post_event(BASE_SHOTS[left_shot_index]+'_hit', 1)
        self.assertEventCalled('ww_code_narrowed_start', 1)
        self.assertEventCalled('ww_state_narrowed_started', 1)
        self.assertEventCalled('ww_state_narrowed_stopped', 1)

        right_shot_index = centerish_shot_index + 2
        self.post_event(BASE_SHOTS[right_shot_index]+'_hit', 1)

        for i, shot_name in enumerate(SHOTS):
            print(shot_name)
            state_name = self.machine.shots[shot_name].state_name
            # shots to the left should be unlit
            if i <= left_shot_index:
                self.assertEqual(state_name, 'unlit')
            # shots to the right should be unlit
            elif i >= right_shot_index:
                self.assertEqual(state_name, 'unlit')
            # shots in between that arent the wiggler shot are lit
            elif i != centerish_shot_index:
                self.assertEqual(state_name, 'lit')
            else:
                self.assertEqual(state_name, 'lit_wiggler')

    def test_mode_is_over_when_song_countdown_expires(self):
        self.setup_wiggly_world()
        self.assertModeRunning('wiggly_world')
        self.advance_time_and_run(100)
        self.assertModeNotRunning('wiggly_world')
        self.assertModeRunning('song_select')
        self.assertEqual(self.machine.state_machines.song_select.state, 'qualifying')

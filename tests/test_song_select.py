from tests.mode_test_case import ModeTestCase

class TestSongSelect(ModeTestCase):
    def assert_charge_profile(self, left, diagonal_left, center, diagonal_right, right):
        self.assertEqual(self.machine.shots.sh_song_select_bash_left.state_name, 'charge_' + str(left))
        self.assertEqual(self.machine.shots.sh_song_select_bash_diagonal_left.state_name, 'charge_' + str(diagonal_left))
        self.assertEqual(self.machine.shots.sh_song_select_bash_center.state_name, 'charge_' + str(center))
        self.assertEqual(self.machine.shots.sh_song_select_bash_diagonal_right.state_name, 'charge_' + str(diagonal_right))
        self.assertEqual(self.machine.shots.sh_song_select_bash_right.state_name, 'charge_' + str(right))

    def assert_song_selected(self, i):
        song_map = ['left', 'diagonal_left', 'center', 'diagonal_right', 'right']
        for j, direction in enumerate(song_map):
            shot_name = "sh_song_select_bash_{0}".format(direction)
            shot = self.machine.shots[shot_name]
            if (i == j):
                self.assertEqual(shot.state_name, 'song_selected')
            else:
                self.assertEqual(shot.state_name, 'unlit')

    def test_qualifying(self):
        "Test that a player can hit the bash target in all of its directions to qualifying a song"
        self.setup_game()
        state_machine = self.machine.state_machines.song_select
        self.assertEqual(self.machine.state_machines.song_select.state, 'qualifying')
 
        self.assert_charge_profile(0, 0, 0, 0, 0)
        # equivalent to sh_song_select_bash_left_hit
        self.hit_and_release_switch("s_bash_right")
        self.advance_time_and_run(1)
        self.assert_charge_profile(2, 1, 0, 0, 0)
        # equivalent to sh_song_select_bash_right_hit
        self.hit_and_release_switch("s_bash_left")
        self.advance_time_and_run(1)
        self.assert_charge_profile(2, 1, 0, 1, 2)
        # equivalent to sh_song_select_bash_center_hit
        self.hit_and_release_switch("s_bash_forward")
        self.advance_time_and_run(1)

        self.assertEqual(self.machine.state_machines.song_select.state, 'qualified')

        # TODO - test handling the mode preview that happens during wait state
        # self.assertEqual(self.machine.state_machines.song_select.state, 'wait')

        # todo - find a way to simulate scoop hit and test for song_running
        # self.advance_time_and_run(5)
        # self.assertEqual(self.machine.state_machines.song_select.state, 'song_running')
        
    def test_bash_charge_persists(self):
        """ A player's bash target charge perists after they drain """

        self.setup_game()

        # adding another player
        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(5)

        self.assert_charge_profile(0, 0, 0, 0, 0)
        self.hit_and_release_switch("s_bash_right")
        self.advance_time_and_run(1)
        self.assert_charge_profile(2, 1, 0, 0, 0)

        self.assertEqual(self.machine.game.player.number, 1)
        self.drain_to_next_ball()

        self.assertEqual(self.machine.game.player.number, 2)
        self.assert_charge_profile(0, 0, 0, 0, 0)
        self.hit_and_release_switch("s_bash_left")
        self.advance_time_and_run(1)
        self.assert_charge_profile(0, 0, 0, 1, 2)
        self.drain_to_next_ball()

        self.assertEqual(self.machine.game.player.number, 1)
        self.assert_charge_profile(2, 1, 0, 0, 0)

        self.drain_to_next_ball()
        self.assert_charge_profile(0, 0, 0, 1, 2)
        

    def test_can_choose_song(self):
        """ Once a song is qualified, players can choose which one they want to play by hitting the bash target """
        self.setup_game()

        # adding another player to test persistence
        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(5)

        # test that player one can qualify a song and select it by making bash hits
        self.qualify_song()
        self.assert_song_selected(2)

        self.hit_and_release_switch("s_bash_left")
        self.advance_time_and_run(1)
        self.assert_song_selected(3)

        self.hit_and_release_switch("s_bash_left")
        self.advance_time_and_run(1)
        self.assert_song_selected(4)

        self.hit_and_release_switch("s_bash_left")
        self.advance_time_and_run(1)
        self.assert_song_selected(4)

        self.hit_and_release_switch("s_bash_forward")
        self.advance_time_and_run(1)
        self.assert_song_selected(3)

        # test for player 2
        self.drain_to_next_ball()
        self.qualify_song()
        self.assert_song_selected(2)

        self.hit_and_release_switch("s_bash_right")
        self.advance_time_and_run(1)
        self.assert_song_selected(1)

        self.hit_and_release_switch("s_bash_right")
        self.advance_time_and_run(1)
        self.assert_song_selected(0)

        self.hit_and_release_switch("s_bash_right")
        self.advance_time_and_run(1)
        self.assert_song_selected(0)

        self.hit_and_release_switch("s_bash_forward")
        self.advance_time_and_run(1)
        self.assert_song_selected(1)

        # test that player 1s song is still selected
        self.drain_to_next_ball()
        self.assertEqual(self.machine.game.player["song_selected"], 3)

        # test that player 2s song is still selected
        self.drain_to_next_ball()
        self.assertEqual(self.machine.game.player["song_selected"], 1)

    def test_starting_song(self):
        "Hitting the scoop when qualified starts the selected song"
        self.setup_game()
        self.mock_event('song_select_2_status_running')
        self.mock_event('scoop_eject_paused_for_song_intro')

        self.qualify_song()
        self.assert_song_selected(2)
        self.hit_switch_and_run("s_scoop", 1)
        self.assertEventCalled('scoop_eject_paused_for_song_intro', 1)
        self.assertEventCalled('song_select_2_status_running', 1)
        self.assertModeNotRunning('song_select')



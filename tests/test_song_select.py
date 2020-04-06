from mpf.tests.MpfTestCase import MagicMock
from mpf.tests.MpfMachineTestCase import MpfMachineTestCase

class TestSongSelect(MpfMachineTestCase):

    def _start_game(self):
        self.machine.playfield.add_ball = MagicMock()
        # self.machine.ball_controller.num_balls_known = 3
        self.assertModeRunning('attract')
        self.hit_switch_and_run("s_trough", 1)
        self.hit_and_release_switch("s_start")

        # All this stuff may be unnecessary but its what I need to do currently when I run mpf both -x 
        self.release_switch_and_run("s_trough", 1)
        self.hit_and_release_switch("s_plunger")
        self.hit_and_release_switch("s_orbit_right")
        self.assertIsNotNone(self.machine.game)

    def _drain_to_next_ball(self):
        self.hit_switch_and_run("s_trough", 1)
        self.release_switch_and_run("s_trough", 1)
        self.hit_and_release_switch("s_plunger")
        self.advance_time_and_run(5)
        self.hit_and_release_switch("s_orbit_right")
        self.advance_time_and_run(5)

    def _skip_skillshot(self):
        state_machine = self.machine.state_machines.song_select
        self.assertEqual(state_machine.state, 'skill_shot')
        self.advance_time_and_run(5)

    def _setup_game(self):
        self._start_game()
        self.assertModeRunning('song_select')

    def _qualify_song(self):
        self.assertEqual(self.machine.state_machines.song_select.state, 'qualifying')
        self.hit_and_release_switch("s_bash_left")
        self.advance_time_and_run(1)
        self.hit_and_release_switch("s_bash_forward")
        self.advance_time_and_run(1)
        self.hit_and_release_switch("s_bash_right")
        self.advance_time_and_run(1)
        self.assertEqual(self.machine.state_machines.song_select.state, 'qualified')

    def _assert_charge_profile(self, left, diagonal_left, center, diagonal_right, right):
        self.assertEqual(self.machine.shots.sh_song_select_bash_left.state_name, 'charge_' + str(left))
        self.assertEqual(self.machine.shots.sh_song_select_bash_diagonal_left.state_name, 'charge_' + str(diagonal_left))
        self.assertEqual(self.machine.shots.sh_song_select_bash_center.state_name, 'charge_' + str(center))
        self.assertEqual(self.machine.shots.sh_song_select_bash_diagonal_right.state_name, 'charge_' + str(diagonal_right))
        self.assertEqual(self.machine.shots.sh_song_select_bash_right.state_name, 'charge_' + str(right))

    def _assert_song_selected(self, i):
        song_map = ['left', 'diagonal_left', 'center', 'diagonal_right', 'right']
        for j, direction in enumerate(song_map):
            shot_name = "sh_song_select_bash_{0}".format(direction)
            shot = self.machine.shots[shot_name]
            if (i == j):
                print(j)
                self.assertEqual(shot.state_name, 'song_selected')
            else:
                self.assertEqual(shot.state_name, 'unlit')

    def test_skill_shot_turns_off(self):
        self._setup_game()
        state_machine = self.machine.state_machines.song_select
        self.assertEqual(state_machine.state, 'skill_shot')
#        todo - update when i figure out how long skill shot hurry should last
        self.advance_time_and_run(5)
        self.assertEqual(self.machine.state_machines.song_select.state, 'qualifying')

    # TODO
    def test_mode_ready_on_ball_start(self):
        pass

    def test_qualifying(self):
        self._setup_game()
        state_machine = self.machine.state_machines.song_select
        self.assertEqual(state_machine.state, 'skill_shot')
        # TODO - update when i figure out how long skill shot hurry should last
        self.advance_time_and_run(5)
        self.assertEqual(self.machine.state_machines.song_select.state, 'qualifying')
 
        # TODO use assert charge profile
        self._assert_charge_profile(0, 0, 0, 0, 0)
        # equivalent to sh_song_select_bash_left_hit
        self.hit_and_release_switch("s_bash_right")
        self.advance_time_and_run(1)
        self._assert_charge_profile(2, 1, 0, 0, 0)
        # equivalent to sh_song_select_bash_right_hit
        self.hit_and_release_switch("s_bash_left")
        self.advance_time_and_run(1)
        self._assert_charge_profile(2, 1, 0, 1, 2)
        # equivalent to sh_song_select_bash_center_hit
        self.hit_and_release_switch("s_bash_forward")
        self.advance_time_and_run(1)

        self.assertEqual(self.machine.state_machines.song_select.state, 'qualified')
        self.hit_and_release_switch("s_scoop")

        self.assertEqual(self.machine.state_machines.song_select.state, 'song_wait')

        # todo - find a way to simulate scoop hit and test for song_running
        # self.advance_time_and_run(5)
        # self.assertEqual(self.machine.state_machines.song_select.state, 'song_running')
        
    def test_bash_charge_persists(self):
        """ A player's bash target charge perists after they drain """

        self._setup_game()
        self._skip_skillshot()

        # adding another player
        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(5)

        self._assert_charge_profile(0, 0, 0, 0, 0)
        self.hit_and_release_switch("s_bash_right")
        self.advance_time_and_run(1)
        self._assert_charge_profile(2, 1, 0, 0, 0)

        self.assertEqual(self.machine.game.player.number, 1)
        self._drain_to_next_ball()

        self.assertEqual(self.machine.game.player.number, 2)
        self._assert_charge_profile(0, 0, 0, 0, 0)
        self.hit_and_release_switch("s_bash_left")
        self.advance_time_and_run(1)
        self._assert_charge_profile(0, 0, 0, 1, 2)
        self._drain_to_next_ball()

        self.assertEqual(self.machine.game.player.number, 1)
        self._assert_charge_profile(2, 1, 0, 0, 0)

        self._drain_to_next_ball()
        self._assert_charge_profile(0, 0, 0, 1, 2)
        

    def test_can_choose_song(self):
        """ Once a song is qualified, players can choose which one they want to play by hitting the bash target """
        self._setup_game()
        self._skip_skillshot()

        # adding another player to test persistence
        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(5)

        # test that player one can qualify a song and select it by making bash hits
        self._qualify_song()
        self._assert_song_selected(2)

        self.hit_and_release_switch("s_bash_left")
        self.advance_time_and_run(1)
        self._assert_song_selected(3)

        self.hit_and_release_switch("s_bash_left")
        self.advance_time_and_run(1)
        self._assert_song_selected(4)

        self.hit_and_release_switch("s_bash_left")
        self.advance_time_and_run(1)
        self._assert_song_selected(4)

        self.hit_and_release_switch("s_bash_forward")
        self.advance_time_and_run(1)
        self._assert_song_selected(3)

        # test for player 2
        self._drain_to_next_ball()
        self._qualify_song()
        self._assert_song_selected(2)

        self.hit_and_release_switch("s_bash_right")
        self.advance_time_and_run(1)
        self._assert_song_selected(1)

        self.hit_and_release_switch("s_bash_right")
        self.advance_time_and_run(1)
        self._assert_song_selected(0)

        self.hit_and_release_switch("s_bash_right")
        self.advance_time_and_run(1)
        self._assert_song_selected(0)

        self.hit_and_release_switch("s_bash_forward")
        self.advance_time_and_run(1)
        self._assert_song_selected(1)

        # test that player 1s song is still selected
        self._drain_to_next_ball()
        self.assertEqual(self.machine.game.player["song_selected"], 3)

        # test that player 2s song is still selected
        self._drain_to_next_ball()
        self.assertEqual(self.machine.game.player["song_selected"], 1)

    

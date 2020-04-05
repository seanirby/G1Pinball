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

    def _setup_game(self):
        self._start_game()
        self.assertModeRunning('song_select')

    def _assert_charge_profile(self, left, diagonal_left, center, diagonal_right, right):
        self.assertEqual(self.machine.shots.sh_song_select_bash_left.state_name, 'charge_' + str(left))
        self.assertEqual(self.machine.shots.sh_song_select_bash_diagonal_left.state_name, 'charge_' + str(diagonal_left))
        self.assertEqual(self.machine.shots.sh_song_select_bash_center.state_name, 'charge_' + str(center))
        self.assertEqual(self.machine.shots.sh_song_select_bash_diagonal_right.state_name, 'charge_' + str(diagonal_right))
        self.assertEqual(self.machine.shots.sh_song_select_bash_right.state_name, 'charge_' + str(right))

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
        

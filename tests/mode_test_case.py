from mpf.tests.MpfTestCase import MagicMock
from mpf.tests.MpfFakeGameTestCase import MpfFakeGameTestCase
from mpf.tests.MpfGameTestCase import MpfGameTestCase
from mpf.tests.MpfMachineTestCase import MpfMachineTestCase
from mpfmc.tests.FullMpfMachineTestCase import FullMachineTestCase

class ModeTestCase(MpfFakeGameTestCase):
    def get_config_file(self):
        return "config.yaml"

    def get_machine_path(self):
        return ""

    def get_absolute_machine_path(self):
        # do not use path relative to MPF folder
        return self.get_machine_path()

    def get_platform(self):
        return 'smart_virtual'

    def assert_drops_state(self, state):
        self.assertSwitchState('s_drop_top', state)
        self.assertSwitchState('s_drop_middle', state)
        self.assertSwitchState('s_drop_bottom', state)

    def assert_song_selected(self, i):
        song_map = ['left', 'diagonal_left', 'center', 'diagonal_right', 'right']
        for j, direction in enumerate(song_map):
            shot_name = "sh_song_select_bash_{0}".format(direction)
            shot = self.machine.shots[shot_name]
            if (i == j):
                self.assertEqual(shot.state_name, 'song_selected')
            else:
                self.assertEqual(shot.state_name, 'unlit')


    def assertStateMachineState(self, machine, state):
        self.assertEqual(self.machine.state_machines[machine].state, state)

    def assertShotState(self, shot, state):
        self.assertEqual(self.machine.shots[shot].state, state)

    def drain_to_next_ball(self):
        self.hit_switch_and_run("s_trough", 1)
        self.release_switch_and_run("s_trough", 1)
        self.hit_and_release_switch("s_plunger")
        self.advance_time_and_run(5)
        self.hit_and_release_switch("s_orbit_right")
        self.advance_time_and_run(5)

    def hit_scoop_and_wait(self, amt):
        self.hit_switch_and_run("s_scoop", amt)

    def qualify_song(self):
        self.assertEqual(self.machine.state_machines.song_select.state, 'qualifying')
        self.hit_and_release_switch("s_bash_left")
        self.advance_time_and_run(1)
        self.hit_and_release_switch("s_bash_forward")
        self.advance_time_and_run(1)
        self.hit_and_release_switch("s_bash_right")
        self.advance_time_and_run(1)
        self.assertEqual(self.machine.state_machines.song_select.state, 'qualified')

    # TODO: is this the best way to do this?
    def knockdown_drops(self):
        self.hit_switch_and_run('s_drop_top', .1)
        self.hit_switch_and_run('s_drop_middle', .1)
        self.hit_switch_and_run('s_drop_bottom', .1)

    def reset_drops(self):
        self.release_switch_and_run('s_drop_top', .1)
        self.release_switch_and_run('s_drop_middle', .1)
        self.release_switch_and_run('s_drop_bottom', .1)

    def setup_game(self):
        self.start_game()
        self.assertModeRunning('song_select')

    def start_game(self):
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

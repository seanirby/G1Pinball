from mpf.tests.MpfTestCase import MagicMock
from mpf.tests.MpfMachineTestCase import MpfMachineTestCase

class TestBar(MpfMachineTestCase):

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
        self.assertModeRunning('bar')

    def test_normal(self):
        self._setup_game()
        # Both ramps start lit, bash timer is not running, ramp count is 0
        # TODO should start mode here
        self.assertEqual(self.machine.shots.bar_ramp_left_lower.state_name, 'lit')
        self.assertEqual(self.machine.shots.bar_ramp_right.state_name, 'lit')
        # TODO should name state something other than complete
        self.assertEqual(self.machine.shots.bar_bash.state_name, 'complete')
        self.assertFalse(self.machine.timers.bar_bash_timer.running)
        self.assertEqual(self.machine.counters.bar_ramp_count.value, 0)


        # hitting one ramp should light the other and start timer
        self.hit_and_release_switch("s_ramp_right")
        self.assertEqual(self.machine.shots.bar_ramp_left_lower.state_name, 'lit')
        self.assertEqual(self.machine.shots.bar_ramp_right.state_name, 'complete')
        self.assertTrue(self.machine.timers.bar_bash_timer.running)
        self.assertEqual(self.machine.counters.bar_ramp_count.value, 1)

        # hitting the same ramp does nothing
        self.hit_and_release_switch("s_ramp_right")
        self.assertEqual(self.machine.shots.bar_ramp_left_lower.state_name, 'lit')
        self.assertEqual(self.machine.shots.bar_ramp_right.state_name, 'complete')
        self.assertTrue(self.machine.timers.bar_bash_timer.running)
        self.assertEqual(self.machine.counters.bar_ramp_count.value, 1)

        # hitting the opposite ramp alternates the ramp and updates ramp counter
        self.hit_and_release_switch("s_ramp_left_lower")
        self.assertEqual(self.machine.shots.bar_ramp_left_lower.state_name, 'complete')
        self.assertEqual(self.machine.shots.bar_ramp_right.state_name, 'lit')
        self.assertTrue(self.machine.timers.bar_bash_timer.running)
        self.assertEqual(self.machine.counters.bar_ramp_count.value, 2)

        # hitting the bash target 'collects' the ramps that were hit and resets shots
        self.hit_and_release_switch("s_bash_forward")
        self.assertEqual(self.machine.shots.bar_ramp_left_lower.state_name, 'lit')
        self.assertEqual(self.machine.shots.bar_ramp_right.state_name, 'lit')
        self.assertEqual(self.machine.shots.bar_bash.state_name, 'complete')
        self.assertFalse(self.machine.timers.bar_bash_timer.running)
        self.assertEqual(self.machine.counters.bar_ramp_count.value, 0)
        # TODO test that my score was updated here

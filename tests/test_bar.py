from tests.mode_test_case import ModeTestCase

class TestBar(ModeTestCase):
    def setup(self):
        self.setup_game()
        self.assertModeRunning('bar')

    def test_normal(self):
        self.setup()
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

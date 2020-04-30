from tests.mode_test_case import ModeTestCase

class TestTest(ModeTestCase):
    def test_starts_and_stops(self):
        self.setup_game()
        self.assertModeRunning('test')

        # this mode runs for 3 seconds but we want to make sure the
        # other long running timer is remove.
        # Concerned about this due to using my own Mode subclass
        self.advance_time_and_run(20)
        self.assertFalse(self.machine.timers['test_long_running'].running)
        self.assertModeNotRunning('test')

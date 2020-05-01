from tests.mode_test_case import ModeTestCase

EVENT_STATE_URGE_ACTIVE_STARTED = 'drops_state_urge_active_started'
EVENT_RESET_DROPS = 'drops_state_reset_bank'
EVENT_URGE_STARTED = 'mode_urge_started'
EVENT_DROPS_DOWN = 'drop_target_bank_drops_down'
DROPS_MODE = 'drops'
URGE_MODE = 'urge'

class TestDrops(ModeTestCase):

    def setup(self):
        self.setup_game()
        self.assertModeRunning(DROPS_MODE)

    def test_starts_urge_mode_when_drops_are_completed(self):
        self.setup()
        self.mock_event(EVENT_DROPS_DOWN)
        self.mock_event(EVENT_STATE_URGE_ACTIVE_STARTED)

        self.assertModeNotRunning(URGE_MODE)
        self.assertStateMachineState('drops', 'start')
        self.knockdown_drops()

        self.assertEventCalled(EVENT_DROPS_DOWN)
        self.assertEventCalled(EVENT_STATE_URGE_ACTIVE_STARTED, 1)
        self.assertStateMachineState('drops', 'urge_active')
        self.assertModeRunning(URGE_MODE)

        # however long this timer lasts, not sure yet
        self.advance_time_and_run(40)
        self.assertModeNotRunning(URGE_MODE)
        self.assertStateMachineState('drops', 'start')

    def test_resets_drops_after_ball_drain(self):
        self.mock_event(EVENT_RESET_DROPS)
        self.setup()

        self.assertEventCalled(EVENT_RESET_DROPS, 1)
        self.assert_drops_state(False)
        self.knockdown_drops()
        self.assert_drops_state(True)

        # wait for success show to complete
        self.advance_time_and_run(10)

        self.drain_one_ball()
        self.advance_time_and_run(5)
        # event is called when urge mode stops and when drops mode starts
        self.assertEventCalled(EVENT_RESET_DROPS, 2)
        self.assert_drops_state(False)

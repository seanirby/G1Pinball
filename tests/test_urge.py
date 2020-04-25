from mode_test_case import ModeTestCase
from modes.urge.code.urge import (
    SHOTS,
    STATE,
    STATE_PAUSED,
    STATE_COMPLETE
)

EVENT_RESET_DROPS = 'drops_state_reset_bank'

class TestUrge(ModeTestCase):

    def setup(self):
        self.setup_game()
        self.mock_event(EVENT_RESET_DROPS)
        self.assertModeRunning('drops')
        self.assertStateMachineState(STATE, STATE_HURRY_UP_INACTIVE)
        self.assertHurryUpTimerRunning(False)
        self.assertFalse(self.machine.timers.drops_hurry_up.running)

    def assertHurryUpTimerRunning(self, is_running):
        self.assertEqual(self.machine.timers.drops_hurry_up.running, is_running)

    def test_hurry_up_times_out(self):
        self.setup()

        self.advance_time_and_run(40)

        self.assertStateMachineState(STATE, STATE_HURRY_UP_INACTIVE)
        self.assertShotState(ROLLOVER_SHOT, ROLLOVER_SHOT_UNLIT_INDEX)
        self.assertHurryUpTimerRunning(False)
        self.assertEventCalled(EVENT_RESET_DROPS, 1)

    # def test_collects_hurry_up(self):
    #     self.setup()

    #     self.hit_rollover_button()
    #     self.assertEventCalled(EVENT_RESET_DROPS, 1)

    #     self.assertHurryUpTimerRunning(False)
    #     self.assertStateMachineState(STATE, STATE_HURRY_UP_INACTIVE)
    #     self.assertShotState(ROLLOVER_SHOT, ROLLOVER_SHOT_UNLIT_INDEX)

    # def test_drains_while_hurry_up_is_active(self):
    #     self.setup()

    #     self.advance_time_and_run(10)
    #     self.assertSwitchState('s_drop_top', True)
    #     self.assertSwitchState('s_drop_middle', True)
    #     self.assertSwitchState('s_drop_bottom', True)

    #     self.drain_to_next_ball()

    #     # make sure timer is reset completely to its start value
    #     start_value = self.machine.timers.urge_hurry_up.start_value
    #     ticks = self.machine.timers.urge_hurry_up.ticks
    #     self.assertEqual(start_value, ticks)

    #     self.assertStateMachineState(STATE, STATE_HURRY_UP_INACTIVE)
    #     self.assertHurryUpTimerRunning(False)
    #     self.assertSwitchState('s_drop_top', False)
    #     self.assertSwitchState('s_drop_middle', False)
    #     self.assertSwitchState('s_drop_bottom', False)

    # def test_start_mode_while_hurry_up_is_active(self):
    #     self.setup()
    #     self.start_hurry_up()
    #     ticks_before_song = self.machine.timers.drops_hurry_up.ticks
        
    #     self.qualify_song()

    #     # Timer should be paused shortly after starting the mode
    #     self.hit_scoop_and_wait(1)
    #     self.assertHurryUpTimerRunning(False)

    #     # Timer should resume once mode has started
    #     self.advance_time_and_run(5)
    #     self.assertModeRunning('wiggly_world')
    #     self.assertHurryUpTimerRunning(True)

    # def test_for_multiple_players(self):
    #     pass

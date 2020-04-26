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
        self.advance_time_and_run(30)
        self.assertModeNotRunning(URGE_MODE)
        self.assertStateMachineState('drops', 'start')

    def test_resets_drops_after_ball_drain(self):
        self.mock_event(EVENT_RESET_DROPS)
        self.setup()

        self.assertEventCalled(EVENT_RESET_DROPS, 1)
        self.assert_drops_state(False)
        self.knockdown_drops()
        self.assert_drops_state(True)

        self.drain_one_ball()
        self.advance_time_and_run(5)
        self.assertEventCalled(EVENT_RESET_DROPS, 2)
        self.assert_drops_state(False)

    # def hit_rollover_button(self):
    #     self.hit_and_release_switch('s_rollover_button')
    #     self.advance_time_and_run(5)

    # def start_hurry_up(self):
    #     self.hit_switch_and_run('s_drop_top', 1)
    #     self.hit_switch_and_run('s_drop_middle', 1)
    #     self.hit_switch_and_run('s_drop_bottom', 1)

    # def assertHurryUpTimerRunning(self, is_running):
    #     self.assertEqual(self.machine.timers.drop_hurry_up.running, is_running)

    # def test_hurry_up_times_out(self):
    #     self.setup()

    #     self.start_hurry_up()
    #     self.assertStateMachineState(STATE, STATE_HURRY_UP_ACTIVE)

    #     self.assertHurryUpTimerRunning(True)
    #     self.assertStateMachineState(STATE, STATE_HURRY_UP_ACTIVE)
    #     self.assertShotState(ROLLOVER_SHOT, ROLLOVER_SHOT_LIT_INDEX)

    #     self.advance_time_and_run(40)

    #     self.assertStateMachineState(STATE, STATE_HURRY_UP_INACTIVE)
    #     self.assertShotState(ROLLOVER_SHOT, ROLLOVER_SHOT_UNLIT_INDEX)
    #     self.assertHurryUpTimerRunning(False)
    #     self.assertEventCalled(EVENT_RESET_DROP, 1)

    # def test_collects_hurry_up(self):
    #     self.setup()

    #     self.start_hurry_up()
    #     self.assertHurryUpTimerRunning(True)
    #     self.assertStateMachineState(STATE, STATE_HURRY_UP_ACTIVE)
    #     self.assertShotState(ROLLOVER_SHOT, ROLLOVER_SHOT_LIT_INDEX)
    #     self.hit_rollover_button()
    #     self.assertEventCalled(EVENT_RESET_DROP, 1)

    #     self.assertHurryUpTimerRunning(False)
    #     self.assertStateMachineState(STATE, STATE_HURRY_UP_INACTIVE)
    #     self.assertShotState(ROLLOVER_SHOT, ROLLOVER_SHOT_UNLIT_INDEX)

    # def test_drains_while_hurry_up_is_active(self):
    #     self.setup()

    #     self.start_hurry_up()
    #     self.advance_time_and_run(10)
    #     self.assert_drops_state('s_drop_top', True)
    #     self.assert_drops_state('s_drop_middle', True)
    #     self.assert_drops_state('s_drop_bottom', True)

    #     self.drain_to_next_ball()

    #     # make sure timer is reset completely to its start value
    #     start_value = self.machine.timers.drop_hurry_up.start_value
    #     ticks = self.machine.timers.drop_hurry_up.ticks
    #     self.assertEqual(start_value, ticks)

    #     self.assertStateMachineState(STATE, STATE_HURRY_UP_INACTIVE)
    #     self.assertHurryUpTimerRunning(False)
    #     self.assert_drops_state('s_drop_top', False)
    #     self.assert_drops_state('s_drop_middle', False)
    #     self.assert_drops_state('s_drop_bottom', False)

    # def test_start_mode_while_hurry_up_is_active(self):
    #     self.setup()
    #     self.start_hurry_up()
    #     ticks_before_song = self.machine.timers.drop_hurry_up.ticks
        
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

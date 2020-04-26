from tests.mode_test_case import ModeTestCase
from modes.urge.code.urge import (
    EVENT_CODE_COLLECTED_HURRY_UP,
    SHOTS,
    LIT_SHOT_INDEX,
    UNLIT_SHOT_INDEX,
)

EVENT_RESET_DROPS = 'drops_state_reset_bank'
EVENT_SHOW_COLLECTED_COMPLETED = 'urge_show_collected_completed'
URGE = 'urge'

class TestUrge(ModeTestCase):

    def setup(self):
        self.setup_game()
        self.assertModeNotRunning(URGE)
        self.knockdown_drops()
        self.assertModeRunning(URGE)

    def assertHurryUpTimerRunning(self, is_running):
        self.assertEqual(self.machine.timers.urge_hurry_up.running, is_running)

    def assert_shots(self, lit_shot_index):
        """ 
        Test that shot at lit_shot_index is lit while others are unlit
        """
        for i, shot in enumerate(SHOTS):
            if i == lit_shot_index:
                self.assertShotState(shot, LIT_SHOT_INDEX)
            else:
                self.assertShotState(shot, UNLIT_SHOT_INDEX)

    def test_lights_a_hurry_up_shot(self):
        self.setup()
        lit_shot_index = self.machine.game.player.urges_collected
        self.assert_shots(lit_shot_index)

    def test_collecting_hurry_up(self):
        first_lit_shot_hit_event = SHOTS[0] + '_hit'
        self.mock_event(first_lit_shot_hit_event)
        second_lit_shot_hit_event = SHOTS[1] + '_hit'
        self.mock_event(first_lit_shot_hit_event)
        self.mock_event(EVENT_CODE_COLLECTED_HURRY_UP)
        self.mock_event(EVENT_SHOW_COLLECTED_COMPLETED)
        self.setup()

        # TODO: this requires implicit knowledge of the switches associated with shots, should refactor
        self.hit_and_release_switch('s_ramp_left_lower')
        self.reset_drops()
        self.advance_time_and_run(2)

        self.assertEventCalled(EVENT_SHOW_COLLECTED_COMPLETED, 1)
        self.assertModeNotRunning(URGE)


        self.drain_one_ball()
        self.advance_time_and_run(1)
        self.advance_time_and_run(1)
        self.knockdown_drops()
        self.advance_time_and_run(1)

        self.assertEqual('start', self.machine.state_machines.drops.state)
        self.assertModeRunning(URGE)
        # self.post_event('sh_orbit_left_hit')
        # self.advance_time_and_run(2)
        # self.assertEventCalled(EVENT_SHOW_COLLECTED_COMPLETED, 2)
        # self.assertModeNotRunning(URGE)

    def test_hitting_unlit_shot_does_nothing(self):
        unlit_shot = SHOTS[1]
        unlit_shot_hit_event = SHOTS[1] + '_hit'
        self.mock_event(unlit_shot_hit_event)
        self.setup()

    def test_hurry_up_times_out_if_not_collected(self):
        self.setup()

        # drops are down
        self.assert_drops_state(True)
        self.advance_time_and_run(40)
        self.assertModeNotRunning(URGE)
        self.assert_drops_state(False)

    def test_hurry_up_shot_is_cycled_when_collected():
        pass



        # self.assertStateMachineState(STATE, STATE_HURRY_UP_INACTIVE)
        # self.assertShotState(ROLLOVER_SHOT, ROLLOVER_SHOT_UNLIT_INDEX)
        # self.assertHurryUpTimerRunning(False)
        # self.assertEventCalled(EVENT_RESET_DROPS, 1)

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

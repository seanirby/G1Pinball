from tests.mode_test_case import ModeTestCase
from modes.urge.code.urge import (
    EVENT_CODE_COLLECTED_HURRY_UP,
    SHOTS,
    LIT_SHOT_INDEX,
    UNLIT_SHOT_INDEX,
)

EVENT_TIMER_COMPLETED = 'timer_urge_complete'
EVENT_DROPS_DOWN = 'drop_target_bank_drops_down'
EVENT_RESET_DROPS = 'drops_state_reset_bank'
EVENT_SHOW_COLLECTED_COMPLETED = 'urge_show_collected_completed'
URGE = 'urge'

class TestUrge(ModeTestCase):

    def setup(self):
        self.setup_game()
        self.assertModeNotRunning(URGE)
        self.post_event(EVENT_DROPS_DOWN)
        self.assertModeRunning(URGE)

    def assertHurryUpTimerRunning(self, is_running):
        self.assertEqual(self.machine.timers.urge.running, is_running)

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
        self.post_event(EVENT_DROPS_DOWN)
        self.advance_time_and_run(10)

        self.assertEventCalled(EVENT_SHOW_COLLECTED_COMPLETED, 1)
        self.assertModeNotRunning(URGE)

        self.drain_one_ball()
        self.advance_time_and_run(5)
        self.assertEqual('start', self.machine.state_machines.drops.state)
        self.assertModeNotRunning(URGE)
        self.post_event(EVENT_DROPS_DOWN)
        self.advance_time_and_run(2)
        self.assertModeRunning(URGE)

        self.post_event('sh_orbit_left_hit')
        self.advance_time_and_run(10)
        self.assertEventCalled(EVENT_SHOW_COLLECTED_COMPLETED, 2)
        self.assertModeNotRunning(URGE)

    def test_hitting_unlit_shot_does_nothing(self):
        unlit_shot = SHOTS[1]
        unlit_shot_hit_event = SHOTS[1] + '_hit'
        self.mock_event(unlit_shot_hit_event)
        self.mock_event(EVENT_CODE_COLLECTED_HURRY_UP)
        self.setup()
        self.post_event(EVENT_DROPS_DOWN)
        self.advance_time_and_run(2)

        self.post_event('sh_orbit_left_hit')
        self.advance_time_and_run(5)
        self.assertEventCalled(EVENT_CODE_COLLECTED_HURRY_UP, 0)

    def test_hurry_up_times_out_if_not_collected(self):
        self.setup()
        self.mock_event(EVENT_TIMER_COMPLETED)
        self.mock_event(EVENT_CODE_COLLECTED_HURRY_UP)

        self.advance_time_and_run(40)
        self.assertEventCalled(EVENT_TIMER_COMPLETED, 1)
        self.assertModeNotRunning(URGE)
        self.assertEventNotCalled(EVENT_CODE_COLLECTED_HURRY_UP)

    def test_drains_while_hurry_up_is_active(self):
        self.setup()
        self.mock_event(EVENT_TIMER_COMPLETED)
        self.mock_event(EVENT_CODE_COLLECTED_HURRY_UP)

        self.advance_time_and_run(5)
        self.drain_one_ball()
        self.advance_time_and_run(5)
        self.post_event(EVENT_DROPS_DOWN)
        self.advance_time_and_run(5)

        self.mock_event(EVENT_CODE_COLLECTED_HURRY_UP)
        self.assertShotState(SHOTS[0], LIT_SHOT_INDEX)

    def test_start_mode_while_hurry_up_is_active(self):
        self.setup()
        self.qualify_song()
        self.assertHurryUpTimerRunning(True)

        self.hit_switch_and_run('s_scoop', 3)

        self.assertHurryUpTimerRunning(False)

        self.advance_time_and_run(3)
        self.assertHurryUpTimerRunning(True)
        self.assertStateMachineState(URGE, 'start')

    def test_for_multiple_players(self):
        pass


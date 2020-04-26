from tests.mode_test_case import ModeTestCase

# TODO: refactor and reformat this file so its consistent with other tests
class TestChargedFlips(ModeTestCase):

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
        self.setup_game()
        self.assertModeRunning('charged_flips')

        # erergy should be 0
        self.assertEqual(self.machine.game.player_list[0].energy, 0)
        

    def _energy_up(self, amt):
        for i in range(amt):
            self.hit_and_release_switch("s_right_inlane")

    def test_not_enough_energy(self):
        self._setup_game()
        # cant charge with 0 energy
        self.hit_and_release_switch("s_charge_right")
        # check that timer is not running
        self.assertFalse(self.machine.timers['charging_timer'].running)

    def test_increase_energy(self):
        self._setup_game()
        # hitting right inlane increases energy by 1
        self._energy_up(1)
        self.assertEqual(self.machine.game.player_list[0].energy, 1)
        # hitting left inlane increases energy by 1
        self._energy_up(1)
        self.assertEqual(self.machine.game.player_list[0].energy, 2)

    def test_premature_charge(self):
        self._setup_game()
        # need at least 3 energy before you can charge
        self._energy_up(3)
        self.assertEqual(self.machine.game.player_list[0].energy, 3)
        # check that timer is not running
        self.assertFalse(self.machine.timers['charging_timer'].running)

        self.hit_and_release_switch("s_charge_right")
        self.assertTrue(self.machine.timers['charging_timer'].running)

        # flipping immediately will cancel charging and players energy will be unchanged and players energy will NOT be used
        self.hit_and_release_switch("s_right_flipper")
        self.assertFalse(self.machine.timers['charging_timer'].running)
        self.assertFalse(self.machine.timers['charge_release_timer'].running)
        self.assertEqual(self.machine.game.player_list[0].energy, 3)

    def test_charge_single_level(self):
        self._setup_game()
        # need at least 3 energy before you can charge
        self._energy_up(3)
        self.assertEqual(self.machine.game.player_list[0].energy, 3)
        # check that timer is not running
        self.assertFalse(self.machine.timers['charging_timer'].running)

        # charging for enough time and flipping uses up 3 energy
        self.hit_and_release_switch("s_charge_right")
        self.assertTrue(self.machine.timers['charging_timer'].running)
        self.advance_time_and_run(10)
        self.hit_and_release_switch("s_right_flipper")
        self.assertFalse(self.machine.timers['charging_timer'].running)
        self.assertTrue(self.machine.timers['charge_release_timer'].running)
        # 2x multiplier while charge_release_timer is running
        self.assertEqual(self.machine.modes['charged_flips'].current_multiplier, 2)
        self.assertEqual(self.machine.game.player_list[0].energy, 0)

        # charge release timer is only active for a short time
        self.advance_time_and_run(2)
        self.assertFalse(self.machine.timers['charge_release_timer'].running)
        # multiplier is back down to 1
        self.assertEqual(self.machine.modes['charged_flips'].current_multiplier, 1)

    def test_charge_two_levels(self):
        self._setup_game()

        # bring up to 6
        self._energy_up(6)
        self.assertEqual(self.machine.game.player_list[0].energy, 6)

        # charge enough to get a 3x multiplier
        self.hit_and_release_switch("s_charge_right")
        self.assertTrue(self.machine.timers['charging_timer'].running)
        self.advance_time_and_run(10)
        self.hit_and_release_switch("s_right_flipper")
        self.assertFalse(self.machine.timers['charging_timer'].running)
        self.assertTrue(self.machine.timers['charge_release_timer'].running)
        # 3x multiplier while charge_release_timer is running
        self.assertEqual(self.machine.modes['charged_flips'].current_multiplier, 3)
        self.assertEqual(self.machine.game.player_list[0].energy, 0)

    def test_charge_three_levels(self):
        self._setup_game()

        # bring up to 9
        self._energy_up(9)
        self.assertEqual(self.machine.game.player_list[0].energy, 9)

        # charge enough to get a 4x multiplier
        self.hit_and_release_switch("s_charge_right")
        self.assertTrue(self.machine.timers['charging_timer'].running)
        self.advance_time_and_run(20)
        self.hit_and_release_switch("s_right_flipper")
        self.assertFalse(self.machine.timers['charging_timer'].running)
        self.assertTrue(self.machine.timers['charge_release_timer'].running)

        # 4x multiplier while charge_release_timer is running
        self.assertEqual(self.machine.modes['charged_flips'].current_multiplier, 4)
        self.assertEqual(self.machine.game.player_list[0].energy, 0)


    def test_partial_charge(self):
        # charge up to 4x but only use 2x
        self._setup_game()

        # bring up to 9
        self._energy_up(9)
        self.assertEqual(self.machine.game.player_list[0].energy, 9)

        # charge enough to get a 2x multiplier
        self.hit_and_release_switch("s_charge_right")
        self.assertTrue(self.machine.timers['charging_timer'].running)
        self.advance_time_and_run(3)
        self.hit_and_release_switch("s_right_flipper")
        self.assertFalse(self.machine.timers['charging_timer'].running)
        self.assertTrue(self.machine.timers['charge_release_timer'].running)

        # 4x multiplier while charge_release_timer is running
        self.assertEqual(self.machine.modes['charged_flips'].current_multiplier, 2)
        self.assertEqual(self.machine.game.player_list[0].energy, 6)

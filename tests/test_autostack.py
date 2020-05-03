import unittest
from tests.mode_test_case import ModeTestCase

class TestAutostack(ModeTestCase):
    pass
#     def test_shows_are_autostacked(self):
#         "When modes are active their autostacked shot shows should be cycled through"
#         self.setUp()
#         self.start_game()
#         self.assertModeRunning('song_select')
#         self.assertModeRunning('foo')
#         autostack = self.machine.modes.autostack
#         monitored_modes = autostack.monitored_modes
#         # assert initial state
#         self.assertEqual(len(monitored_modes), 2)
        
#         self.advance_time_and_run(1)
#         self.post_event('timer_autostack_tick')
#         self.post_event('timer_autostack_tick')
#         self.post_event('timer_autostack_tick')


#         # # modes should be started so check that 
#         # active_mode = autostack.active_mode
#         # active_modes = autostack.active_modes
#         # self.assertEqual(autostack.active_mode, 'foo')
#         # self.assertEqual(active_modes.index(active_mode), 0)
#         # self.assertEqual(len(active_modes), 2)

#         # shows will cycle

#         # self.assertFalse(bool(self.machine.shots.sh_song_select_bash_center.running_show))
#         # self.assertTrue(bool(self.machine.shots.sh_bash_center.running_show))
#         # self.assertNotEqual(self.machine.shots.sh_bash_center.running_show.show, self.machine.shows['off'])

# #unittest.main()                 # 

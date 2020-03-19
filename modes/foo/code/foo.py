from mpf.core.mode import Mode

# done - next red shot is automatically moved clockwise when a shit is made
# you have X seconds to hit the red shot
# after X seconds the red shot is gone for good!
# if the bash is hit then then the RED timer is reset


class Foo(Mode):
    num_shots = 10
    starting_high_value_shot = "ramp_left_lower"
    high_value_state = "high_value"
    complete_state = "complete"
    complete_state_index = 2
    shot_names = [
        "ramp_left_lower",
        "rollover_button",
        "orbit_left",
        "ramp_left_upper",
        "zone_left",
        "gate_right",
        "inner_loop",
        "scoop",
        "ramp_right",
        "orbit_right"
    ]

    def mode_init(self):
        print("My custom mode code is being initialized")

    def mode_start(self, **kwargs):
        self.high_value_shot_disabled = False
        self.machine.shots[self.starting_high_value_shot].advance()
        self.add_mode_event_handler("s_bash_left_active", self.advance, 0, direction=1)
        self.add_mode_event_handler("s_bash_right_active", self.advance, 0, direction=-1)
        # shot hit handlers
        self.add_mode_event_handler("s_ramp_left_lower_active", self.shot_hit, 0, shot="ramp_left_lower")
        self.add_mode_event_handler("s_rollover_button_active", self.shot_hit, 0, shot="rollover_button")

        self.add_mode_event_handler("seq_orbit_left_hit", self.shot_hit, 0, shot="orbit_left")
        self.add_mode_event_handler("s_ramp_left_upper_active", self.shot_hit, 0, shot="ramp_left_upper")
        self.add_mode_event_handler("s_zone_left_center_active", self.shot_hit, 0, shot="zone_left")
        self.add_mode_event_handler("s_gate_right_active", self.shot_hit, 0, shot="gate_right")
        self.add_mode_event_handler("s_inner_loop_active", self.shot_hit, 0, shot="inner_loop")
        self.add_mode_event_handler("s_scoop_active", self.shot_hit, 0, shot="scoop")
        self.add_mode_event_handler("s_ramp_right_active", self.shot_hit, 0, shot="ramp_right")
        self.add_mode_event_handler("seq_orbit_right_hit", self.shot_hit, 0, shot="orbit_right")
        # self.add_mode_event_handler("timer_high_value_shot_timer_complete", self.disable_high_value_shot)
        # self.add_mode_event_handler("timer_high_value_shot_timer_tick", self.speed_up_high_value_show)

        
    @staticmethod
    def rotate(l, n):
        return l[n:] + l[:n]

    # def speed_up_high_value_show(self, **kwargs):
    #     pass
    #     # import pdb; pdb.set_trace()

    def is_remaining_shot(self, shot):
        is_complete = shot.state_name == self.complete_state
        return not is_complete

    def shot_hit(self, **kwargs):
        # if im 'disabled' do nothing

        shot = self.machine.shots[kwargs["shot"]]
#        import pdb; pdb.set_trace()
        if self.is_remaining_shot(shot):
            if shot.state_name == self.high_value_state:
                self.advance(direction=1)
            shot.jump(self.complete_state_index)

    def disable_high_value_shot(self, **kwargs):
        for shot in self.machine.shots:
            if shot.state_name == self.high_value_state:
                shot.reset()
                break
            
        self.high_value_shot_disabled = True

    def advance(self, **kwargs):
        if self.high_value_shot_disabled:
            return

        # self.machine.timers.high_value_shot_timer.reset()

        direction = kwargs["direction"]
        # selection_group will contain all remaining shots in the mode
        # AND any disabled shots that have the 'high_value' state
        # selector on them
        selection_group = []
        shots = self.machine.shots

        # collect remaining shots and current 
        current_high_value_shot = None

        for i, shot_name in enumerate(self.shot_names):
            shot = shots[shot_name]
            on_high_value = shot.state_name ==self.high_value_state

            if self.is_remaining_shot(shot):
                selection_group.append(shot)
            if on_high_value:
                current_high_value_shot = shot
        
#        import pdb; pdb.set_trace()
        if self.is_remaining_shot(current_high_value_shot):
            current_high_value_shot.reset()

        current_high_value_shot_index = selection_group.index(current_high_value_shot)
        self.rotate(selection_group, direction)[current_high_value_shot_index].advance()


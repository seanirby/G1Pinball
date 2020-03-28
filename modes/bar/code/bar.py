from mpf.core.mode import Mode

class Bar(Mode):
    def __init__(self, *args, **kwargs):
        """Initialize bonus mode."""
        super().__init__(*args, **kwargs)

    def mode_start(self, **kwargs):
        self.add_mode_event_handler("s_ramp_right_active", self.ramp_hit, side="right")
        self.add_mode_event_handler("s_ramp_left_lower_active", self.ramp_hit, side="left")

        self.add_mode_event_handler("s_bash_forward_active", self.bash_hit, side="center")  
        self.add_mode_event_handler("s_bash_left_active", self.bash_hit, side="left")
        self.add_mode_event_handler("s_bash_right_active", self.bash_hit, side="right")
        self.add_mode_event_handler('timer_bar_bash_timer_tick', self.bar_bash_timer_tick)
        self.add_mode_event_handler('timer_bar_bash_timer_complete', self.bash_timer_complete)

        self.add_mode_event_handler('bar_start_started', self.bar_state_machine_started)


    def bar_state_machine_started(self, **kwargs):
        bar_bash_timer = self.machine.timers['bar_bash_timer']

        self.machine.counters.bar_ramp_count.reset()
        self.machine.shots['bar_ramp_right'].jump(0)
        self.machine.shots['bar_ramp_left_lower'].jump(0)

        bar_bash_timer.stop()
        bar_bash_timer.reset()
        self.machine.shots['bar_bash'].jump(0)


    def bash_timer_complete(self, **kwargs):
        pass

    def bar_bash_timer_tick(self, **kwargs):
        bar_bash = self.machine.shots['bar_bash']

        if bar_bash.state == 1:
            bar_bash.advance()
        else:
            bar_bash.jump(1)

    def ramp_hit(self, **kwargs):
        side = kwargs['side']
        bar_state = self.machine.state_machines['bar']
        bar_bash_timer = self.machine.timers['bar_bash_timer']

        if bar_state.state == 'start':
            bar_bash_timer.start()
            # start bash timer
            if side == 'right':
                self.machine.events.post('bar_right_hit')
                self.machine.shots['bar_ramp_right'].jump(1)
                self.machine.shots['bar_ramp_left_lower'].jump(0)
            else:
                self.machine.events.post('bar_left_hit')
                self.machine.shots['bar_ramp_right'].jump(0)
                self.machine.shots['bar_ramp_left_lower'].jump(1)
        elif bar_state.state == 'left_ramp_lit' and side == 'left':
            bar_bash_timer.restart()
            self.machine.events.post('bar_left_hit')
            self.machine.shots['bar_ramp_right'].jump(0)
            self.machine.shots['bar_ramp_left_lower'].jump(1)
        elif bar_state.state == 'right_ramp_lit' and side == 'right':
            bar_bash_timer.restart()
            self.machine.events.post('bar_right_hit')
            self.machine.shots['bar_ramp_right'].jump(1)
            self.machine.shots['bar_ramp_left_lower'].jump(0)

    def bash_hit(self, **kwargs):
        side = kwargs['side']
        bar_state = self.machine.state_machines['bar']
        bar_bash_timer = self.machine.timers['bar_bash_timer']
        counter = self.machine.counters['bar_ramp_count'].count

        if bar_state.state == 'left_ramp_lit' or bar_state.state == 'right_ramp_lit':
            # collect all ramps lit
            self.machine.events.post('bar_collect_ramp_hits')
            count = self.machine.counters.bar_ramp_count.value
            self.player.score += 1000000*count
            self.machine.counters.bar_ramp_count.reset()
        
        
        
    
    

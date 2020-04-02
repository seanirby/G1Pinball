from mpf.core.mode import Mode

# - test that charging timer works

class ChargedFlips(Mode):
    # We dont want players charging if they only have a bit of energy
    min_energy_value_to_begin_charging = 3
    flipper_down_delay = 200
    
    def mode_init(self):
        # probably a much better way to define instance variables
        self.is_charging = None
        self._current_multiplier = 1
        self.charge_starting_energy = 0
        

    @property
    def current_multiplier(self):
        """Return current_multiplier."""
        return self._current_multiplier


    def mode_start(self, **kwargs):
        self.charge_starting_energy = 0
        self.add_mode_event_handler("s_charge_right_active", self.charge_pressed, side="right")
        self.add_mode_event_handler("s_charge_left_active", self.charge_pressed, side="left")
        self.add_mode_event_handler('player_charged_flips_charging_timer_tick', self.charging_tick)

        self.add_mode_event_handler('s_right_flipper_active', self.flipper_pressed, side="right")
        self.add_mode_event_handler('s_left_flipper_active', self.flipper_pressed, side="left")
        self.add_mode_event_handler('timer_charge_release_timer_complete', self.reset_multiplier)

    def reset_multiplier(self, **kwargs):
        self._current_multiplier = 1

    # If my respective flipper is pressed while I'm charging 
    def flipper_pressed(self, **kwargs):
        side = kwargs['side']
        if self.is_charging == side:
            self.is_charging = None
            self.machine.events.post('charging_stopped')

            charging_timer = self.machine.timers['charging_timer']
            charging_timer.stop()
            charging_timer.reset()

            self.machine.counters.energy.enable()
            
            # only fire off the charge release if I have a charged up multiplier
            if self._current_multiplier > 1:
                self.machine.timers['charge_release_timer'].restart()
                ticks = charging_timer.ticks
                # 
                if self._current_multiplier == 2:
                    self.player.energy = max(self.player.energy - 3, 0)
                elif self._current_multiplier == 3:
                    self.player.energy = max(self.player.energy - 6, 0)
                else:
                    self.player.energy = 0
            else:
                self._current_multiplier = 1

    def charge_pressed(self, **kwargs):
        side = kwargs['side']
        # here we decide whether to begin charging
        # we DONT want to charge if any of the following are true
        # play a short dismissal sound if any of these conditions are met

        # - i dont energy!
        if self.player.energy < self.min_energy_value_to_begin_charging:
            return
        # - another side is already charging
        elif self.is_charging:
            # dont play sound
            return
        # - my respective flipper is up
        elif not self.is_respective_flipper_down(side):
            return
        # while unlikely there should be no reason the player can charge while waiting for a charged shot to complete
        elif self.machine.timers['charge_release_timer'].running:
            return
        # - maybe if im in some cool down period quickly after a previous charge was completed

        # kickoff charging timer
        self.machine.events.post('charging_started')
        self.is_charging = side
        # # ensure we start timer at 0
        self.machine.timers['charging_timer'].restart()

    # check that my respective flipper is down and has been down for a bit of time
    def is_respective_flipper_down(self, side):
        s_flipper = 's_right_flipper' if side == 'right' else 's_left_flipper'
        return self.machine.switch_controller.is_state(s_flipper, False, self.flipper_down_delay)

    def charging_tick(self, **kwargs):
        timer = self.machine.timers['charging_timer']
        
        if timer.ticks >= 9 and self.player.energy >= 9:
            self._current_multiplier = 4
        elif timer.ticks >= 6 and timer.ticks < 9 and self.player.energy >= 6:
            self._current_multiplier = 3
        elif timer.ticks >= 3 and timer.ticks < 6 and self.player.energy >= 3:
            self._current_multiplier = 2



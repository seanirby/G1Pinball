from modes.base_mode import BaseMode

BASE_VALUE = 250000

class Urge(BaseMode):
    def mode_start(self, **kwargs):
        super().mode_start(**kwargs)
        self.add_mode_event_handler('urge_collected', self.collected)
        self.add_mode_event_handler('urge_display_collected', self.display_collected)

    def collected(self, **kwargs):
        self.player.score += self.get_amount_collected()

    def display_collected(self, **kwargs):
        amt_collected = self.get_amount_collected()
        row_one = "UNCONTROLLABLE".ljust(16, "!")
        row_two = ("URGE!+"+format(amt_collected, ',d')).ljust(16, "!")
        self.display.set_vars(r1=row_one, r2=row_two)

    def get_amount_collected(self):
        return self.machine.counters.urge.value * BASE_VALUE
        
    

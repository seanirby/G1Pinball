EMPTY_CHAR = '!'
ALL_ON_CHAR = '~'

ROWS = 2
ROW_LENGTH = 16
TOTAL_LENGTH = ROWS * ROW_LENGTH
CHAR_SET = [34,36,37,38,39,40,41,42,43,44,45,47,48,49,50,51,52,53,54,55,56,57,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,92,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,124,126,165,166,176,177] 

FLASH_TIMER = 'base_flash'
EVENT_FLASH_START = 'base_flash_start'

class Display():
    """
    This class is used to print to a mode's slide
    """

    def __init__(self, machine, mode_name):
        self.machine = machine
        self._first_row_name = 'd_{}_1'.format(mode_name)
        self._second_row_name = 'd_{}_2'.format(mode_name)

    def flash(self, **kwargs):
        seconds = kwargs.get('seconds')
        timer = self.machine.timers[FLASH_TIMER]
        timer.end_value = int(seconds*10) if seconds else 10
        self.machine.events.post(EVENT_FLASH_START)

    def prnt(self, string, i_start, i_lower, i_upper, repeat=False):
        string = str(string)
        first_row = self.machine.variables.get_machine_var(self._first_row_name)
        second_row = self.machine.variables.get_machine_var(self._second_row_name)
        buff = list(first_row + second_row)

        word_len = len(string)
        i_end = i_start + word_len
        # offset index to access word character
        i_word = None
        for j in range(i_lower, i_upper):
            # the modulo lets us wrap text
            if repeat:
                i_word = (j - i_start) % word_len
                buff[j] = string[i_word]
            else:
                if i_start <= j < i_end:
                    i_word = j - i_start
                    buff[j] = string[i_word]

        self.machine.variables.set_machine_var(self._first_row_name, ''.join(buff[:16]))
        self.machine.variables.set_machine_var(self._second_row_name, ''.join(buff[16:]))

    def set_vars(self, **kwargs):
        self.machine.variables.set_machine_var(self._first_row_name, kwargs['r1'])
        self.machine.variables.set_machine_var(self._second_row_name, kwargs['r2'])

    def set_vars_format(self, **kwargs):
        row_one_format_str = kwargs.get("r1")
        row_two_format_str = kwargs.get("r2")

        row_one_player_var = kwargs.get("r1_player_var")
        row_two_player_var = kwargs.get("r2_player_var")

        row_one_arg = '' if not(bool(row_one_player_var)) else self.machine.game.player[row_one_player_var]
        row_two_arg = '' if not(bool(row_two_player_var)) else self.machine.game.player[row_two_player_var]

        row_one_formatted = row_one_format_str.format(row_one_arg)
        row_two_formatted = row_two_format_str.format(row_two_arg)

        self.machine.variables.set_machine_var(self._first_row_name, row_one_formatted)
        self.machine.variables.set_machine_var(self._second_row_name, row_two_formatted)

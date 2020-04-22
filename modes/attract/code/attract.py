from mpf.core.mode import Mode

EMPTY_CHAR = '!'
ALL_ON_CHAR = '~'
DISPLAY_ROWS = 2
DISPLAY_COLUMNS = 16
DISPLAY_FIRST_ROW = 0
DISPLAY_SECOND_ROW = DISPLAY_COLUMNS
DISPLAY_LENGTH = DISPLAY_ROWS * DISPLAY_COLUMNS
CHAR_SET = [34,36,37,38,39,40,41,42,43,44,45,47,48,49,50,51,52,53,54,55,56,57,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,92,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,124,126,165,166,176,177] 

WORD_PRESS_START = list(list('PRESS') + [EMPTY_CHAR]*1 + list('START') + [EMPTY_CHAR]*5)

class Attract(Mode):
    def mode_start(self, **kwargs):
        self._i = 0
        self._j = 0
        self._k = 0
        self._l = 0

        self._state = 'start'
        # self.add_mode_event_handler('timer_attract_ticker_tick', self.handle_tick)
        # self.add_mode_event_handler('timer_attract_ticker_complete', self.handle_timeout)
        # self.machine.events.post('state_attract_start_started')

    def handle_timeout(self, **kwargs):
        state = self._state

        self.clear_display()
        self._i = 0;
        self._j = 0;

        if state == 'start':
            self._state = 'wave'
            self.machine.events.post('state_attract_wave_started')
        elif state == 'wave':
            self._state = 'character_count'
            self.machine.events.post('state_attract_character_count_started')
        elif state == 'character_count':
            self._state = 'start'
            self.machine.events.post('state_attract_start_started')

    def handle_tick(self, **kwargs):
        state = self._state
        # self.handle_wave_tick()

        # if state == 'start':
        #     self.handle_start_tick()
        # elif state == 'wave':
        #     self.handle_wave_tick()
        # elif state == 'character_count':
        #     self.handle_character_count_tick()

    def handle_start_tick(self):
        self.machine.variables.set_machine_var("d{0}".format(self._i), self.get_char_from_set(self._j))

        next_i = (self._i + 1) % (DISPLAY_LENGTH)
        self._i = next_i
        if next_i == 0:
            self._j = (self._j + 1) % (len(CHAR_SET))

    def handle_wave_tick(self):
        self.print_word(WORD_PRESS_START, self._i, 0, DISPLAY_COLUMNS, '!')
        self.print_word(WORD_PRESS_START, -self._i + DISPLAY_SECOND_ROW + 6, DISPLAY_SECOND_ROW, DISPLAY_SECOND_ROW + DISPLAY_COLUMNS, True)

        next_i = (self._i + 1) % (DISPLAY_LENGTH)
        self._i = next_i

    def handle_character_count_tick(self):
        next_i = None
        if self._i < DISPLAY_COLUMNS:
            self.print_word(['!', '>', '!'], self._i, 0, DISPLAY_SECOND_ROW)
            # self.print_display_char('>', self._i)
            next_i = self._i + 1
            if next_i == DISPLAY_COLUMNS:
                next_i = DISPLAY_LENGTH
        else:
            self.print_word(['!', '<', '!'], self._i - 2, DISPLAY_SECOND_ROW, DISPLAY_LENGTH)

            next_i = self._i - 1
            if next_i < DISPLAY_SECOND_ROW:
                next_i = DISPLAY_FIRST_ROW
        
        self._i = next_i


    def print_display_char(self, char, i):
        first_row = self.machine.variables.get_machine_var('d_test_first')
        second_row = self.machine.variables.get_machine_var('d_test_second')
        together = list(first_row + second_row)

        together[i] = char

        self.machine.variables.set_machine_var('d_test_first', ''.join(together[:16]))
        self.machine.variables.set_machine_var('d_test_second', ''.join(together[16:]))

        # if self.machine.variables.get_machine_var(name) != char:
        #     self.machine.variables.set_machine_var(name, char)

    # def print_display_char(self, char, i):
    #     name = "d{0}".format(i)
    #     if self.machine.variables.get_machine_var(name) != char:
    #         self.machine.variables.set_machine_var(name, char)
    

    def print_word(self, word, i_start, i_lower, i_upper, repeat=False):
        first_row = self.machine.variables.get_machine_var('d_test_first')
        second_row = self.machine.variables.get_machine_var('d_test_second')
        buff = list(first_row + second_row)

        word_len = len(word)
        i_end = i_start + word_len
        # offset index to access word character
        i_word = None
        for j in range(i_lower, i_upper):
            # the modulo lets us wrap text
            if repeat:
                i_word = (j - i_start) % word_len
                buff[j] = word[i_word]
            else:
                if i_start <= j < i_end:
                    i_word = j - i_start
                    buff[j] = word[i_word]

        self.machine.variables.set_machine_var('d_test_first', ''.join(buff[:16]))
        self.machine.variables.set_machine_var('d_test_second', ''.join(buff[16:]))

    # def print_word(self, word, i_start, i_lower, i_upper, repeat=False):
    #     """
    #     Print out all the characters in the list 'word' to the display, starting at index 'i'.

    #     Bounds for the print operation can be set with the i_lower and
    #     i_upper arguments.  If i_start is out of bounds then no print will
    #     occur at that index.  i_lower is inclusive while i_upper is
    #     exclusive in following with Python convention.  Ex: range(i_lower, i_upper)

    #     The fill_leftover arg is a character that will be printed for
    #     any value of i that is both in bounds AND does not align with
    #     the word printout. For example

    #     print_word(['F', 'O', 'O'], 1, 0, 4, '#') would result in the following output:
    #     # F O O
    #     """

    #     word_len = len(word)
    #     i_end = i_start + word_len
    #     # offset index to access word character
    #     i_word = None
    #     for j in range(i_lower, i_upper):
    #         # the modulo lets us wrap text
    #         if repeat:
    #             i_word = (j - i_start) % word_len
    #             self.print_display_char(word[i_word], j)
    #         else:
    #             if i_start <= j < i_end:
    #                 i_word = j - i_start
    #                 self.print_display_char(word[i_word], j)

    #         # if i <= j < word_upper:
    #         #     j_wrapped = (j - i)
    #         #     self.print_display_char(word[j_wrapped], j)
    #         # else:
    #         #     self.print_display_char(fill_leftover, j)

    def clear_display(self):
        for i in range(0, 32):
            self.print_display_char(EMPTY_CHAR, i)

    def get_char_from_set(self, i):
        return chr(CHAR_SET[i])

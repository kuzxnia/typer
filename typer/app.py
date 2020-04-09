from __future__ import division

import curses
import logging
from time import time

from typer.util.common_words import common_words_from_range
from typer.util.statistic import accuracy, cpm, wpm

logging.basicConfig(
    filename="typer.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)
log = logging.getLogger(__name__)


class Game:
    def __init__(self):
        log.info("init board")
        self.stdscr = curses.initscr()
        curses.cbreak()
        curses.noecho()

        # Clear and refresh the screen for a blank canvas
        self.stdscr.clear()
        self.stdscr.refresh()

        self.init_colors()

        self.quit = False
        self.periods = []

        self.init_words()
        self.detect_window_size_change()
        log.info("init board ended successfully")

    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, 239)  # white on dark gray
        curses.init_pair(4, 48, curses.COLOR_BLACK)  # green on default
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(6, curses.COLOR_WHITE, 242)  # white on dark gray

    def init_words(self):
        # self.words = list(chain.from_iterable(drow_words("en", 50) for _ in range(rows_amount)))
        self.words = common_words_from_range("en", 0, 10)
        self.answers = []
        self.current_word = 0
        self.current_row = 0
        self.correct_words_ids = []
        self.incorrect_words_ids = []

    def __del__(self):
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def iter_words(self):
        current_row_len = 0
        row_index = 0
        for i, word in enumerate(self.words):
            if current_row_len + len(word) <= 50:
                current_row_len += len(word)
            else:
                row_index += 1
                current_row_len = len(word)

            yield row_index, i, word

    def is_first_in_row(self, index):
        last_row = -1
        for row_index, word_index, _ in self.iter_words():
            if last_row != row_index:
                last_row = row_index
                if word_index == index:
                    return True
        else:
            return False

    def detect_window_size_change(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.start_x = int((self.width // 2) - (60 // 2) - 60 % 2)
        self.start_y = int((self.height // 2) - 2)

    def start_timer(self):
        log.debug("starting timer")
        if not self.periods:
            self.periods.append(time())

    def handle_events(self, key, change, writen_text):
        if key == 127:  # backspace
            if change != 0:
                change += -1
                writen_text = writen_text[:-1]
        elif key == ord(" ") or key == 10:
            change = 0

            if writen_text == self.words[self.current_word]:
                self.correct_words_ids.append(self.current_word)
            else:
                self.incorrect_words_ids.append(self.current_word)

            self.current_word += 1
            self.periods.append(time())
            self.answers.append(writen_text)

            if self.is_first_in_row(self.current_word):
                self.current_row += 1

            writen_text = ""
        elif key != 0:
            writen_text += chr(key)
            change += 1

        return change, writen_text

    def render_words(self):
        color_set = False
        temp_x = self.start_x

        self.stdscr.attron(curses.A_BOLD)

        for row_index, word_index, word in self.iter_words():
            log.debug("row_index=%s, word_index=%s, word=%s", row_index, word_index, word)
            if row_index not in (self.current_row, self.current_row + 1):
                continue

            color_set = True
            if self.current_word > word_index:
                if word == self.answers[word_index]:
                    self.stdscr.attron(curses.color_pair(4))
                else:
                    self.stdscr.attron(curses.color_pair(2))
            elif self.current_word == word_index and self.periods:
                self.stdscr.attron(curses.color_pair(6))
            else:
                color_set = False

            if self.is_first_in_row(word_index):
                temp_x = self.start_x

            self.stdscr.addstr(self.start_y + row_index - self.current_row, temp_x, word)
            temp_x += len(word) + 1

            if color_set:
                self.stdscr.attroff(curses.color_pair(4))
                self.stdscr.attroff(curses.color_pair(2))
                self.stdscr.attroff(curses.color_pair(6))
        self.stdscr.attroff(curses.A_BOLD)

    def render_summary(self):
        log.debug("timer stopped")

        execution_time = self.periods[-1] - self.periods[0]
        # +1 for each space
        correct_words = [self.words[id_] for id_ in self.correct_words_ids]
        incorrect_words = [self.answers[id_] for id_ in self.incorrect_words_ids]

        CPM = cpm(correct_words, execution_time)
        WPM = wpm(correct_words, execution_time)
        ACCURACY = accuracy(correct_words, incorrect_words)

        summary = [
            "Well done" if wpm > 50 and accuracy > 95 else "You need to train more",
            f"It only took you {execution_time:.2f}s",
            f"CPM = {CPM} | WPM = {WPM} | accuracy = {ACCURACY:.2f}%",
            f"invalid words = {len(self.incorrect_words_ids)} | correct words = {len(self.correct_words_ids)}",
            "",
            "Press any key to exit",
        ]

        log.info("cpm = %s time = %s %s", cpm, execution_time, (execution_time / 60.0))
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.attron(curses.A_BOLD)

        for i, line in enumerate(summary):
            self.stdscr.addstr(self.start_y + i, int((self.width // 2) - (len(line) // 2) - len(line) % 2), line)

        self.stdscr.attroff(curses.color_pair(1))
        self.stdscr.attroff(curses.A_BOLD)
        self.quit = True

    def render_input_bar(self, change, writen_text):
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.addstr(
            self.start_y + 6, self.start_x, writen_text + " " * (60 - len(writen_text)),
        )
        self.stdscr.attroff(curses.color_pair(3))

        self.stdscr.move(self.start_y + 6, self.start_x + change)

    def run(self):
        change = 0
        writen_text = ""

        key = 0
        log.debug("running game loop")
        while not self.quit:
            self.stdscr.clear()

            change, writen_text = self.handle_events(key, change, writen_text)

            if len(self.words) == len(self.answers):
                self.render_summary()
            else:
                self.render_words()
                self.render_input_bar(change, writen_text)

            self.stdscr.refresh()
            try:
                # Wait for next input
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                self.quit = True

            self.start_timer()

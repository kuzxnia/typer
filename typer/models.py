import curses
import logging
from abc import ABC, abstractmethod
from itertools import zip_longest
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


class Base(ABC):
    def __init__(self):
        self.stdscr = curses.initscr()
        self.stdscr.keypad(True)
        curses.cbreak()
        curses.noecho()

        # Clear and refresh the screen for a blank canvas
        self.stdscr.clear()
        self.stdscr.refresh()

        self.init_colors()
        self.detect_window_size_change()
        self.cursor_pos_x = self.start_x

        self.quit = False

    def __del__(self):
        self.stdscr.keypad(False)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, 239)  # white on dark gray
        curses.init_pair(4, 48, curses.COLOR_BLACK)  # green on default
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(6, curses.COLOR_WHITE, 242)  # white on dark gray

    def detect_window_size_change(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.start_x = int((self.width // 2) - (60 // 2) - 60 % 2)
        self.start_y = int((self.height // 2) - 2)

    def handle_key_event(self):
        if self.quit:
            return

        try:
            # Wait for next input
            return self.stdscr.getch()
        except KeyboardInterrupt:
            self.quit = True

    def run(self):
        key = 0
        while not self.quit:
            self.stdscr.clear()
            self.handle_events(key)
            self.render()
            self.stdscr.refresh()
            key = self.handle_key_event()

    @abstractmethod
    def handle_events(self, key):
        pass

    @abstractmethod
    def render(self):
        pass


class GameMenu(Base):
    def __init__(self):
        super(GameMenu, self).__init__()
        self.column = 0

        self.current_lang = 0
        self.current_range = 0

        self.ranges = {i: (n, n + 100) for i, n in enumerate(range(0, 1000, 100))}
        self.languages = {0: "en"}

    @property
    def lang(self):
        return self.languages.get(self.current_lang, "en")

    @property
    def range(self):
        return self.ranges.get(self.current_range, (0, 100))

    def handle_events(self, key):
        log.info("log")
        if key == curses.KEY_LEFT and self.column != 0:
            self.column = 0

        elif key == curses.KEY_RIGHT and self.column != 1:
            self.column = 1

        elif key == curses.KEY_UP:
            if self.column == 0 and self.current_range > 0:
                self.current_range -= 1
            elif self.column == 1 and self.current_lang > 0:
                self.current_lang -= 1

        elif key == curses.KEY_DOWN:
            if self.column == 0 and self.current_range < len(self.ranges) - 1:
                self.current_range += 1
            elif self.column == 1 and self.current_lang < len(self.languages) - 1:
                self.current_lang += 1

        elif key == curses.KEY_ENTER or key == 10:
            self.quit = True

    def render(self):
        ranges = [f"{n} ... {n+99}" for n in range(0, 1000, 100)]
        languages = ["English"]  # change to fetched from configuration

        # print heading
        self.stdscr.attron(curses.A_BOLD)
        self.stdscr.attron(curses.color_pair(0))
        heading = "Pick range:" + " " * 18 + " Pick language:" + " " * 16
        self.stdscr.addstr(self.start_y - 2, int((self.width // 2) - (len(heading) // 2) - len(heading) % 2), heading)
        self.stdscr.attroff(curses.color_pair(0))

        for i, (rang, lang) in enumerate(zip_longest(ranges, languages)):
            if self.current_range == i:
                self.stdscr.attron(curses.color_pair(6))
            self.stdscr.addstr(self.start_y + i, int((self.width // 2) - 30), f" {rang or ''} ")
            self.stdscr.attroff(curses.color_pair(6))

            if self.current_lang == i:
                self.stdscr.attron(curses.color_pair(6))
            self.stdscr.addstr(self.start_y + i, int((self.width // 2)), f" {lang or ''} ")
            self.stdscr.attroff(curses.color_pair(6))

        self.stdscr.attroff(curses.A_BOLD)

        self.stdscr.move(
            self.start_y + (self.current_range if self.column == 0 else self.current_lang),
            self.cursor_pos_x + self.column * 30,
        )


class Game(Base):
    def __init__(self, start=0, end=10, lang="en"):
        super(Game, self).__init__()
        self.periods = []

        self.temp_word = ""
        self.words = common_words_from_range(lang, start, end)
        self.answers = []
        self.current_word = 0
        self.current_row = 0
        self.correct_words = []
        self.incorrect_words = []

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

    def handle_key_event(self):
        if not self.quit:
            key = super(Game, self).handle_key_event()

            if not self.periods:
                log.debug("starting timer")
                self.periods.append(time())

            return key

    def handle_events(self, key):
        if key == 127:  # backspace
            if self.cursor_pos_x != self.start_x:
                self.cursor_pos_x += -1
                self.temp_word = self.temp_word[:-1]
        elif key == ord(" ") or key == 10:
            self.cursor_pos_x = self.start_x

            current_word = self.words[self.current_word]

            if self.temp_word == current_word:
                self.correct_words.append(current_word)
            else:
                self.incorrect_words.append(current_word)

            self.current_word += 1
            self.periods.append(time())
            self.answers.append(self.temp_word)

            if self.is_first_in_row(self.current_word):
                self.current_row += 1

            self.temp_word = ""
        elif key != 0:
            self.temp_word += chr(key)
            self.cursor_pos_x += 1

        if len(self.words) == len(self.answers):
            self.quit = True

        return self.temp_word

    def render(self):
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

        # input bar
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.addstr(
            self.start_y + 6, self.start_x, self.temp_word + " " * (60 - len(self.temp_word)),
        )
        self.stdscr.attroff(curses.color_pair(3))

        self.stdscr.move(self.start_y + 6, self.cursor_pos_x)


class GameSummary(Base):
    def __init__(self, periods, correct_words, incorrect_words):
        super(GameSummary, self).__init__()
        self.periods = periods
        self.correct_words = correct_words
        self.incorrect_words = incorrect_words

    def handle_events(self, key):
        # TODO: summary menu, invalid words, ...
        if key == 10:
            self.quit = True

    def render(self):
        log.debug("timer stopped")

        execution_time = self.periods[-1] - self.periods[0]

        CPM = cpm(self.correct_words, execution_time)
        WPM = wpm(self.correct_words, execution_time)
        ACCURACY = accuracy(self.correct_words, self.incorrect_words)

        summary = [
            "Well done" if WPM > 50 and ACCURACY > 95 else "You need to train more",
            f"It only took you {execution_time:.2f}s",
            f"CPM = {CPM} | WPM = {WPM} | accuracy = {ACCURACY:.2f}%",
            f"invalid words = {len(self.incorrect_words)} | correct words = {len(self.correct_words)}",
            "",
            "Press enter to exit",
        ]

        log.info("cpm = %s time = %s %s", cpm, execution_time, (execution_time / 60.0))
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.attron(curses.A_BOLD)

        for i, line in enumerate(summary):
            self.stdscr.addstr(self.start_y + i, int((self.width // 2) - (len(line) // 2) - len(line) % 2), line)

        self.stdscr.attroff(curses.color_pair(1))
        self.stdscr.attroff(curses.A_BOLD)

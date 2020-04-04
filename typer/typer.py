from __future__ import division

import curses
import logging
from time import time

from typer.most_common_words_by_lang import load_words

logging.basicConfig(
    filename="typer.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)
log = logging.getLogger(__name__)

words = load_words("en")


def drow_words():
    import random

    max_chars_in_line = 50

    res = []
    chars_in_line = 0
    while chars_in_line <= max_chars_in_line:
        temp_word = random.choice(words)
        if chars_in_line + len(temp_word) > max_chars_in_line + 3:
            continue
        res.append(temp_word)
        chars_in_line += len(temp_word) + 1
    return res


rows_amount = 2
rows = [drow_words() for _ in range(rows_amount)]
answers = [[] for _ in range(rows_amount)]
len_of_longest = max(map(lambda row: sum(len(word + " ") for word in row), rows))


# zmiana koloru słow podczas pisania, po zaakceptowaniu albo całe zielone albo całe czerwone
# noqa - function too complex,
def run(stdscr):  # noqa
    key = 0
    change = 0
    current_word = 0
    current_row = 0
    correct_words_len = 0
    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, 239)  # white on dark gray
    curses.init_pair(4, 48, curses.COLOR_BLACK)  # green on default
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)
    writen_text = ""

    start_time = 0
    while key != ord("q"):
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        start_x = int((width // 2) - (len_of_longest // 2) - len_of_longest % 2)
        start_y = int((height // 2) - len(rows))

        if key == 263:  # backspace
            if change != 0:
                change += -1
                writen_text = writen_text[:-1]
        elif key == ord(" ") or key == 10:
            change = 0

            current_word += 1
            if len(rows[current_row]) == current_word - 1:
                current_word = 1
                current_row += 1
                log.info(f"next row {current_row}")

            answers[current_row].append(writen_text)
            writen_text = ""

        elif key != 0:
            writen_text += chr(key)
            change += 1

        if current_row == len(rows) - 1 and len(rows[current_row]) == len(
            answers[current_row]
        ):
            execution_time = time() - start_time
            log.info(
                f"cpm = {correct_words_len} time = {execution_time} {execution_time / 60.0}"
            )
            cpm = correct_words_len // (execution_time / 60.0)
            statusbarstr = f"Press 'q' to exit | CPM = {cpm} WPM = {cpm/5}"
            stdscr.attron(curses.color_pair(5))
            stdscr.addstr(height - 1, 0, statusbarstr)
            stdscr.addstr(
                height - 1, len(statusbarstr), " " * (width - len(statusbarstr) - 1)
            )
            stdscr.attroff(curses.color_pair(5))
            stdscr.refresh()
            log.info("render submit")
            while key != ord("q"):
                key = stdscr.getch()
            exit()

        correct_words_len = 0
        # Turning on attributes for title
        stdscr.attron(curses.A_BOLD)
        # Rendering words
        temp_x = start_x
        color_set = False
        for row_index, row in enumerate(rows):
            for word_index, word in enumerate(row):
                if (
                    current_row == row_index
                    and current_word > word_index
                    or current_row > row_index
                ):
                    if word == answers[row_index][word_index]:
                        stdscr.attron(curses.color_pair(4))
                        correct_words_len += len(word)
                    else:
                        stdscr.attron(curses.color_pair(2))
                    color_set = True

                stdscr.addstr(start_y + row_index, temp_x, word)
                temp_x += len(word) + 1

                if color_set:
                    stdscr.attroff(curses.color_pair(4))
                    stdscr.attroff(curses.color_pair(2))
                color_set = False

            temp_x = start_x
        # Turning off attributes for title
        stdscr.attroff(curses.A_BOLD)

        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(
            start_y + 6,
            start_x,
            writen_text + " " * (len_of_longest - len(writen_text)),
        )
        stdscr.attroff(curses.color_pair(3))

        stdscr.move(start_y + 6, start_x + change)

        # Refresh the screen
        stdscr.refresh()

        # Wait for next input
        key = stdscr.getch()

        if not start_time:
            start_time = time()


if __name__ == "__main__":
    # print text
    # line under empty
    # contunuisly upgrading
    curses.wrapper(run)

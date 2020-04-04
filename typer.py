import curses
import logging
logging.basicConfig(
    filename='typer.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)
log = logging.getLogger(__name__)


def save_1000_most_common_en_words_to_file():
    from bs4 import BeautifulSoup
    import requests
    page = requests.get('https://1000mostcommonwords.com/1000-most-common-english-words')
    soup = BeautifulSoup(page.content, 'html.parser')
    res = []
    for i in soup.find('div', {'class': 'entry-content'}).find_all('td'):
        t = i.get_text()
        if t and not str(t).isnumeric():
            res.append(t + '\n')
    with open('en_1000_popular.txt', 'w') as f:
        f.writelines(res)


def load_words():
    with open('en_1000_popular.txt', 'r') as f:
        return [word[:-1] for word in f.readlines()]  # last char in '\n'


words = load_words()


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
len_of_longest = max(map(lambda row: sum(len(word + ' ') for word in row), rows))


# zmiana koloru słow podczas pisania, po zaakceptowaniu albo całe zielone albo całe czerwone
@curses.wrapper
def run(stdscr):
    key = 0
    change = 0
    current_word = 0
    current_row = 0
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
    writen_text = ''

    while (key != ord('q')):
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        start_x = int((width // 2) - (len_of_longest // 2) - len_of_longest % 2)
        start_y = int((height // 2) - len(rows))

        if key == 263:  # backspace
            if change != 0:
                change += -1
                writen_text = writen_text[:-1]
        elif key == ord(' ') or key == 10:
            change = 0
            if len(rows[current_row]) == current_word:
                current_word = 1
                current_row += 1
            else:
                current_word += 1
            answers[current_row].append(writen_text)
            writen_text = ''
            # accepting word

        elif key != 0:
            writen_text += chr(key)
            change += 1

        # Turning on attributes for title
        stdscr.attron(curses.A_BOLD)

        # Rendering words
        temp_x = start_x
        color_set = False
        for row_index, row in enumerate(rows):
            # default
            # red
            # green
            for word_index, word in enumerate(row):
                if current_row == row_index and current_word > word_index or current_row > row_index:
                    if word == answers[row_index][word_index]:
                        stdscr.attron(curses.color_pair(4))
                    else:
                        stdscr.attron(curses.color_pair(2))
                    color_set = True
                else:
                    color_set = False

                stdscr.addstr(start_y + row_index, temp_x, word)
                temp_x += len(word) + 1

                if color_set:
                    stdscr.attroff(curses.color_pair(4))
                    stdscr.attroff(curses.color_pair(2))

            temp_x = start_x
        log.info('after render ')
        # Turning off attributes for title
        stdscr.attroff(curses.A_BOLD)

        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(start_y + 6, start_x, writen_text + " " * (len_of_longest - len(writen_text)))
        stdscr.attroff(curses.color_pair(3))

        stdscr.move(start_y + 6, start_x + change)

        # Refresh the screen
        stdscr.refresh()

        # Wait for next input
        key = stdscr.getch()


if __name__ == '__main__':
    # print text
    # line under empty
    # contunuisly upgrading
    run()

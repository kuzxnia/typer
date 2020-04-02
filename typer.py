import sys
import time
import line
from itertools import zip_longest
from event import read_single_keypress


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


class Board:
    def __init__(self):
        self.current_line = 0
        self.rows_amount = 2
        self.current_word_index = 0
        self.rows = [' '.join(drow_words()) for _ in range(self.rows_amount)]
        self.answers = ['' for _ in range(self.rows_amount)]

    def move_line_down(self, val=1):
        for _ in range(val):
            line.down()
            self.current_line += 1

    def move_line_up(self, val=1):
        for _ in range(val):
            line.up()
            self.current_line -= 1

    def clear(self):
        i = 0
        while i != self.current_line:
            line.up()
            self.current_line -= 1

    def check_current_word_and_line(self):
        for row_num, (r, a) in enumerate(zip(self.rows, self.answers)):
            for word_num, (w, we) in enumerate(zip_longest(r, a)):
                if w != we:
                    return row_num, word_num

    def set_curr_line_to_curr_answer_line(self):
        row_num, word_num = self.check_current_word_and_line()

        self.clear()
        # self.move_line_down(((row_num + 1) * 2) - 1)
        sys.stdout.write("\033[%d;%dH" % (((row_num + 1) * 2) - 1, word_num))
        self.current_word_index = word_num

    def run(self):
        while 1:
            for c_row in range(self.rows_amount):
                sys.stdout.write('\r' + self.rows[c_row])
                sys.stdout.flush()
                self.move_line_down()
                sys.stdout.write('\r' + ' ' * len(self.rows[c_row]))
                sys.stdout.write('\r' + self.answers[c_row])
                sys.stdout.flush()
                self.move_line_down()

            self.set_curr_line_to_curr_answer_line()

            char = read_single_keypress()[0]

            if char != '\x7f':  # backspace
                self.answers[self.current_line - 1] += char
            else:
                self.answers[self.current_line - 1] = self.answers[self.current_line - 1][:-1]

            self.clear()


if __name__ == '__main__':
    # print text
    # line under empty
    # contunuisly upgrading
    b = Board()
    b.run()

    # a = read_single_keypress()
    # print('-> %s %s' % (repr(a), a))

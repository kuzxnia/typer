import random

from typer.util import scrape

AVALIABLE_LANGUAGES = {"en": scrape.fetch_most_common_en_words}


def save_words_to_file(lang_code: str, words: list):
    fetch_function = AVALIABLE_LANGUAGES.get(lang_code.lower())
    if not fetch_function:
        raise Exception("Language is not avaliable or code is invalid")

    with open("en_1000_popular.txt", "w") as f:
        f.writelines([word + "\n" for word in words])


def load_words(lang_code: str):
    lang_code = lang_code.lower()

    if lang_code not in AVALIABLE_LANGUAGES:
        raise Exception("Language is not avaliable or code is invalid")

    with open(f"{lang_code}_1000_popular.txt", "r") as f:
        return [word[:-1] for word in f.readlines()]  # last char in '\n'


def drow_words(lang_code: str, max_chars_in_line: int = 50):
    words = load_words(lang_code)

    res = []
    chars_in_line = 0
    while chars_in_line < max_chars_in_line:
        temp_word = random.choice(words)
        if chars_in_line + len(temp_word) > max_chars_in_line + 2:
            continue
        res.append(temp_word)
        chars_in_line += len(temp_word) + 1
    return res

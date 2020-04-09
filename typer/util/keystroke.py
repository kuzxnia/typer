def score_for_char(char: str):
    return 2 if char.isupper() else 1


def score_for_words(words: list):
    return sum(score_for_char(char) for char in "".join(words))

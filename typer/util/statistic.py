from __future__ import division

from typer.util.keystroke import score_for_words


def cpm(correct_words: list, duration: float):
    return score_for_words(correct_words) // (duration / 60.0)


def wpm(correct_words: list, duration):
    return cpm / 5


def accuracy(correct_words: list, incorrect_words: list):
    correct_words_score = score_for_words(correct_words)
    incorrect_words_score = score_for_words(incorrect_words)

    if correct_words_score == 0:
        return 0
    else:
        return correct_words_score / (correct_words_score + incorrect_words_score) * 100

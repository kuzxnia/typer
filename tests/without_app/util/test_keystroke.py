import string

import pytest
from typer.util import keystroke


def test_score_for_lowercase_chars():
    assert all(keystroke.score_for_char(char) == 1 for char in string.ascii_lowercase)


def test_score_for_uppercase_chars():
    assert all(keystroke.score_for_char(char) == 2 for char in string.ascii_uppercase)


def test_score_for_words_call_score_for_chars(mocker):
    # given
    mocked_func = mocker.patch.object(keystroke, "score_for_char")
    mocked_func.return_value = 1

    # when
    score = keystroke.score_for_words(["t"])

    assert score == 1
    mocked_func.assert_called_with("t")


@pytest.mark.parametrize("char, result", [(["anna"], 4), (["Anna"], 5)])
def test_score_for_words(char, result):
    assert keystroke.score_for_words(char) == result

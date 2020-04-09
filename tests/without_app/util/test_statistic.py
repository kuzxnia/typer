import pytest
from typer.util import statistic


@pytest.mark.parametrize(
    "words, duration, expected", [(["a" * 100], 60, 100), (["a" * 10], 30, 20), (["A" * 200], 30, 800)]
)
def test_cpm(words, duration, expected):
    assert statistic.cpm(words, duration) == expected


@pytest.mark.parametrize(
    "words, duration, expected", [(["a" * 100], 60, 20), (["a" * 10], 30, 4), (["A" * 200], 30, 160)]
)
def test_wpm(words, duration, expected):
    assert statistic.wpm(words, duration) == expected


def test_wpm_call_cpm(mocker):
    # given
    mocked_func = mocker.patch.object(statistic, "cpm")
    mocked_func.return_value = 100

    # when
    score = statistic.wpm(["a" * 100], 60)

    assert score == 20
    mocked_func.assert_called_with(["a" * 100], 60)


@pytest.mark.parametrize(
    "correct_words, incorrect_words, expected",
    [(["a" * 9], ["a"], 90), (["a" * 95], ["a" * 5], 95), (["A" * 95], ["A" * 5], 95)],
)
def test_accuracy(correct_words, incorrect_words, expected):
    assert statistic.accuracy(correct_words, incorrect_words) == expected

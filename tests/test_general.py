import time

import pytest

from py_teamup_api import teamup_api


@pytest.mark.parametrize(
    argnames="a, b, answer",
    argvalues=[
        (5, 7, 12),
        (5, 10, 15),
        (5, 12, 17),
    ],
)
def test_func(a, b, answer):
    result = teamup_api.add_numbers(a, b)
    assert result == answer


@pytest.mark.slow
def test_funcs():
    time.sleep(3)
    assert True

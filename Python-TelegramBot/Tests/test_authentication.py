import pytest
from auth import check_user_allowed


def test_valid_user_allowed():
    user_id = 123
    assert check_user_allowed(user_id) is True


def test_invalid_user_disallowed():
    user_id = -1
    assert check_user_allowed(user_id) is False
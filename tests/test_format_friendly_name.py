import pytest

from mail_forwarder.app import format_friendly_name


@pytest.fixture
def email_from():
    return "mail@example.com"


def test_format_friendly_name_happy_path(email_from):
    email_from_header = "Name Surname <test@somedomain.com>"

    new_from_header = format_friendly_name(email_from_header, email_from)
    assert new_from_header == f"Name Surname ~test@somedomain.com~ <{email_from}>"


def test_format_friendly_name_escapes_multiple_angle_brackets(email_from):
    email_from_header = "<<<test@somedomain.com>>>"

    new_from_header = format_friendly_name(email_from_header, email_from)
    assert new_from_header == f"~~~test@somedomain.com~~~ <{email_from}>"

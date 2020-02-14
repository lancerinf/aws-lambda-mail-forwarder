import pytest
import os
from unittest import mock
from email.message import EmailMessage

from mail_forwarder.app import prepare_email_for_forwarding


@pytest.fixture
def base_email_msg():
    em = EmailMessage()
    em.add_header('Reply-To', 'reply-to@example.com')
    em.add_header('Return-Path', 'return-path@example.com')
    em.add_header('From', 'original_from@example.com')
    em.add_header('DKIM-Signature', 'The Greatest Signature')

    return em


@mock.patch.dict(os.environ, {'FORWARD_FROM_ADDRESS': 'mail@example.com'})
def test_prepare_email_for_forwarding_strips_dkim_signature_header(base_email_msg):
    modified_email_message = prepare_email_for_forwarding(base_email_msg)

    assert not modified_email_message['DKIM-Signature']


@mock.patch.dict(os.environ, {'FORWARD_FROM_ADDRESS': 'mail@example.com'})
def test_prepare_email_for_forwarding_strips_return_path_header(base_email_msg):
    modified_email_message = prepare_email_for_forwarding(base_email_msg)

    assert not modified_email_message['Return-Path']

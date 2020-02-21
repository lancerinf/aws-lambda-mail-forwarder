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

    assert 'DKIM-Signature' not in modified_email_message


@mock.patch.dict(os.environ, {'FORWARD_FROM_ADDRESS': 'mail@example.com'})
def test_prepare_email_for_forwarding_strips_return_path_header(base_email_msg):
    modified_email_message = prepare_email_for_forwarding(base_email_msg)

    assert 'Return-Path' not in modified_email_message


@mock.patch.dict(os.environ, {'FORWARD_FROM_ADDRESS': 'mail@example.com'})
def test_prepare_email_for_forwarding_sets_reply_to(base_email_msg):
    del base_email_msg['Reply-To']
    del base_email_msg['Return-Path']
    modified_email_message = prepare_email_for_forwarding(base_email_msg)

    assert 'Reply-To' in modified_email_message


@mock.patch.dict(os.environ, {'FORWARD_FROM_ADDRESS': 'mail@example.com'})
def test_prepare_email_for_forwarding_keeps_reply_to_if_it_exists(base_email_msg):
    modified_email_message = prepare_email_for_forwarding(base_email_msg)

    assert modified_email_message['Reply-To'] == base_email_msg['Reply-To']


@mock.patch.dict(os.environ, {'FORWARD_FROM_ADDRESS': 'mail@example.com'})
def test_prepare_email_for_forwarding_sets_reply_to_to_return_path_if_it_exists(base_email_msg):
    del base_email_msg['Reply-To']
    modified_email_message = prepare_email_for_forwarding(base_email_msg)

    assert modified_email_message['Reply-To'] == base_email_msg['Return-Path']


@mock.patch.dict(os.environ, {'FORWARD_FROM_ADDRESS': 'mail@example.com'})
def test_prepare_email_for_forwarding_sets_reply_to_to_from_if_no_better_exists(base_email_msg):
    del base_email_msg['Reply-To']
    del base_email_msg['Return-Path']
    modified_email_message = prepare_email_for_forwarding(base_email_msg)

    assert modified_email_message['Reply-To'] == base_email_msg['From']

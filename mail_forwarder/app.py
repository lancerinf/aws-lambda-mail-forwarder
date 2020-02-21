from boto3 import client
import email
import urllib.parse
import os
from copy import deepcopy


def lambda_handler(event, context):
    # Fetch file from S3
    s3_client = client('s3')
    s3_object_body = get_object_from_s3(s3_client, event)

    # Parse object as EmailMessage
    email_message = parse_email_message(s3_object_body)

    # Prepare EmailMessage to be forwarded, switch headers
    email_message = prepare_email_for_forwarding(email_message)

    # Send modified EmailMessage with SES
    ses_client = client('ses')
    send_result = forward_email(ses_client, email_message)
    return send_result


def get_object_from_s3(s3_client, trigger_event):
    s3_put_notification = trigger_event['Records'][0]
    bucket = s3_put_notification['s3']['bucket']['name']
    key = urllib.parse.unquote(s3_put_notification['s3']['object']['key'])
    s3_object_response = s3_client.get_object(
        Bucket=bucket,
        Key=key
    )
    return s3_object_response['Body']


def parse_email_message(s3_object_body):
    # Parse email as suggested: https://docs.python.org/3.7/library/email.parser.html
    parsed_email_message = email.message_from_bytes(s3_object_body.read())
    return parsed_email_message


def prepare_email_for_forwarding(email_message):
    forward_from_address = os.environ['FORWARD_FROM_ADDRESS']
    email_message_copy = deepcopy(email_message)

    # Ensure Reply-To header is set to most relevant Address while also removing Return-Path header.
    if 'Reply-To' not in email_message:
        if 'Return-Path' in email_message: email_message_copy['Reply-To'] = email_message['Return-Path']
        else: email_message_copy['Reply-To'] = email_message['From']
    del email_message_copy['Return-Path']

    # Remove any pre-existing DKIM-Signature header.
    del email_message_copy['DKIM-Signature']

    # Set From header to user-friendly name.
    email_message_copy.replace_header('From', format_friendly_name(email_message['From'], forward_from_address))

    return email_message_copy


def format_friendly_name(email_from_header, forward_from_address):
    angle_bracket_escaped_from_header = email_from_header.replace('<', '~').replace('>', '~')
    return f'{angle_bracket_escaped_from_header} <{forward_from_address}>'


def forward_email(ses_client, email_message):
    forward_from_address = os.environ['FORWARD_FROM_ADDRESS']
    forward_to = os.environ['FORWARD_TO_ADDRESS']

    # Actually send the email
    send_result = ses_client.send_raw_email(
        Source=forward_from_address,
        Destinations=[
            forward_to,
        ],
        RawMessage={
            'Data': email_message.as_bytes()
        }
    )
    return send_result

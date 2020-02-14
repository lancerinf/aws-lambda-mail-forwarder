from boto3 import client
import email
import urllib.parse
import os


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
    forward_from = os.environ['FORWARD_FROM_ADDRESS']
    enriched_from_header = format_friendly_name(email_message['From'], forward_from)

    # Ensure Reply-To header is set to most relevant Address.
    if email_message['Return-Path']:
        if not email_message['Reply-To']:
            email_message.add_header('Reply-To', email_message['Return-Path'])
        del email_message['Return-Path']

    # Set From header to user-friendly name.
    email_message.replace_header('From', enriched_from_header)

    # Remove all pre-existing DKIM-Signature headers:
    del email_message['DKIM-Signature']
    return email_message


def format_friendly_name(email_from_header, forward_from):
    email_from_header = email_from_header.replace('<', '~')
    email_from_header = email_from_header.replace('>', '~')
    return f'{email_from_header} <{forward_from}>'


def forward_email(ses_client, email_message):
    forward_from = os.environ['FORWARD_FROM_ADDRESS']
    forward_to = os.environ['FORWARD_TO_ADDRESS']

    # Actually send the email
    send_result = ses_client.send_raw_email(
        Source=forward_from,
        Destinations=[
            forward_to,
        ],
        RawMessage={
            'Data': email_message.as_bytes()
        }
    )
    return send_result

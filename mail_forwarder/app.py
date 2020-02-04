from boto3 import client
import email
import urllib.parse
import os
import sys


def lambda_handler(event, context):
    s3_notification = event['Records'][0]

    try:
        # Fetch file from S3
        s3_client = client('s3')
        s3_object_bytes = get_object_from_s3(s3_client, s3_notification)

        # Check if valid email
        email_message = parse_email_message(s3_object_bytes)

        # Modify EmailMessage replyTo and From fields
        # Send new/modified EmailMessage object with SES
        ses_client = client('ses')
        send_result = twist_and_forward(ses_client, email_message)
        print(send_result)

    except s3_client.exceptions.NoSuchKey as e:
        print(f'S3Exception(NoSuchKey): {e}')
    except ses_client.exceptions.ClientError as e:
        print(f'SESException(ClientError): {e}')
    except:
        print(f'Whoops, a new exception was thrown:', sys.exc_info()[0])


def get_object_from_s3(s3_client, s3_notification):
    bucket = s3_notification['s3']['bucket']['name']
    key = urllib.parse.unquote(s3_notification['s3']['object']['key'])
    s3_object_response = s3_client.get_object(
        Bucket=bucket,
        # Key=key
        Key='inbox/federico@lancerin.com/v2ehb4igsa1n6n9323oqvna4so3knlg6h0985f01'
    )
    return s3_object_response['Body'].read()


def parse_email_message(s3_object_bytes):
    # Parse email as suggested: https://docs.python.org/3.7/library/email.parser.html
    parsed_email_message = email.message_from_bytes(s3_object_bytes)
    return parsed_email_message


def twist_and_forward(ses_client, email_message):
    forward_from = os.environ['FORWARD_FROM_ADDRESS']
    forward_to = os.environ['FORWARD_TO_ADDRESS']

    if not email_message.get('Reply-To'):
        email_message.add_header('Reply-To', email_message.get('From'))

    del email_message['Return-Path']
    email_message.replace_header('From', forward_from)

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

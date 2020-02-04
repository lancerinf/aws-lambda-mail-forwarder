from boto3 import client
import email
import urllib.parse

SES_SEND_IDENTITY = 'mailforwarder@lancerin.com'


def lambda_handler(event, context):
    s3_notification = event['Records'][0]
    print("Well well, let's deal with this S3 event: ")
    print(s3_notification)

    try:
        # Fetch file from S3
        s3_client = client('s3')
        s3_object_bytes = get_object_from_s3(s3_client, s3_notification)

        # Check if valid email
        email_message = parse_email_message(s3_object_bytes)
        print('Received email: \n', email_message)

        # Deep copy MIME OR MODIFY replyTo and sender fields
        # Send new/modified MIME object with SES

    except s3_client.exceptions.NoSuchKey as e:
        print(f'S3Exception(NoSuchKey): {e}')


def get_object_from_s3(s3_client, s3_notification):
    bucket = s3_notification['s3']['bucket']['name']
    key = urllib.parse.unquote(s3_notification['s3']['object']['key'])
    s3_object_response = s3_client.get_object(
        Bucket=bucket,
        Key=key
    )
    return s3_object_response['Body'].read()


def parse_email_message(s3_object_bytes):
    print('Is this a valid MIME? ..or Maybe a valid MEME!')
    # Parse email as suggested: https://docs.python.org/3.7/library/email.parser.html
    parsed_email_message = email.message_from_bytes(s3_object_bytes)
    return parsed_email_message

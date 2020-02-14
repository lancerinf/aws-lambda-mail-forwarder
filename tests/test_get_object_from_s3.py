import pytest
from boto3 import client
from unittest.mock import Mock

from mail_forwarder import app


@pytest.fixture
def mock_s3_client():
    mock_s3_client = Mock(spec=client('s3'))
    attrs = {'get_object.return_value': dict(Body='Value')}
    mock_s3_client.configure_mock(**attrs)
    return mock_s3_client


def s3_put_object_notification(bucket_name, object_key):
    return {
        'Records': [
            {
                'eventVersion': '2.0',
                'eventSource': 'aws:s3',
                's3': {
                    's3SchemaVersion': '1.0',
                    'bucket': {
                        'name': bucket_name
                    },
                    'object': {
                        'key': object_key
                    }
                }
            }
        ]
    }


def test_get_object_from_s3_correctly_takes_bucket_and_key_from_event(mock_s3_client):
    notification = s3_put_object_notification('fedebucket', 'HappyFace.jpg')
    app.get_object_from_s3(mock_s3_client, notification)

    mock_s3_client.get_object.assert_called_with(
        Bucket='fedebucket',
        Key='HappyFace.jpg'
    )


def test_get_object_from_s3_unquotes_keys_special_characters(mock_s3_client):
    notification = s3_put_object_notification('fedebucket', 'email%40example.com/HappyFace.jpg')
    app.get_object_from_s3(mock_s3_client, notification)

    mock_s3_client.get_object.assert_called_with(
        Bucket='fedebucket',
        Key='email@example.com/HappyFace.jpg'
    )
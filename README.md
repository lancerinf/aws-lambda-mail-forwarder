# aws-lambda-mail-forwarder

This AWS Lambda will be triggered each time a new email is received by SES and the content put in my bucket.

The Function takes the message from S3 and forwards it to my Gmail account, while also setting the `reply-to` field to
the original `sender`, so when I hit Reply, the Destination is set correctly.

## Development

Use the facilities in the Makefile to:
* test
* build
* local-invoke
* deploy

..the function, from the repository root.

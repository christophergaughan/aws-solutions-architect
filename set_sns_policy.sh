#!/bin/bash
aws sns set-topic-attributes \
    --topic-arn arn:aws:sns:us-east-1:001752764000:TextractTopic \
    --attribute-name Policy \
    --attribute-value '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "textract.amazonaws.com"
                },
                "Action": "SNS:Publish",
                "Resource": "arn:aws:sns:us-east-1:001752764000:TextractTopic"
            }
        ]
    }'


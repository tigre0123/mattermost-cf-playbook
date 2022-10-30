#!/bin/bash

aws cloudformation validate-template --template-body file://ansible-cf-mattermost.yml 2>&1 1>/dev/null | grep ValidationError
if [ $? = 0 ]; then
    echo "cloudformation template validate error"
    exit 1
fi

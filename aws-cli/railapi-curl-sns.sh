#!/bin/bash
sns_topic_arn="arn:aws:sns:ap-southeast-1:556627625820:railapi-curl-pong-test"
url="https://railapi.shohoz.com/v1.0/app/ping"

status=$(curl -s -o /dev/null -w "%{http_code}" $url)
if [ $status = 200 ]; then
   message="Status is $status"
   echo $message
   exit 1
fi
  aws sns publish --topic-arn $sns_topic_arn --message "Warning!!! train-railapi isn't working"

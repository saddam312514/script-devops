#!/bin/bash
read -p "Enter ASG Name : " ASG_NAME
#get the desired capacity value and fix min and max value
desired_capacity=$(aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names "$ASG_NAME" --query 'AutoScalingGroups[0].DesiredCapacity' --output text)

aws autoscaling update-auto-scaling-group --auto-scaling-group-name "$ASG_NAME" --min-size $desired_capacity --max-size $desired_capacity

#get asg instance IDs
INSTANCE_IDS=$(aws autoscaling describe-auto-scaling-instances --query 'AutoScalingInstances[?AutoScalingGroupName==`'$ASG_NAME'` && LifecycleState==`InService`].InstanceId' --output text)

#get IP address of all those instance
aws ec2 describe-instances --instance-ids $INSTANCE_IDS  --query 'Reservations[].Instances[].PrivateIpAddress' --output text

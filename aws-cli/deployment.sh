#!/bin/bash

# Set variables
read -p "Enter Instance Name : " EC2_INSTANCE_NAME
read -p "Enter Instance Template Name : " INSTANCE_TEMPLATE_NAME

TIME=$(TZ='Asia/Dhaka' date '+%d-%m-%y'-'%H-%M')

AMI_NAME=$EC2_INSTANCE_NAME'-'$TIME
IMAGE_DESCRIPTION=$EC2_INSTANCE_NAME'-'$TIME
IMAGE_TAG=$EC2_INSTANCE_NAME'-'$TIME
TEMPLATE_VERSION_DESCRIPTION=$INSTANCE_TEMPLATE_NAME'-'$TIME

#Query Instance ID
INSTANCE_ID=$(aws ec2 describe-instances --filters  "Name=tag:Name,Values=$EC2_INSTANCE_NAME" "Name=instance-state-name,Values=running" --query 'Reservations[*].Instances[*].[InstanceId]' --output text |head -n 1)

# Create the AMI
AMI_ID=$(aws ec2 create-image --instance-id "$INSTANCE_ID" --name "$AMI_NAME" --description "$IMAGE_DESCRIPTION" --tag-specifications 'ResourceType=image,Tags=[{Key=Name,Value='$IMAGE_TAG'}]' --no-reboot --output text)

state1=$(aws ec2 describe-images --image-ids $AMI_ID --query 'Images[*].State' --output text)

echo 'Image on '$state1' state and Image ID is '$AMI_ID''
echo 'Please wait until the image is available....'

aws ec2 wait image-available --image-ids $AMI_ID

state2=$(aws ec2 describe-images --image-ids $AMI_ID --query 'Images[*].State' --output text)

echo Image is $state2


# Get the default template version number
DEFAULT_VERSION=$(aws ec2 describe-launch-templates --query 'LaunchTemplates[?LaunchTemplateName==`'$INSTANCE_TEMPLATE_NAME'`].DefaultVersionNumber' --output text)

# Create a new version of the ASG template
aws ec2 create-launch-template-version --launch-template-name $INSTANCE_TEMPLATE_NAME --version-description $TEMPLATE_VERSION_DESCRIPTION --source-version $DEFAULT_VERSION --launch-template-data '{"ImageId":"'$AMI_ID'"}'

# Get the new template version number
NEW_VERSION=$(aws ec2 describe-launch-template-versions --launch-template-name $INSTANCE_TEMPLATE_NAME --query 'LaunchTemplateVersions[*].[VersionNumber]' --output text  |head -n 1)


# Set the new template version as the default version
aws ec2 modify-launch-template --launch-template-name $INSTANCE_TEMPLATE_NAME --default-version $NEW_VERSION

echo '********Congratulations!! your new version of template is ready********'
echo 'New Image ID is '$AMI_ID' of Instance '$EC2_INSTANCE_NAME''
echo New Template Version is $NEW_VERSION


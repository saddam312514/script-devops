#!/bin/bash
# Set variables
read -p "Enter Image ID : " AMI_ID
read -p "Enter Instance Template Name : " INSTANCE_TEMPLATE_NAME

TIME=$(TZ='Asia/Dhaka' date '+%d-%m-%y'-'%H-%M')
TEMPLATE_VERSION_DESCRIPTION=$INSTANCE_TEMPLATE_NAME'-'$TIME

# Get the default template version number
DEFAULT_VERSION=$(aws ec2 describe-launch-templates --query 'LaunchTemplates[?LaunchTemplateName==`'$INSTANCE_TEMPLATE_NAME'`].DefaultVersionNumber' --output text)

# Create a new version of the ASG template
aws ec2 create-launch-template-version --launch-template-name $INSTANCE_TEMPLATE_NAME --version-description $TEMPLATE_VERSION_DESCRIPTION --source-version $DEFAULT_VERSION --launch-template-data '{"ImageId":"'$AMI_ID'"}'

# Get the new template version number
NEW_VERSION=$(aws ec2 describe-launch-template-versions --launch-template-name $INSTANCE_TEMPLATE_NAME --query 'LaunchTemplateVersions[*].[VersionNumber]' --output text  |head -n 1)


# Set the new template version as the default version
aws ec2 modify-launch-template --launch-template-name $INSTANCE_TEMPLATE_NAME --default-version $NEW_VERSION

echo '********Congratulations!! your new version of template is ready********'
echo New Template Version is $NEW_VERSION


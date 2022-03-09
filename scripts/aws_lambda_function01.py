from tracemalloc import Filter
import boto3
import logging

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#define the connection
region = 'us-east-1'
account_id = ''
sns_topic_name = 'test_auto_alarm'
ec2 = boto3.resource('ec2', region_name=region)

# Create CloudWatch client
cloudwatch = boto3.client('cloudwatch')


def lambda_handler(event, context):
    # Use the filter() method of the instances collection to retrieve
    # all running EC2 instances.
    filters = [
        {
            'Name': 'tag:NICKNAME',
            'Values': ['test_alarm_tag']
        }
    ]
    
    #filter the instances
    instances = ec2.instances.filter(Filters=filters)
    # instances = ec2.instances.filter(Filters)

    #locate all running instances
    RunningInstances = [instance.id for instance in instances]

    for instance_id in RunningInstances:
        print(instance_id)
        # Create alarm with actions enabled
        cloudwatch.put_metric_alarm(
            AlarmName=f'StatusCheckFailedAlarm-{instance_id}',
            ComparisonOperator='GreaterThanThreshold',
            EvaluationPeriods=3,
            MetricName='StatusCheckFailed',
            Namespace='AWS/EC2',
            Period=60,
            Statistic='Minimum',
            Threshold=0,
            ActionsEnabled=True,
            AlarmActions=[
            # f'arn:aws:swf:{region}:{account_id}:action/actions/AWS_EC2.InstanceId.Reboot/1.0',
            # f'arn:aws:automate:{region}:ec2:reboot', f'arn:aws:sns:{region}:{account_id}:{sns_topic_name}',
            f'arn:aws:swf:{region}:{account_id}:action/actions/AWS_EC2.InstanceId.Reboot/1.0', f'arn:aws:sns:{region}:{account_id}:{sns_topic_name}', 
            ],
            AlarmDescription='Alarm when status check fails',
            Dimensions=[
                {
                'Name': 'InstanceId',
                'Value': f'{instance_id}'
                },
            ],
        
            Tags=[
                {
                    'Key': 'NICKNAME',
                    'Value': 'test_alarm_tag'
                },
            ],
            Unit='Seconds'
        )

    else:
        print("Nothing to see here")

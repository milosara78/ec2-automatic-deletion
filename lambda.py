import boto3
import datetime

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    today = datetime.datetime.now().date()

    # Get all EC2 instances with the 'end_date' tag
    instances = ec2.describe_instances(Filters=[{'Name': 'tag-key', 'Values': ['end_date']}])

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}

            end_date_str = tags.get('end_date')
            auto_terminate = tags.get('auto_terminate', 'false').lower()  # Default to 'false' if not set

            # Process only if auto_terminate is explicitly 'true'
            if auto_terminate == 'true' and end_date_str:
                try:
                    # Parse the end_date
                    end_date = datetime.datetime.strptime(end_date_str, "%m/%d/%y").date()
                    if today > end_date:
                        print(f"Terminating instance {instance_id} with end_date {end_date} and auto_terminate={auto_terminate}")
                        ec2.terminate_instances(InstanceIds=[instance_id])
                except ValueError:
                    print(f"Invalid date format for instance {instance_id}: {end_date_str}")
            else:
                print(f"Skipping instance {instance_id} (auto_terminate={auto_terminate})")


#make sure you have tag for instance as auto_terminate=true because this code targets only those instances

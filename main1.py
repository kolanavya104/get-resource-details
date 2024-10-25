import boto3
from prettytable import PrettyTable
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os

def get_ec2_details(state):
    ec2 = boto3.client('ec2')
    instances = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': [state]}]
    )
    
    instance_data = []
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            name_tag = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), "N/A")
            instance_data.append({
                'Name': name_tag,
                'Instance ID': instance['InstanceId'],
                'State': instance['State']['Name'],
                'Launch Date': instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S')
            })
    return instance_data

def get_s3_bucket_details():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    bucket_data = [{'Bucket Name': bucket['Name'], 'Region': s3.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']} for bucket in response['Buckets']]
    return bucket_data

def format_table(data, columns):
    table = PrettyTable()
    table.field_names = columns
    for item in data:
        table.add_row([item[col] for col in columns])
    return table

def main():
    try:
        # Fetching details
        running_instances = get_ec2_details('running')
        stopped_instances = get_ec2_details('stopped')
        s3_buckets = get_s3_bucket_details()
        
        # Formatting the tables for terminal output
        running_table = format_table(running_instances, ['Name', 'Instance ID', 'State', 'Launch Date'])
        stopped_table = format_table(stopped_instances, ['Name', 'Instance ID', 'State', 'Launch Date'])
        s3_table = format_table(s3_buckets, ['Bucket Name', 'Region'])
        
        # Displaying results in terminal
        print("\nRunning Instances:\n", running_table)
        print("\nStopped Instances:\n", stopped_table)
        print("\nS3 Buckets:\n", s3_table)
        
    except (NoCredentialsError, PartialCredentialsError) as e:
        print("AWS credentials not found. Ensure they are configured properly.")
        
if __name__ == "__main__":
    main()

#AWS SDK for Python, used to interact with AWS services.
import boto3
# create well-formatted tables for HTML representation.
from prettytable import PrettyTable
#write Specific exceptions to handle AWS credential and client errors.
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
#or accessing environment variables.
import os



#function retrieves details of EC2 instances based on their state, like "running" or "stopped".
def get_ec2_details(state):
    #Create an EC2 client with boto3 using AWS credentials stored in environment variables.
    ec2 = boto3.client('ec2',
                       aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                       aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                       region_name=os.getenv('AWS_DEFAULT_REGION'))

    #Fetch instance data filtered by the specified state (e.g., "running").
    instances = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': [state]}]
    )

    #extract details of each instance,If an instance has no "Name" tag, it defaults to "N/A".
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
    #Return the list of instance details:
    return instance_data

#function retrieves details of all S3 buckets.
def get_s3_bucket_details():
    # Initialize the S3 client with environment variables
    s3 = boto3.client('s3',
                      aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                      region_name=os.getenv('AWS_DEFAULT_REGION'))

    #Calls list_buckets() to get all bucket names.
    response = s3.list_buckets()
    #Create a list of dictionaries containing bucket name and region.
    bucket_data = [{'Bucket Name': bucket['Name'], 'Region': s3.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']} for bucket in response['Buckets']]
    return bucket_data

#function formats data into an HTML table.
def format_table(data, columns):
    #Set up table columns and add data rows:...Sets column headers based on columns.Adds each item as a row.
    table = PrettyTable()
    table.field_names = columns
    for item in data:
        table.add_row([item[col] for col in columns])
    return table.get_html_string()

#Function to Send an email with AWS SES (Simple Email Service).
def send_email_via_ses(content, sender_email, recipient_email):
    ses = boto3.client('ses',
                       aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                       aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                       region_name=os.getenv('AWS_DEFAULT_REGION'))
    
    #Sends an email with sender and recipient addresses, a subject, and the HTML body content.Catches errors if email sending fails.
    try:
        response = ses.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': [recipient_email],
            },
            Message={
                'Subject': {
                    'Data': "AWS Resource Details",
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': content,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        print("Email sent successfully.")
    except ClientError as e:
        print(f"Error sending email: {e.response['Error']['Message']}")

def main():
    try:
        running_instances = get_ec2_details('running')
        stopped_instances = get_ec2_details('stopped')
        s3_buckets = get_s3_bucket_details()
        
        # Formatting the tables
        running_table = format_table(running_instances, ['Name', 'Instance ID', 'State', 'Launch Date'])
        stopped_table = format_table(stopped_instances, ['Name', 'Instance ID', 'State', 'Launch Date'])
        s3_table = format_table(s3_buckets, ['Bucket Name', 'Region'])
        
        email_content = f"<h2>Running Instances</h2>{running_table}<br><h2>Stopped Instances</h2>{stopped_table}<br><h2>S3 Buckets</h2>{s3_table}"
        
        sender_email = "kola.navya@kansocloud.com"  # Replace with your SES-verified sender email
        recipient_email = "kolanavya478@gmail.com"  # Replace with the actual recipient email
        send_email_via_ses(email_content, sender_email, recipient_email)
        
    except (NoCredentialsError, PartialCredentialsError) as e:
        print("AWS credentials not found. Ensure they are configured properly.")
        
if __name__ == "__main__":
    main()








# Force redeploy 2
import json
import logging
import boto3
import os
from botocore.exceptions import ClientError
 
# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
 
# Initialize AWS Clients
ec2 = boto3.client('ec2')
ses = boto3.client('ses')
s3 = boto3.client('s3') 
 
def send_security_alert(sender, recipient, open_groups, open_buckets):
    """Generates and sends a unified security warning email for EC2 and S3."""
    subject = "⚠️ CRITICAL: Security Guardrail Breach Detected"
    
    # Build EC2 rows
    ec2_rows = ""
    for group in open_groups:
        ec2_rows += f"""
        <tr>
            <td style='padding:8px; border:1px solid #ddd;'><b>{group['GroupId']}</b></td>
            <td style='padding:8px; border:1px solid #ddd;'>{group['GroupName']}</td>
            <td style='padding:8px; border:1px solid #ddd; color:red;'><b>Port {group['Port']} (Open to World)</b></td>
        </tr>
        """
 
    # Build S3 rows
    s3_rows = ""
    for bucket in open_buckets:
        s3_rows += f"""
        <tr>
            <td style='padding:8px; border:1px solid #ddd;'><b>{bucket}</b></td>
            <td style='padding:8px; border:1px solid #ddd; color:red;'><b>Public Access Block Missing/Disabled</b></td>
        </tr>
        """
 
    # Assemble HTML Body
    body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #d9534f;">🚨 Security Guardrail Alert</h2>
            <p>The automated security scanner identified infrastructure resources exposed to the public internet.</p>
            
            {"<h3>🔒 Exposed EC2 Security Groups</h3>" if open_groups else ""}
            {f'''<table style="width:100%; border-collapse: collapse; text-align:left; margin-bottom:20px;">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding:8px; border:1px solid #ddd;">Group ID</th>
                        <th style="padding:8px; border:1px solid #ddd;">Group Name</th>
                        <th style="padding:8px; border:1px solid #ddd;">Exposure</th>
                    </tr>
                </thead>
                <tbody>{ec2_rows}</tbody>
            </table>''' if open_groups else ""}
 
            {"<h3>🪣 Non-Compliant S3 Buckets</h3>" if open_buckets else ""}
            {f'''<table style="width:100%; border-collapse: collapse; text-align:left; margin-bottom:20px;">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding:8px; border:1px solid #ddd;">Bucket Name</th>
                        <th style="padding:8px; border:1px solid #ddd;">Exposure</th>
                    </tr>
                </thead>
                <tbody>{s3_rows}</tbody>
            </table>''' if open_buckets else ""}
            
            <p style="margin-top:20px; color:#555;"><i>Please restrict these public configurations immediately via the AWS Console.</i></p>
        </body>
    </html>
    """
 
    try:
        response = ses.send_email(
            Source=sender,
            Destination={'ToAddresses': [recipient]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': body_html}}
            }
        )
        logger.info(f"Security alert email sent successfully: {response['MessageId']}")
    except Exception as e:
        logger.error(f"Failed to send security email via SES: {str(e)}")
 
def lambda_handler(event, context):
    logger.info("Starting security guardrail compliance scan...")
    
    sender = os.environ.get('SENDER_EMAIL')
    recipient = os.environ.get('RECIPIENT_EMAIL')
    
    open_groups = []
    open_buckets = []
    
    # 1. Scan EC2 Security Groups
    try:
        response = ec2.describe_security_groups()
        for group in response['SecurityGroups']:
            for permission in group.get('IpPermissions', []):
                for ip_range in permission.get('IpRanges', []):
                    if ip_range.get('CidrIp') == '0.0.0.0/0':
                        from_port = permission.get('FromPort', 'All')
                        open_groups.append({
                            'GroupId': group['GroupId'],
                            'GroupName': group['GroupName'],
                            'Port': from_port
                        })
    except Exception as e:
        logger.error(f"Error scanning EC2 security groups: {str(e)}")
 
    # 2. Scan S3 Buckets for Public Access Blocks
    try:
        buckets_response = s3.list_buckets()
        for bucket in buckets_response.get('Buckets', []):
            bucket_name = bucket['Name']
            try:
                # Check if public access block is configured
                pab = s3.get_public_access_block(Bucket=bucket_name)
                config = pab.get('PublicAccessBlockConfiguration', {})
                
                # If any key public block is set to False, the bucket is flaggable
                if not (config.get('BlockPublicAcls') and config.get('IgnorePublicAcls') and
                        config.get('BlockPublicPolicy') and config.get('RestrictPublicBuckets')):
                    open_buckets.append(bucket_name)
                    
            except ClientError as e:
                # If NoSuchPublicAccessBlockConfiguration error is thrown, it has no protection at all
                if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
                    open_buckets.append(bucket_name)
                else:
                    logger.error(f"Could not read configurations for bucket {bucket_name}: {str(e)}")
    except Exception as e:
        logger.error(f"Error scanning S3 buckets: {str(e)}")
        
    # 3. Action Evaluation and Email Alert Trigger
    if (open_groups or open_buckets) and sender and recipient:
        logger.warning(f"Guardrail breaches found! EC2: {len(open_groups)}, S3: {len(open_buckets)}. Alerting...")
        send_security_alert(sender, recipient, open_groups, open_buckets)
    else:
        logger.info("Scan complete. Infrastructure matches all security guardrails.")
        
    return {
        'statusCode': 200,
        'body': json.dumps('Security guardrail scan completed successfully.')
    }
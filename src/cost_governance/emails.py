import boto3
import os
 
def send_html_report(report_data):
    ses = boto3.client('ses')
    
    # Read verified identities straight from the Lambda environment variables
    SENDER = os.environ.get('SENDER_EMAIL')
    RECIPIENT = os.environ.get('RECIPIENT_EMAIL')
    
    html_body = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 25px; }
            th, td { border: 1px solid #dddddd; text-align: left; padding: 10px; }
            th { background-color: #f2f2f2; color: #333; }
            h2 { color: #2C3E50; margin-top: 20px; }
            .success { color: #27AE60; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>AWS Cost Optimization Weekly Report</h1>
        <p>Hello, here is the automated weekly infrastructure cost governance overview.</p>
    """
    
    # Table 1: Unattached Volumes
    html_body += "<h2>💾 Unattached EBS Volumes</h2>"
    if report_data.get('volumes'):
        html_body += "<table><tr><th>Volume ID</th><th>Size (GB)</th><th>Availability Zone</th></tr>"
        for vol in report_data['volumes']:
            html_body += f"<tr><td>{vol['VolumeId']}</td><td>{vol['SizeGb']} GB</td><td>{vol['AvailabilityZone']}</td></tr>"
        html_body += "</table>"
    else:
        html_body += "<p class='success'>No unattached volumes found. 🎉</p>"
 
    # Table 2: Orphaned Snapshots
    html_body += "<h2>📸 Orphaned Snapshots</h2>"
    if report_data.get('snapshots'):
        html_body += "<table><tr><th>Snapshot ID</th><th>Original Volume ID</th><th>Size (GB)</th><th>Description</th></tr>"
        for snap in report_data['snapshots']:
            html_body += f"<tr><td>{snap['SnapshotId']}</td><td>{snap['VolumeId']}</td><td>{snap['SizeGb']} GB</td><td>{snap['Description']}</td></tr>"
        html_body += "</table>"
    else:
        html_body += "<p class='success'>No orphaned snapshots found. 🎉</p>"
 
    # Table 3: Idle Instances
    html_body += "<h2>🖥️ Idle EC2 Instances (Last 6 Months)</h2>"
    if report_data.get('instances'):
        html_body += "<table><tr><th>Instance ID</th><th>Max CPU %</th><th>Launch Date</th></tr>"
        for inst in report_data['instances']:
            html_body += f"<tr><td>{inst['InstanceId']}</td><td>{inst['MaxCpu']}%</td><td>{inst['LaunchTime']}</td></tr>"
        html_body += "</table>"
    else:
        html_body += "<p class='success'>No idle instances found. 🎉</p>"
 
    html_body += """
    </body>
    </html>
    """
    
    try:
        response = ses.send_email(
            Destination={'ToAddresses': [RECIPIENT]},
            Message={
                'Body': {'Html': {'Charset': "UTF-8", 'Data': html_body}},
                'Subject': {'Charset': "UTF-8", 'Data': "Weekly AWS Cost Governance Report"}
            },
            Source=SENDER
        )
        print(f"Email sent successfully! Message ID: {response['MessageId']}")
    except Exception as e:
        print(f"Error sending email via SES: {str(e)}")
        raise e
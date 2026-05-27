import json
import logging

# Import the specialized scanning functions from our new modules
from volumes import check_unattached_volumes
from snapshots import check_orphaned_snapshots
from instances import check_idle_instances
from emails import send_html_report
 
# Set up logging for production visibility
logger = logging.getLogger()
logger.setLevel(logging.INFO)
 
def lambda_handler(event, context):
    logger.info("Starting automated cost governance weekly scan...")
    
    try:
        # Gather data from each independent module
        unattached_volumes = check_unattached_volumes()
        orphaned_snapshots = check_orphaned_snapshots()
        idle_instances     = check_idle_instances()
        
        # Consolidate the findings into a single report dataset
        report_data = {
            "volumes": unattached_volumes,
            "snapshots": orphaned_snapshots,
            "instances": idle_instances
        }
        
        logger.info(f"Scan complete. Volumes: {len(unattached_volumes)}, "
                    f"Snapshots: {len(orphaned_snapshots)}, "
                    f"Instances: {len(idle_instances)}")
        
        # 3. Pass the consolidated data to the email module
        send_html_report(report_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Cost governance report sent successfully!')
        }
        
    except Exception as e:
        logger.error(f"Error during cost governance execution: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error executing scan: {str(e)}')
        }
































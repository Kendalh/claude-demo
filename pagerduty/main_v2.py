#!/usr/bin/env python3
"""
Main Command Interface
Clean command-line interface for incident management operations
"""
import sys
import argparse
import signal
import time
import yaml
from datetime import datetime
from pagerduty_client_v2 import PagerDutyAPIClient
from database_v2 import IncidentDatabase
from analytics_v2 import IncidentAnalytics


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    print(f"\n🛑 Received signal {signum}. Gracefully shutting down...")
    print("💾 Any incidents processed so far have been saved to the database.")
    sys.exit(0)


def setup_signal_handlers():
    """Setup signal handlers to prevent timeout issues"""
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    # Ignore SIGPIPE to prevent broken pipe errors
    if hasattr(signal, 'SIGPIPE'):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def load_config():
    """Load PagerDuty configuration"""
    import yaml
    try:
        with open("PagerDuty.yaml", 'r') as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        print("❌ Error: PagerDuty.yaml configuration file not found")
        sys.exit(1)


def update_incidents_command(days: int = 7, service_id: str = None):
    """Update incidents for the last X days by fetching from PagerDuty API"""
    if service_id:
        print(f"🔄 Updating incidents for service {service_id} for the last {days} days...")
    else:
        print(f"🔄 Updating incidents for all services for the last {days} days...")
    print(f"⏱️ This may take several minutes for escalation checking...")
    start_time = datetime.now()
    
    try:
        # Load config to get API token
        config = load_config()
        api_token = config.get('token')
        if not api_token:
            print("❌ Error: No API token found in PagerDuty.yaml")
            sys.exit(1)
        
        # Initialize components
        api_client = PagerDutyAPIClient(api_token)
        database = IncidentDatabase()
        
        # Keep connection alive and show progress
        last_heartbeat = time.time()
        
        def show_heartbeat():
            nonlocal last_heartbeat
            current_time = time.time()
            if current_time - last_heartbeat > 30:  # Every 30 seconds
                elapsed = current_time - start_time.timestamp()
                print(f"💓 Still processing... ({elapsed:.0f}s elapsed)")
                last_heartbeat = current_time
        
        # Fetch incidents from PagerDuty API with escalation checking
        print("🌐 Starting API calls to PagerDuty...")
        if service_id:
            # Validate service ID exists in config
            service_ids, service_id_to_name = api_client.load_services_from_config()
            if service_id not in service_ids:
                print(f"❌ Service ID {service_id} not found in PagerDuty.yaml")
                print(f"💡 Available services: {', '.join(service_ids)}")
                sys.exit(1)
            incidents = api_client.fetch_incidents_for_date_range(days=days, service_ids=[service_id])
        else:
            incidents = api_client.fetch_incidents_for_date_range(days=days)
        
        if not incidents:
            print("ℹ️ No incidents found for the specified period")
            return
        
        # Store incidents in database
        print("💾 Storing incidents in database...")
        stored_count = database.store_incidents_batch(incidents)
        
        # Calculate execution time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Summary
        escalated_count = sum(1 for incident in incidents if incident.is_escalated)
        print(f"\n📊 Update Summary:")
        print(f"   Period: Last {days} days")
        print(f"   Total incidents fetched: {len(incidents)}")
        print(f"   Incidents stored: {stored_count}")
        print(f"   Escalated incidents: {escalated_count}")
        print(f"   Execution time: {duration:.2f} seconds ({duration/60:.1f} minutes)")
        print(f"✅ Update completed successfully")
        
    except KeyboardInterrupt:
        print(f"\n🛑 Operation cancelled by user after {(datetime.now() - start_time).total_seconds():.1f} seconds")
        print("💾 Any processed incidents have been saved to the database")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error during update: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def show_summary_command(days: int = 7):
    """Show summary metrics for the last X days"""
    print(f"📊 Incident Summary - Last {days} Days")
    print("=" * 50)
    
    try:
        analytics = IncidentAnalytics()
        summary = analytics.get_summary_metrics(days)
        
        # Overall metrics
        print(f"\n🔢 Overall Metrics:")
        print(f"   Total incidents: {summary['total_incidents']}")
        print(f"   Triggered incidents: {summary['triggered_incidents']}")
        print(f"   Resolved incidents: {summary['resolved_incidents']}")
        print(f"   Escalated incidents: {summary['escalated_incidents']}")
        print(f"   Escalation rate: {summary['escalation_rate']}%")
        print(f"   Services monitored: {summary['services_count']}")
        
        # Service breakdown
        if summary['service_metrics']:
            print(f"\n🔧 Service Breakdown:")
            for service in sorted(summary['service_metrics'], key=lambda x: x.total_incidents, reverse=True):
                print(f"\n    Serivce Name: {service.service_name}")
                print(f"      Service ID: {service.service_id}")
                print(f"      Total incidents: {service.total_incidents}")
                print(f"      • Triggered: {service.triggered_incidents}")
                print(f"      • Resolved: {service.resolved_incidents}")
                print(f"      • Escalated: {service.escalated_incidents} ({service.escalation_rate:.1f}%)")
        else:
            print(f"\n⚠️ No service metrics available - this may indicate missing service data")
        
        # Top escalated services
        top_escalated = analytics.get_top_escalated_services(days, limit=3)
        if any(s.escalated_incidents > 0 for s in top_escalated):
            print(f"\n🚨 Top Escalated Services:")
            for i, service in enumerate(top_escalated[:3], 1):
                if service.escalated_incidents > 0:
                    print(f"   {i}. {service.service_name}: {service.escalated_incidents} escalated ({service.escalation_rate:.1f}%)")
        
        # Daily trend (last 7 days only for readability)
        if days <= 7 and summary['daily_trend']:
            print(f"\n📈 Daily Trend:")
            for day in summary['daily_trend']:
                print(f"   {day['date']}: {day['total_incidents']} total, {day['escalated_incidents']} escalated")
        
        if summary['total_incidents'] == 0:
            print(f"\nℹ️ No incidents found for the last {days} days")
            print("💡 Run 'python3 main_v2.py --update-incidents' to fetch data from PagerDuty")
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        sys.exit(1)


def show_escalations_command(days: int = 7):
    """Show only escalated incidents for the last X days"""
    print(f"🚨 Escalated Incidents - Last {days} Days")
    print("=" * 50)
    
    try:
        database = IncidentDatabase()
        escalated_incidents = database.get_escalated_incidents_last_x_days(days)
        
        if not escalated_incidents:
            print(f"✅ No escalated incidents found in the last {days} days")
            return
        
        print(f"Found {len(escalated_incidents)} escalated incidents:\n")
        
        for incident in escalated_incidents:
            print(f"📍 {incident.service_name}")
            print(f"   ID: {incident.id}")
            print(f"   Title: {incident.title}")
            print(f"   Status: {incident.status}")
            print(f"   Created: {incident.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"   Urgency: {incident.urgency}")
            if incident.priority:
                print(f"   Priority: {incident.priority}")
            if incident.escalation_policy_name:
                print(f"   Escalation Policy: {incident.escalation_policy_name}")
            print()
        
    except Exception as e:
        print(f"❌ Error retrieving escalated incidents: {e}")
        sys.exit(1)


def show_database_info_command():
    """Show database information and statistics"""
    print("🗄️ Database Information")
    print("=" * 30)
    
    try:
        database = IncidentDatabase()
        
        total_incidents = database.get_incident_count()
        service_ids = database.get_all_service_ids()
        
        print(f"Total incidents in database: {total_incidents}")
        print(f"Services tracked: {len(service_ids)}")
        
        if service_ids:
            print(f"Service IDs: {', '.join(service_ids)}")
        
        # Show some recent incidents
        recent_incidents = database.get_incidents_last_x_days(1)
        print(f"Incidents from last 24 hours: {len(recent_incidents)}")
        
    except Exception as e:
        print(f"❌ Error retrieving database info: {e}")
        sys.exit(1)


def cleanup_old_data_command(days: int = 30):
    """Clean up incidents older than X days"""
    print(f"🧹 Cleaning up incidents older than {days} days...")
    
    try:
        database = IncidentDatabase()
        deleted_count = database.delete_incidents_older_than_days(days)
        
        if deleted_count > 0:
            print(f"✅ Deleted {deleted_count} old incidents")
        else:
            print("ℹ️ No old incidents to delete")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        sys.exit(1)


def get_incident_command(incident_id: str):
    """Get and display incident details by ID"""
    print(f"🔍 Looking up incident: {incident_id}")
    
    try:
        database = IncidentDatabase()
        incident = database.get_incident_by_id(incident_id)
        
        if incident:
            print(f"\n📋 Incident Details:")
            print(f"   ID: {incident.id}")
            print(f"   Title: {incident.title}")
            print(f"   Status: {incident.status}")
            print(f"   Service: {incident.service_name} ({incident.service_id})")
            print(f"   Urgency: {incident.urgency}")
            print(f"   Created: {incident.created_at}")
            
            if incident.acknowledged_at:
                print(f"   Acknowledged: {incident.acknowledged_at}")
            if incident.resolved_at:
                print(f"   Resolved: {incident.resolved_at}")
            
            print(f"   Escalated: {'Yes' if incident.is_escalated else 'No'}")
            print(f"   CCOE Resolved: {'Yes' if incident.resolved_by_ccoe else 'No'}")
            
            if incident.caused_by_infra:
                print(f"   Infrastructure Cause: {incident.caused_by_infra}")
            else:
                print(f"   Infrastructure Cause: No")
            
            if incident.escalation_policy_name:
                print(f"   Escalation Policy: {incident.escalation_policy_name}")
            if incident.priority:
                print(f"   Priority: {incident.priority}")
            if incident.description:
                print(f"   Description: {incident.description}")
            
            # PagerDuty link
            print(f"   🔗 PagerDuty URL: https://ebay-cpt.pagerduty.com/incidents/{incident.id}")
            
        else:
            print(f"❌ Incident {incident_id} not found in database")
            print("💡 Make sure the incident ID is correct and try running --update-incidents first")
        
    except Exception as e:
        print(f"❌ Error retrieving incident: {e}")
        sys.exit(1)


def update_service_date_command(service_id: str, date_str: str):
    """Update incidents for a specific service and date"""
    print(f"🔄 Updating incidents for service {service_id} on {date_str}")
    
    try:
        # Validate date format
        from datetime import datetime
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print(f"❌ Invalid date format. Please use YYYY-MM-DD (e.g., 2025-08-20)")
            sys.exit(1)
        
        # Load API token and initialize client
        with open('PagerDuty.yaml', 'r') as file:
            config = yaml.safe_load(file)
            api_token = config['token']
        
        client = PagerDutyAPIClient(api_token)
        
        # Validate service ID exists in config
        service_ids, service_id_to_name = client.load_services_from_config()
        if service_id not in service_ids:
            print(f"❌ Service ID {service_id} not found in PagerDuty.yaml")
            print(f"💡 Available services: {', '.join(service_ids)}")
            sys.exit(1)
        
        service_name = service_id_to_name.get(service_id, service_id)
        print(f"📋 Service: {service_name} ({service_id})")
        
        # Validate date
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now()
        days_ago = (today.date() - target_date.date()).days
        
        if days_ago < 0:
            print(f"❌ Cannot update future dates")
            sys.exit(1)
        elif days_ago > 30:
            print(f"⚠️ Warning: Updating data from {days_ago} days ago")
        
        # Use refactored method to fetch incidents for specific date and service
        print(f"🌐 Fetching incidents from PagerDuty API...")
        target_incidents = client.fetch_incidents_for_date_range(
            start_date=date_str,
            end_date=date_str,
            service_ids=[service_id]
        )
        
        print(f"📥 Found {len(target_incidents)} incidents for {service_name} on {date_str}")
        
        if target_incidents:
            # Store in database using existing method
            database = IncidentDatabase()
            stored_count = database.store_incidents_batch(target_incidents)
            
            ccoe_count = sum(1 for inc in target_incidents if inc.resolved_by_ccoe)
            infra_count = sum(1 for inc in target_incidents if inc.is_caused_by_infrastructure())
            escalated_count = sum(1 for inc in target_incidents if inc.is_escalated)
            
            print(f"💾 Stored {stored_count} incidents")
            print(f"📊 Summary:")
            print(f"   - Escalated: {escalated_count}")
            print(f"   - CCOE Resolved: {ccoe_count}")
            print(f"   - Infrastructure Caused: {infra_count}")
        else:
            print(f"ℹ️ No incidents found for {service_name} on {date_str}")
            
    except FileNotFoundError:
        print("❌ PagerDuty.yaml configuration file not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error updating service incidents: {e}")
        sys.exit(1)


def main():
    print("Hello Claude")
    
    # Setup signal handlers first
    setup_signal_handlers()
    
    parser = argparse.ArgumentParser(
        description='PagerDuty Incident Management Tool v2',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main_v2.py --update-incidents 7        # Update incidents for last 7 days (all services)
  python3 main_v2.py --update-incidents 7 --service P0CAL62  # Update specific service for last 7 days
  python3 main_v2.py --show-summary 14           # Show 14-day summary
  python3 main_v2.py --show-escalations          # Show escalated incidents
  python3 main_v2.py --database-info             # Show database information
  python3 main_v2.py --cleanup 60                # Delete incidents older than 60 days
  python3 main_v2.py --get-incident Q1ABC123    # Get incident details by ID
  python3 main_v2.py --update-service P0CAL62 --date 2025-08-20  # Update specific service and date
        """
    )
    
    parser.add_argument('--update-incidents', type=int, metavar='DAYS', 
                       help='Update incidents for the last X days (default: 7)')
    parser.add_argument('--service', type=str, metavar='SERVICE_ID',
                       help='Specific service ID to update (used with --update-incidents, default: all services)')
    parser.add_argument('--show-summary', type=int, metavar='DAYS', nargs='?', const=7,
                       help='Show summary metrics for the last X days (default: 7)')
    parser.add_argument('--show-escalations', type=int, metavar='DAYS', nargs='?', const=7,
                       help='Show escalated incidents for the last X days (default: 7)')
    parser.add_argument('--database-info', action='store_true',
                       help='Show database information and statistics')
    parser.add_argument('--cleanup', type=int, metavar='DAYS',
                       help='Delete incidents older than X days (default: 30)')
    parser.add_argument('--get-incident', type=str, metavar='INCIDENT_ID',
                       help='Get incident details by incident ID')
    parser.add_argument('--update-service', type=str, metavar='SERVICE_ID',
                       help='Update incidents for a specific service (requires --date)')
    parser.add_argument('--date', type=str, metavar='YYYY-MM-DD',
                       help='Specific date for service update (used with --update-service)')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.update_incidents is not None:
            days = args.update_incidents if args.update_incidents > 0 else 7
            update_incidents_command(days, args.service)
            
        elif args.show_summary is not None:
            days = args.show_summary if args.show_summary > 0 else 7
            show_summary_command(days)
            
        elif args.show_escalations is not None:
            days = args.show_escalations if args.show_escalations > 0 else 7
            show_escalations_command(days)
            
        elif args.database_info:
            show_database_info_command()
            
        elif args.cleanup is not None:
            days = args.cleanup if args.cleanup > 0 else 30
            cleanup_old_data_command(days)
            
        elif args.get_incident:
            get_incident_command(args.get_incident)
            
        elif args.update_service:
            if not args.date:
                print("❌ --date is required when using --update-service")
                print("💡 Example: python3 main_v2.py --update-service PHMCGNE --date 2025-08-20")
                sys.exit(1)
            update_service_date_command(args.update_service, args.date)
            
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
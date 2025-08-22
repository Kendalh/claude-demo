"""
PagerDuty Dashboard Web Application v2
Flask web app with service tabs, calendar views, and admin functionality
"""
from flask import Flask, render_template, jsonify, request
import subprocess
import os
import yaml
from datetime import datetime, timedelta, timezone
from database_v2 import IncidentDatabase
from analytics_v2 import IncidentAnalytics
import re
from urllib.parse import urlparse

app = Flask(__name__)

# UTC-7 timezone for consistency with backend
UTC_MINUS_7 = timezone(timedelta(hours=-7))

def load_service_config():
    """Load service configuration from PagerDuty.yaml"""
    try:
        with open('PagerDuty.yaml', 'r') as file:
            config = yaml.safe_load(file)
        
        services = {}
        for service in config.get('services', []):
            # Extract service ID from URL
            path = urlparse(service['url']).path
            service_id_match = re.search(r'/([A-Z0-9]{7})$', path)
            if service_id_match:
                service_id = service_id_match.group(1)
                services[service_id] = {
                    'name': service['name'],
                    'url': service['url']
                }
        
        return services
    except Exception as e:
        print(f"Error loading service config: {e}")
        return {}

@app.route('/')
def dashboard():
    """Main dashboard page"""
    services = load_service_config()
    return render_template('dashboard_v2.html', services=services)

@app.route('/admin')
def admin():
    """Admin page"""
    return render_template('admin_v2.html')

@app.route('/api/services')
def api_services():
    """Get all services"""
    services = load_service_config()
    return jsonify(services)

@app.route('/api/service/<service_id>/calendar')
def api_service_calendar(service_id):
    """Get calendar data for a service"""
    try:
        year = int(request.args.get('year', datetime.now().year))
        month = int(request.args.get('month', datetime.now().month))
        
        # Calculate month boundaries
        start_date = datetime(year, month, 1, tzinfo=UTC_MINUS_7).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=UTC_MINUS_7).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=UTC_MINUS_7).date() - timedelta(days=1)
        
        # Get incidents for the service
        db = IncidentDatabase()
        incidents = db.get_incidents_by_date_range(
            start_date.isoformat(),
            end_date.isoformat(),
            service_id
        )
        
        # Group incidents by date using the created_at timestamp directly
        calendar_data = {}
        for incident in incidents:
            # Extract date directly from the created_at timestamp
            if incident.created_at.tzinfo is not None:
                # Convert timezone-aware datetime to UTC-7
                utc_minus_7 = timezone(timedelta(hours=-7))
                local_time = incident.created_at.astimezone(utc_minus_7)
                incident_date = local_time.date().isoformat()
            else:
                # For naive datetime, assume it's already in the local timezone
                incident_date = incident.created_at.date().isoformat()
            
            if incident_date not in calendar_data:
                calendar_data[incident_date] = {
                    'total': 0,
                    'triggered': 0,
                    'resolved': 0,
                    'escalated': 0,
                    'ccoe_resolved': 0,
                    'infrastructure_caused': 0,
                    'escalated_incidents': []
                }
            
            calendar_data[incident_date]['total'] += 1
            
            if incident.is_triggered_or_acknowledged():
                calendar_data[incident_date]['triggered'] += 1
            elif incident.is_resolved():
                calendar_data[incident_date]['resolved'] += 1
            
            if incident.is_escalated:
                calendar_data[incident_date]['escalated'] += 1
                # Construct PagerDuty incident URL
                pagerduty_url = f"https://ebay-cpt.pagerduty.com/incidents/{incident.id}"
                calendar_data[incident_date]['escalated_incidents'].append({
                    'id': incident.id,
                    'title': incident.title,
                    'html_url': pagerduty_url,
                    'urgency': incident.urgency,
                    'status': incident.status
                })
            
            if incident.resolved_by_ccoe:
                calendar_data[incident_date]['ccoe_resolved'] += 1
            
            if incident.is_caused_by_infrastructure():
                calendar_data[incident_date]['infrastructure_caused'] += 1
        
        return jsonify(calendar_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/service/<service_id>/summary')
def api_service_summary(service_id):
    """Get summary metrics for a service"""
    try:
        days = int(request.args.get('days', 7))
        
        analytics = IncidentAnalytics()
        service_metrics = analytics.get_service_metrics_last_x_days(days)
        
        # Find metrics for this service
        service_data = None
        for service in service_metrics:
            if service.service_id == service_id:
                service_data = service
                break
        
        if not service_data:
            return jsonify({
                'service_id': service_id,
                'days': days,
                'total_incidents': 0,
                'triggered_incidents': 0,
                'resolved_incidents': 0,
                'escalated_incidents': 0,
                'escalation_rate': 0.0,
                'ccoe_resolved_incidents': 0,
                'infrastructure_caused_incidents': 0
            })
        
        return jsonify({
            'service_id': service_data.service_id,
            'service_name': service_data.service_name,
            'days': days,
            'total_incidents': service_data.total_incidents,
            'triggered_incidents': service_data.triggered_incidents,
            'resolved_incidents': service_data.resolved_incidents,
            'escalated_incidents': service_data.escalated_incidents,
            'escalation_rate': round(service_data.escalation_rate, 2),
            'ccoe_resolved_incidents': service_data.ccoe_resolved_incidents,
            'infrastructure_caused_incidents': service_data.infrastructure_caused_incidents
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/service/<service_id>/trends')
def api_service_trends(service_id):
    """Get trend data for a service"""
    try:
        days = int(request.args.get('days', 7))
        
        # Get incidents for this service
        db = IncidentDatabase()
        incidents = db.get_incidents_last_x_days(days, service_id)
        
        # Group by date using the created_at timestamp directly
        daily_data = {}
        for incident in incidents:
            # Extract date directly from the created_at timestamp
            if incident.created_at.tzinfo is not None:
                # Convert timezone-aware datetime to UTC-7
                utc_minus_7 = timezone(timedelta(hours=-7))
                local_time = incident.created_at.astimezone(utc_minus_7)
                incident_date = local_time.date().isoformat()
            else:
                # For naive datetime, assume it's already in the local timezone
                incident_date = incident.created_at.date().isoformat()
            
            if incident_date not in daily_data:
                daily_data[incident_date] = {
                    'date': incident_date,
                    'total': 0,
                    'triggered': 0,
                    'resolved': 0,
                    'escalated': 0,
                    'ccoe_resolved': 0,
                    'infrastructure_caused': 0
                }
            
            daily_data[incident_date]['total'] += 1
            
            if incident.is_triggered_or_acknowledged():
                daily_data[incident_date]['triggered'] += 1
            elif incident.is_resolved():
                daily_data[incident_date]['resolved'] += 1
            
            if incident.is_escalated:
                daily_data[incident_date]['escalated'] += 1
            
            if incident.resolved_by_ccoe:
                daily_data[incident_date]['ccoe_resolved'] += 1
            
            if incident.is_caused_by_infrastructure():
                daily_data[incident_date]['infrastructure_caused'] += 1
        
        # Convert to sorted list
        trend_data = list(daily_data.values())
        trend_data.sort(key=lambda x: x['date'])
        
        return jsonify(trend_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/update', methods=['POST'])
def api_admin_update():
    """Trigger incident data update"""
    try:
        data = request.get_json() or {}
        days = min(int(data.get('days', 7)), 7)  # Max 7 days
        
        # Execute the update command
        cmd = ['python3', 'main_v2.py', '--update-incidents', str(days)]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            timeout=1800  # 30 minutes
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': f'Successfully updated incidents for last {days} days',
                'output': result.stdout,
                'days': days
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to update incidents',
                'error': result.stderr,
                'days': days
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': 'Update command timed out after 30 minutes'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/stats')
def api_stats():
    """Get system statistics"""
    try:
        db = IncidentDatabase()
        analytics = IncidentAnalytics()
        
        total_count = db.get_incident_count()
        service_ids = db.get_all_service_ids()
        
        recent_7d = analytics.get_total_incidents_last_x_days(7)
        escalated_7d = analytics.get_escalated_incidents_last_x_days(7)
        
        return jsonify({
            'total_incidents': total_count,
            'services_count': len(service_ids),
            'incidents_last_7_days': recent_7d.value,
            'escalated_last_7_days': escalated_7d.value,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
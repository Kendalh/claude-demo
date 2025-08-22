"""
PagerDuty API Client
Centralized client for fetching incidents from PagerDuty API with escalation checking
"""
import requests
import yaml
from typing import List, Dict, Any
from urllib.parse import urlparse
import re
from datetime import datetime, timedelta, timezone
from incident_v2 import Incident


class PagerDutyAPIClient:
    """Centralized PagerDuty API client that fetches incidents and checks escalation status"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.pagerduty.com"
        self.headers = {
            "Authorization": f"Token token={api_token}",
            "Accept": "application/vnd.pagerduty+json;version=2"
        }
        # UTC-7 timezone for date calculations
        self.utc_minus_7 = timezone(timedelta(hours=-7))
    
    def load_services_from_config(self, config_path: str = "PagerDuty.yaml") -> tuple[List[str], Dict[str, str]]:
        """Load service IDs and names from PagerDuty.yaml configuration"""
        with open(config_path, 'r') as file:
            data = yaml.safe_load(file)
        
        service_ids = []
        service_id_to_name = {}
        
        for service in data.get('services', []):
            service_url = service['url']
            service_name = service['name']
            service_id = self._extract_service_id(service_url)
            service_ids.append(service_id)
            service_id_to_name[service_id] = service_name
        
        return service_ids, service_id_to_name
    
    def _extract_service_id(self, service_url: str) -> str:
        """Extract service ID from PagerDuty service URL"""
        path = urlparse(service_url).path
        service_id_match = re.search(r'/([A-Z0-9]{7})$', path)
        if service_id_match:
            return service_id_match.group(1)
        raise ValueError(f"Could not extract service ID from URL: {service_url}")
    
    def fetch_incidents_for_date_range(self, start_date: str = None, end_date: str = None, days: int = 7, service_ids: List[str] = None) -> List[Incident]:
        """
        Fetch incidents for a date range (UTC-7 timezone) with escalation checking
        Args:
            start_date: Start date in YYYY-MM-DD format (UTC-7), if None uses days parameter
            end_date: End date in YYYY-MM-DD format (UTC-7), if None uses today
            days: Number of days back from end_date (only used if start_date is None)
            service_ids: List of specific service IDs to fetch, if None fetches all configured services
        Returns:
            List of Incident objects with escalation status determined from log entries
        """
        # Load service IDs and names from config
        all_service_ids, service_id_to_name = self.load_services_from_config()
        
        # Use provided service_ids or default to all configured services
        if service_ids is None:
            service_ids = all_service_ids
        else:
            # Validate provided service IDs
            invalid_ids = [sid for sid in service_ids if sid not in all_service_ids]
            if invalid_ids:
                raise ValueError(f"Invalid service IDs: {invalid_ids}. Available: {all_service_ids}")
        
        # Calculate date range in UTC-7 timezone
        if end_date:
            end_time = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=self.utc_minus_7)
            end_time = end_time.replace(hour=23, minute=59, second=59)
        else:
            end_time = datetime.now(self.utc_minus_7)
        
        if start_date:
            start_time = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=self.utc_minus_7)
            days_range = (end_time.date() - start_time.date()).days + 1
            print(f"🔄 Fetching incidents from {start_date} to {end_time.strftime('%Y-%m-%d')} ({days_range} days)")
        else:
            start_time = end_time - timedelta(days=days-1)
            start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            print(f"🔄 Fetching incidents for last {days} days (UTC-7 timezone)...")
        
        print(f"📋 Monitoring {len(service_ids)} services:")
        for service_id in service_ids:
            service_name = service_id_to_name.get(service_id, service_id)
            print(f"   {service_id}: {service_name}")
        
        # Convert to ISO format for API
        since = start_time.isoformat()
        until = end_time.isoformat()
        
        print(f"📅 Date range: {start_time.date()} to {end_time.date()} (UTC-7)")
        
        # Fetch raw incidents from API
        raw_incidents = self._fetch_incidents_from_api(service_ids, since, until)
        print(f"📥 Fetched {len(raw_incidents)} raw incidents from PagerDuty API")
        
        # Process each incident and check escalation status
        incidents = []
        escalated_count = 0
        total_incidents = len(raw_incidents)
        
        print(f"🔍 Checking escalation status for {total_incidents} incidents...")
        print(f"⚡ Processing in batches to prevent timeouts...")
        
        # Process in smaller batches to save progress incrementally
        batch_size = 20
        processed_count = 0
        
        for batch_start in range(0, total_incidents, batch_size):
            batch_end = min(batch_start + batch_size, total_incidents)
            batch = raw_incidents[batch_start:batch_end]
            
            print(f"📦 Processing batch {batch_start//batch_size + 1}/{(total_incidents + batch_size - 1)//batch_size} (incidents {batch_start + 1}-{batch_end})")
            
            for raw_incident in batch:
                incident_id = raw_incident['id']
                processed_count += 1
                
                # Show progress every 10 incidents
                if processed_count % 10 == 0 or processed_count == total_incidents:
                    print(f"   Progress: {processed_count}/{total_incidents} incidents processed ({processed_count/total_incidents*100:.1f}%)")
                
                # Check escalation status via log entries and fetch custom fields in parallel
                is_escalated = self._check_incident_escalation(incident_id)
                custom_fields = self._get_incident_custom_fields(incident_id)
                
                if is_escalated:
                    escalated_count += 1
                    print(f"🚨 Incident {incident_id} is escalated")
                
                # Convert to Incident object with proper service name mapping and custom fields
                incident = self._convert_to_incident_object(raw_incident, is_escalated, service_id_to_name, custom_fields)
                incidents.append(incident)
            
            # Show batch completion
            print(f"✅ Batch {batch_start//batch_size + 1} completed ({len(batch)} incidents)")
            
            # Small delay between batches to be nice to the API
            if batch_end < total_incidents:
                import time
                time.sleep(1)
        
        print(f"✅ Processed {len(incidents)} incidents ({escalated_count} escalated)")
        return incidents
    
    def _fetch_incidents_from_api(self, service_ids: List[str], since: str, until: str) -> List[Dict[str, Any]]:
        """Fetch incidents from PagerDuty API with pagination"""
        url = f"{self.base_url}/incidents"
        
        all_incidents = []
        offset = 0
        limit = 100
        
        while True:
            params = {
                "service_ids[]": service_ids,
                "since": since,
                "until": until,
                "limit": limit,
                "offset": offset,
                "sort_by": "created_at:desc"
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=1800)  # 30 minutes
            response.raise_for_status()
            
            data = response.json()
            incidents = data.get("incidents", [])
            
            if not incidents:
                break
            
            all_incidents.extend(incidents)
            
            # Check if there are more pages
            if not data.get("more", False) or len(incidents) < limit:
                break
            
            offset += limit
        
        return all_incidents
    
    def fetch_incidents_for_last_x_days(self, days: int = 7) -> List[Incident]:
        """
        Convenience method for backward compatibility
        Fetch incidents for the last X days (UTC-7 timezone)
        """
        return self.fetch_incidents_for_date_range(days=days)
    
    def _check_incident_escalation(self, incident_id: str) -> bool:
        """
        Check if incident has been escalated by examining log entries
        Returns True if any log entry has type 'escalate_log_entry'
        """
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}/incidents/{incident_id}/log_entries"
                params = {
                    "limit": 100,
                    "include[]": ["channels"],
                    "is_overview": "false"
                }
                
                # Use shorter timeout for individual requests (30 seconds)
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                response.raise_for_status()
                
                log_entries = response.json().get("log_entries", [])
                
                # Check for escalate_log_entry type
                for log_entry in log_entries:
                    if log_entry.get('type') == 'escalate_log_entry':
                        return True
                
                return False
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⏱️ Timeout checking incident {incident_id}, retrying ({attempt + 1}/{max_retries})...")
                    import time
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"⚠️ Final timeout for incident {incident_id}, skipping escalation check")
                    return False
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Error checking incident {incident_id}: {e}, retrying ({attempt + 1}/{max_retries})...")
                    import time
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"⚠️ Final error for incident {incident_id}: {e}")
                    return False
        
        return False
    
    def _get_incident_custom_fields(self, incident_id: str) -> Dict[str, Any]:
        """
        Fetch custom fields for an incident
        Returns dict with resolution and prelim_root_cause values
        """
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}/incidents/{incident_id}/custom_fields/values"
                
                # Use shorter timeout for individual requests (30 seconds)
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                custom_fields = response.json().get("custom_fields", [])
                
                # Extract resolution and prelim_root_cause values
                result = {
                    'resolution': None,
                    'prelim_root_cause': None
                }
                
                for field in custom_fields:
                    field_name = field.get('name', '').lower()
                    field_value = field.get('value')
                    
                    if field_name == 'resolution' and field_value:
                        result['resolution'] = field_value.lower().strip()
                    elif field_name == 'prelim_root_cause' and field_value:
                        result['prelim_root_cause'] = field_value.lower().strip()
                
                return result
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⏱️ Timeout fetching custom fields for incident {incident_id}, retrying ({attempt + 1}/{max_retries})...")
                    import time
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"⚠️ Final timeout for custom fields incident {incident_id}")
                    return {'resolution': None, 'prelim_root_cause': None}
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Error fetching custom fields for incident {incident_id}: {e}, retrying ({attempt + 1}/{max_retries})...")
                    import time
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"⚠️ Final error fetching custom fields for incident {incident_id}: {e}")
                    return {'resolution': None, 'prelim_root_cause': None}
        
        return {'resolution': None, 'prelim_root_cause': None}
    
    def _convert_to_incident_object(self, raw_incident: Dict[str, Any], is_escalated: bool, service_id_to_name: Dict[str, str], custom_fields: Dict[str, Any] = None) -> Incident:
        """Convert raw PagerDuty API response to Incident object"""
        service = raw_incident.get('service', {})
        escalation_policy = raw_incident.get('escalation_policy', {})
        
        # Get service info - prefer config name over API name for consistency
        service_id = service.get('id', '')
        service_name = service_id_to_name.get(service_id, service.get('name', ''))
        
        # Parse timestamps and convert to UTC-7
        created_at = datetime.fromisoformat(raw_incident['created_at'].replace('Z', '+00:00'))
        created_at = created_at.astimezone(self.utc_minus_7)
        
        resolved_at = None
        if raw_incident.get('resolved_at'):
            resolved_at = datetime.fromisoformat(raw_incident['resolved_at'].replace('Z', '+00:00'))
            resolved_at = resolved_at.astimezone(self.utc_minus_7)
        
        acknowledged_at = None
        # Check if there's acknowledgment information
        acknowledgments = raw_incident.get('acknowledgments', [])
        if acknowledgments:
            # Get the first acknowledgment timestamp
            ack_time_str = acknowledgments[0].get('at', '')
            if ack_time_str:
                acknowledged_at = datetime.fromisoformat(ack_time_str.replace('Z', '+00:00'))
                acknowledged_at = acknowledged_at.astimezone(self.utc_minus_7)
        
        # Process custom fields
        custom_fields = custom_fields or {}
        resolved_by_ccoe = custom_fields.get('resolution').lower() == 'ccoe'
        caused_by_infra = custom_fields.get('prelim_root_cause')
        
        return Incident(
            id=raw_incident['id'],
            title=raw_incident.get('title', ''),
            status=raw_incident['status'],
            service_id=service_id,
            service_name=service_name,
            created_at=created_at,
            resolved_at=resolved_at,
            acknowledged_at=acknowledged_at,
            is_escalated=is_escalated,
            escalation_policy_id=escalation_policy.get('id'),
            escalation_policy_name=escalation_policy.get('name'),
            urgency=raw_incident.get('urgency', 'low'),
            priority=raw_incident.get('priority', {}).get('name') if raw_incident.get('priority') else None,
            description=raw_incident.get('description', ''),
            resolved_by_ccoe=resolved_by_ccoe,
            caused_by_infra=caused_by_infra
        )
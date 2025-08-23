"""
Tests for Incident data model (incident_v2.py)
Tests the pure data transfer object with no external dependencies
"""
import pytest
from datetime import datetime, timezone, timedelta
from freezegun import freeze_time

from incident_v2 import Incident


class TestIncidentDataModel:
    """Test suite for the Incident data model"""
    
    def test_incident_initialization(self, sample_incident_data):
        """Test basic incident initialization with all fields"""
        incident = Incident(**sample_incident_data)
        
        assert incident.id == 'Q1ABC123DEF'
        assert incident.title == 'Test incident'
        assert incident.status == 'resolved'
        assert incident.service_id == 'PHMCGNE'
        assert incident.service_name == 'Test Service'
        assert incident.is_escalated is False
        assert incident.urgency == 'high'
        assert incident.priority == 'P2'
        assert incident.resolved_by_ccoe is True
        assert incident.caused_by_infra == 'rheos'
    
    def test_incident_minimal_initialization(self, utc_minus_7):
        """Test incident initialization with only required fields"""
        minimal_data = {
            'id': 'MIN123',
            'title': 'Minimal incident',
            'status': 'triggered',
            'service_id': 'SERVICE1',
            'service_name': 'Minimal Service',
            'created_at': datetime(2025, 8, 23, 10, 0, 0, tzinfo=utc_minus_7)
        }
        
        incident = Incident(**minimal_data)
        
        assert incident.id == 'MIN123'
        assert incident.resolved_at is None
        assert incident.acknowledged_at is None
        assert incident.is_escalated is False
        assert incident.urgency == 'low'  # default value
        assert incident.priority is None
        assert incident.resolved_by_ccoe is False  # default value
        assert incident.caused_by_infra is None
    
    def test_to_dict_conversion(self, sample_incident):
        """Test conversion from Incident object to dictionary"""
        incident_dict = sample_incident.to_dict()
        
        assert incident_dict['id'] == 'Q1ABC123DEF'
        assert incident_dict['title'] == 'Test incident'
        assert incident_dict['status'] == 'resolved'
        assert incident_dict['service_id'] == 'PHMCGNE'
        assert incident_dict['service_name'] == 'Test Service'
        assert incident_dict['is_escalated'] is False
        assert incident_dict['urgency'] == 'high'
        assert incident_dict['priority'] == 'P2'
        assert incident_dict['resolved_by_ccoe'] is True
        assert incident_dict['caused_by_infra'] == 'rheos'
        
        # Check datetime serialization
        assert incident_dict['created_at'].endswith('-07:00')
        assert incident_dict['resolved_at'].endswith('-07:00')
        assert incident_dict['acknowledged_at'].endswith('-07:00')
    
    def test_to_dict_with_none_values(self, utc_minus_7):
        """Test to_dict handles None values correctly"""
        incident = Incident(
            id='NONE123',
            title='Test with nones',
            status='triggered',
            service_id='SERVICE1',
            service_name='Test Service',
            created_at=datetime(2025, 8, 23, 10, 0, 0, tzinfo=utc_minus_7),
            resolved_at=None,
            acknowledged_at=None,
            priority=None,
            description=None,
            caused_by_infra=None
        )
        
        incident_dict = incident.to_dict()
        
        assert incident_dict['resolved_at'] is None
        assert incident_dict['acknowledged_at'] is None
        assert incident_dict['priority'] is None
        assert incident_dict['description'] is None
        assert incident_dict['caused_by_infra'] is None
    
    def test_from_dict_conversion(self, sample_incident_data):
        """Test conversion from dictionary to Incident object"""
        # Convert to dict format (with ISO datetime strings)
        original_incident = Incident(**sample_incident_data)
        incident_dict = original_incident.to_dict()
        
        # Convert back to Incident
        reconstructed_incident = Incident.from_dict(incident_dict)
        
        assert reconstructed_incident.id == original_incident.id
        assert reconstructed_incident.title == original_incident.title
        assert reconstructed_incident.status == original_incident.status
        assert reconstructed_incident.service_id == original_incident.service_id
        assert reconstructed_incident.service_name == original_incident.service_name
        assert reconstructed_incident.is_escalated == original_incident.is_escalated
        assert reconstructed_incident.urgency == original_incident.urgency
        assert reconstructed_incident.priority == original_incident.priority
        assert reconstructed_incident.resolved_by_ccoe == original_incident.resolved_by_ccoe
        assert reconstructed_incident.caused_by_infra == original_incident.caused_by_infra
        
        # Check datetime fields
        assert reconstructed_incident.created_at == original_incident.created_at
        assert reconstructed_incident.resolved_at == original_incident.resolved_at
        assert reconstructed_incident.acknowledged_at == original_incident.acknowledged_at
    
    def test_from_dict_with_none_datetime(self, utc_minus_7):
        """Test from_dict handles None datetime values correctly"""
        incident_dict = {
            'id': 'NONE123',
            'title': 'Test with none datetimes',
            'status': 'triggered',
            'service_id': 'SERVICE1',
            'service_name': 'Test Service',
            'created_at': datetime(2025, 8, 23, 10, 0, 0, tzinfo=utc_minus_7).isoformat(),
            'resolved_at': None,
            'acknowledged_at': None,
            'is_escalated': False,
            'escalation_policy_id': 'POLICY123',
            'escalation_policy_name': 'Test Policy',
            'urgency': 'low',
            'priority': 'P3',
            'description': 'Test description',
            'resolved_by_ccoe': False,
            'caused_by_infra': None
        }
        
        incident = Incident.from_dict(incident_dict)
        
        assert incident.resolved_at is None
        assert incident.acknowledged_at is None
        assert incident.created_at.tzinfo is not None
    
    def test_from_dict_boolean_conversion(self):
        """Test from_dict properly converts boolean fields"""
        incident_dict = {
            'id': 'BOOL123',
            'title': 'Boolean test',
            'status': 'resolved',
            'service_id': 'SERVICE1',
            'service_name': 'Test Service',
            'created_at': '2025-08-23T10:00:00-07:00',
            'resolved_at': '2025-08-23T11:00:00-07:00',
            'acknowledged_at': '2025-08-23T10:15:00-07:00',
            'is_escalated': 1,  # SQLite boolean as integer
            'escalation_policy_id': 'POLICY123',
            'escalation_policy_name': 'Test Policy',
            'urgency': 'high',
            'priority': 'P1',
            'description': 'Boolean test',
            'resolved_by_ccoe': 1,  # SQLite boolean as integer
            'caused_by_infra': 'rheos'
        }
        
        incident = Incident.from_dict(incident_dict)
        
        assert incident.is_escalated is True
        assert incident.resolved_by_ccoe is True
    
    def test_get_date_str_utc_minus_7_with_timezone_aware(self, utc_minus_7):
        """Test date string extraction with timezone-aware datetime"""
        incident = Incident(
            id='TZ123',
            title='Timezone test',
            status='triggered',
            service_id='SERVICE1',
            service_name='Test Service',
            created_at=datetime(2025, 8, 23, 15, 30, 0, tzinfo=timezone.utc)  # UTC time
        )
        
        date_str = incident.get_date_str_utc_minus_7()
        
        # UTC 15:30 becomes UTC-7 08:30, same date
        assert date_str == '2025-08-23'
    
    def test_get_date_str_utc_minus_7_with_naive_datetime(self):
        """Test date string extraction with naive datetime (assumes UTC-7)"""
        incident = Incident(
            id='NAIVE123',
            title='Naive timezone test',
            status='triggered',
            service_id='SERVICE1',
            service_name='Test Service',
            created_at=datetime(2025, 8, 23, 10, 30, 0)  # Naive datetime
        )
        
        date_str = incident.get_date_str_utc_minus_7()
        
        # Naive datetime assumed to be in UTC-7
        assert date_str == '2025-08-23'
    
    @freeze_time("2025-08-23 18:00:00")  # UTC time
    def test_get_date_str_timezone_conversion(self):
        """Test timezone conversion edge case around date boundaries"""
        # Create incident at UTC midnight (previous day in UTC-7)
        incident = Incident(
            id='EDGE123',
            title='Edge case test',
            status='triggered',
            service_id='SERVICE1',
            service_name='Test Service',
            created_at=datetime(2025, 8, 24, 0, 30, 0, tzinfo=timezone.utc)  # UTC midnight
        )
        
        date_str = incident.get_date_str_utc_minus_7()
        
        # UTC 00:30 on 8/24 becomes UTC-7 17:30 on 8/23
        assert date_str == '2025-08-23'
    
    def test_is_triggered_or_acknowledged(self):
        """Test status checking for triggered/acknowledged states"""
        triggered_incident = Incident(
            id='TRIG123', title='Triggered', status='triggered',
            service_id='S1', service_name='Service',
            created_at=datetime.now()
        )
        
        acknowledged_incident = Incident(
            id='ACK123', title='Acknowledged', status='acknowledged',
            service_id='S1', service_name='Service',
            created_at=datetime.now()
        )
        
        resolved_incident = Incident(
            id='RES123', title='Resolved', status='resolved',
            service_id='S1', service_name='Service',
            created_at=datetime.now()
        )
        
        assert triggered_incident.is_triggered_or_acknowledged() is True
        assert acknowledged_incident.is_triggered_or_acknowledged() is True
        assert resolved_incident.is_triggered_or_acknowledged() is False
    
    def test_is_triggered_or_acknowledged_case_insensitive(self):
        """Test status checking is case insensitive"""
        incident = Incident(
            id='CASE123', title='Case test', status='TRIGGERED',
            service_id='S1', service_name='Service',
            created_at=datetime.now()
        )
        
        assert incident.is_triggered_or_acknowledged() is True
    
    def test_is_resolved(self):
        """Test resolved status checking"""
        resolved_incident = Incident(
            id='RES123', title='Resolved', status='resolved',
            service_id='S1', service_name='Service',
            created_at=datetime.now()
        )
        
        triggered_incident = Incident(
            id='TRIG123', title='Triggered', status='triggered',
            service_id='S1', service_name='Service',
            created_at=datetime.now()
        )
        
        assert resolved_incident.is_resolved() is True
        assert triggered_incident.is_resolved() is False
    
    def test_is_resolved_case_insensitive(self):
        """Test resolved status checking is case insensitive"""
        incident = Incident(
            id='CASE123', title='Case test', status='RESOLVED',
            service_id='S1', service_name='Service',
            created_at=datetime.now()
        )
        
        assert incident.is_resolved() is True
    
    def test_is_caused_by_infrastructure_with_value(self):
        """Test infrastructure cause detection with non-empty value"""
        incident = Incident(
            id='INFRA123', title='Infrastructure issue', status='resolved',
            service_id='S1', service_name='Service',
            created_at=datetime.now(),
            caused_by_infra='rheos'
        )
        
        assert incident.is_caused_by_infrastructure() is True
    
    def test_is_caused_by_infrastructure_with_empty_value(self):
        """Test infrastructure cause detection with empty/None values"""
        none_incident = Incident(
            id='NONE123', title='No infra cause', status='resolved',
            service_id='S1', service_name='Service',
            created_at=datetime.now(),
            caused_by_infra=None
        )
        
        empty_incident = Incident(
            id='EMPTY123', title='Empty infra cause', status='resolved',
            service_id='S1', service_name='Service',
            created_at=datetime.now(),
            caused_by_infra=''
        )
        
        whitespace_incident = Incident(
            id='WS123', title='Whitespace infra cause', status='resolved',
            service_id='S1', service_name='Service',
            created_at=datetime.now(),
            caused_by_infra='   '
        )
        
        assert none_incident.is_caused_by_infrastructure() is False
        assert empty_incident.is_caused_by_infrastructure() is False
        assert whitespace_incident.is_caused_by_infrastructure() is False
    
    def test_roundtrip_serialization(self, sample_incident):
        """Test that to_dict -> from_dict preserves all data"""
        original = sample_incident
        dict_form = original.to_dict()
        reconstructed = Incident.from_dict(dict_form)
        
        # Test all fields are preserved
        assert original.id == reconstructed.id
        assert original.title == reconstructed.title
        assert original.status == reconstructed.status
        assert original.service_id == reconstructed.service_id
        assert original.service_name == reconstructed.service_name
        assert original.created_at == reconstructed.created_at
        assert original.resolved_at == reconstructed.resolved_at
        assert original.acknowledged_at == reconstructed.acknowledged_at
        assert original.is_escalated == reconstructed.is_escalated
        assert original.escalation_policy_id == reconstructed.escalation_policy_id
        assert original.escalation_policy_name == reconstructed.escalation_policy_name
        assert original.urgency == reconstructed.urgency
        assert original.priority == reconstructed.priority
        assert original.description == reconstructed.description
        assert original.resolved_by_ccoe == reconstructed.resolved_by_ccoe
        assert original.caused_by_infra == reconstructed.caused_by_infra
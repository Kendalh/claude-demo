"""
Pytest configuration and shared fixtures for PagerDuty Incident Analytics tests
"""
import pytest
import tempfile
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
import sqlite3

# Add parent directory to path to import modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from incident_v2 import Incident
from database_v2 import IncidentDatabase


@pytest.fixture
def utc_minus_7():
    """UTC-7 timezone for testing"""
    return timezone(timedelta(hours=-7))


@pytest.fixture
def sample_incident_data(utc_minus_7):
    """Sample incident data for testing"""
    return {
        'id': 'Q1ABC123DEF',
        'title': 'Test incident',
        'status': 'resolved',
        'service_id': 'PHMCGNE',
        'service_name': 'Test Service',
        'created_at': datetime(2025, 8, 23, 10, 0, 0, tzinfo=utc_minus_7),
        'resolved_at': datetime(2025, 8, 23, 11, 0, 0, tzinfo=utc_minus_7),
        'acknowledged_at': datetime(2025, 8, 23, 10, 15, 0, tzinfo=utc_minus_7),
        'is_escalated': False,
        'escalation_policy_id': 'POLICY123',
        'escalation_policy_name': 'Default Escalation',
        'urgency': 'high',
        'priority': 'P2',
        'description': 'Test incident description',
        'resolved_by_ccoe': True,
        'caused_by_infra': 'rheos'
    }


@pytest.fixture
def sample_incident(sample_incident_data):
    """Sample Incident object for testing"""
    return Incident(**sample_incident_data)


@pytest.fixture
def sample_incidents(utc_minus_7):
    """Multiple sample incidents for testing"""
    base_time = datetime(2025, 8, 23, 10, 0, 0, tzinfo=utc_minus_7)
    
    incidents = []
    for i in range(5):
        incidents.append(Incident(
            id=f'Q{i}ABC123DEF',
            title=f'Test incident {i}',
            status='resolved' if i % 2 == 0 else 'triggered',
            service_id='PHMCGNE',
            service_name='Test Service',
            created_at=base_time + timedelta(hours=i),
            resolved_at=base_time + timedelta(hours=i+1) if i % 2 == 0 else None,
            acknowledged_at=base_time + timedelta(minutes=15+i*5),
            is_escalated=i % 3 == 0,
            escalation_policy_id='POLICY123',
            escalation_policy_name='Default Escalation',
            urgency='high' if i % 2 == 0 else 'low',
            priority=f'P{i+1}',
            description=f'Test incident {i} description',
            resolved_by_ccoe=i % 2 == 0,
            caused_by_infra='rheos' if i % 3 == 0 else None
        ))
    return incidents


@pytest.fixture
def temp_db():
    """Temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def test_db(temp_db):
    """Test database instance with initialized schema"""
    db = IncidentDatabase(temp_db)
    return db


@pytest.fixture
def mock_pagerduty_config():
    """Mock PagerDuty configuration data"""
    return {
        'token': 'test_api_token_12345',
        'services': [
            {
                'name': 'Test Service 1',
                'url': 'https://company.pagerduty.com/service-directory/PHMCGNE'
            },
            {
                'name': 'Test Service 2', 
                'url': 'https://company.pagerduty.com/service-directory/PABCDEF'
            }
        ]
    }


@pytest.fixture
def mock_pagerduty_incident_response():
    """Mock PagerDuty API incident response"""
    return {
        'incidents': [
            {
                'id': 'Q1ABC123DEF',
                'title': 'Test incident from API',
                'status': 'resolved',
                'service': {
                    'id': 'PHMCGNE',
                    'summary': 'Test Service'
                },
                'created_at': '2025-08-23T10:00:00-07:00',
                'updated_at': '2025-08-23T11:00:00-07:00',
                'escalation_policy': {
                    'id': 'POLICY123',
                    'summary': 'Default Escalation'
                },
                'urgency': 'high',
                'priority': {
                    'summary': 'P2'
                },
                'description': 'Test incident from API',
                'custom_fields': [
                    {
                        'field': {
                            'name': 'resolution'
                        },
                        'value': 'ccoe'
                    },
                    {
                        'field': {
                            'name': 'prelim_root_cause'
                        },
                        'value': 'rheos'
                    }
                ]
            }
        ]
    }


@pytest.fixture
def mock_pagerduty_log_response():
    """Mock PagerDuty API log entries response"""
    return {
        'log_entries': [
            {
                'type': 'escalate_log_entry',
                'created_at': '2025-08-23T10:30:00-07:00',
                'agent': {
                    'summary': 'Escalation Policy'
                }
            }
        ]
    }


@pytest.fixture
def mock_flask_app():
    """Mock Flask app for testing"""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    from app_v2 import app
    app.config['TESTING'] = True
    return app.test_client()
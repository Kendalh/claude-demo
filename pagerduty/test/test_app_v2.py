"""
Tests for Flask web application (app_v2.py)
Tests web routes, JSON API endpoints with mocked dependencies
"""
import pytest
import json
import tempfile
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, mock_open, MagicMock

from app_v2 import app, load_service_config, UTC_MINUS_7
from analytics_v2 import ServiceMetrics
from test.fixtures.sample_pagerduty_data import SAMPLE_CONFIG_YAML


class TestFlaskWebApplication:
    """Test suite for Flask web application"""
    
    @pytest.fixture
    def client(self):
        """Create test Flask client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_dashboard_route(self, client):
        """Test main dashboard route"""
        with patch('app_v2.load_service_config') as mock_load:
            mock_load.return_value = {
                'PHMCGNE': {'name': 'Test Service', 'url': 'https://test.com/PHMCGNE'}
            }
            
            response = client.get('/')
            
            assert response.status_code == 200
            assert b'Test Service' in response.data  # Should contain service name
    
    def test_admin_route(self, client):
        """Test admin page route"""
        response = client.get('/admin')
        
        assert response.status_code == 200
        # Should render admin template successfully
    
    def test_api_services_route(self, client):
        """Test API endpoint for getting all services"""
        with patch('app_v2.load_service_config') as mock_load:
            mock_services = {
                'PHMCGNE': {'name': 'Test Service A', 'url': 'https://test.com/PHMCGNE'},
                'PABCDEF': {'name': 'Test Service B', 'url': 'https://test.com/PABCDEF'}
            }
            mock_load.return_value = mock_services
            
            response = client.get('/api/services')
            
            assert response.status_code == 200
            assert response.is_json
            
            data = response.get_json()
            assert data == mock_services
    
    def test_api_service_calendar_valid_service(self, client):
        """Test calendar API with valid service and date parameters"""
        mock_incidents = [
            MagicMock(
                id='TEST123',
                title='Test Incident',
                created_at=datetime(2025, 8, 23, 10, 0, 0, tzinfo=UTC_MINUS_7),
                is_escalated=True,
                urgency='high',
                status='resolved',
                resolved_by_ccoe=True,
                caused_by_infra='rheos'
            )
        ]
        
        # Mock methods on the incident objects
        mock_incidents[0].is_triggered_or_acknowledged.return_value = False
        mock_incidents[0].is_resolved.return_value = True
        mock_incidents[0].is_caused_by_infrastructure.return_value = True
        
        with patch('app_v2.IncidentDatabase') as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_incidents_by_date_range.return_value = mock_incidents
            mock_db_class.return_value = mock_db
            
            response = client.get('/api/service/PHMCGNE/calendar?year=2025&month=8')
            
            assert response.status_code == 200
            assert response.is_json
            
            data = response.get_json()
            assert '2025-08-23' in data
            
            day_data = data['2025-08-23']
            assert day_data['total'] == 1
            assert day_data['resolved'] == 1
            assert day_data['escalated'] == 1
            assert day_data['ccoe_resolved'] == 1
            assert day_data['infrastructure_caused'] == 1
            assert len(day_data['escalated_incidents']) == 1
    
    def test_api_service_calendar_default_parameters(self, client):
        """Test calendar API with default year/month parameters"""
        with patch('app_v2.IncidentDatabase') as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_incidents_by_date_range.return_value = []
            mock_db_class.return_value = mock_db
            
            with patch('app_v2.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime(2025, 8, 23)
                
                response = client.get('/api/service/PHMCGNE/calendar')
                
                assert response.status_code == 200
                
                # Should call with current year/month
                mock_db.get_incidents_by_date_range.assert_called_once()
    
    def test_api_service_calendar_database_error(self, client):
        """Test calendar API handles database errors"""
        with patch('app_v2.IncidentDatabase') as mock_db_class:
            mock_db_class.side_effect = Exception("Database connection failed")
            
            response = client.get('/api/service/PHMCGNE/calendar')
            
            assert response.status_code == 500
            assert response.is_json
            
            data = response.get_json()
            assert 'error' in data
    
    def test_api_service_calendar_incident_timezone_handling(self, client):
        """Test calendar API handles different timezone scenarios"""
        # Test with timezone-aware incident
        utc_incident = MagicMock(
            id='UTC123',
            title='UTC Incident',
            created_at=datetime(2025, 8, 24, 1, 0, 0, tzinfo=timezone.utc),  # UTC midnight = UTC-7 18:00 prev day
            is_escalated=False,
            resolved_by_ccoe=False
        )
        utc_incident.is_triggered_or_acknowledged.return_value = True
        utc_incident.is_resolved.return_value = False
        utc_incident.is_caused_by_infrastructure.return_value = False
        
        # Test with naive incident
        naive_incident = MagicMock(
            id='NAIVE123',
            title='Naive Incident',
            created_at=datetime(2025, 8, 23, 10, 0, 0),  # Naive datetime
            is_escalated=False,
            resolved_by_ccoe=False
        )
        naive_incident.is_triggered_or_acknowledged.return_value = True
        naive_incident.is_resolved.return_value = False
        naive_incident.is_caused_by_infrastructure.return_value = False
        
        with patch('app_v2.IncidentDatabase') as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_incidents_by_date_range.return_value = [utc_incident, naive_incident]
            mock_db_class.return_value = mock_db
            
            response = client.get('/api/service/PHMCGNE/calendar?year=2025&month=8')
            
            assert response.status_code == 200
            data = response.get_json()
            
            # UTC incident should appear on previous day due to timezone conversion
            assert '2025-08-23' in data
            # Naive incident should appear on same day
            assert '2025-08-23' in data
    
    def test_api_service_summary_valid_request(self, client):
        """Test service summary API with valid parameters"""
        mock_service_metrics = ServiceMetrics(
            service_id='PHMCGNE',
            service_name='Test Service',
            total_incidents=100,
            triggered_incidents=20,
            resolved_incidents=80,
            escalated_incidents=15,
            escalation_rate=15.0,
            ccoe_resolved_incidents=10,
            infrastructure_caused_incidents=5
        )
        
        with patch('app_v2.IncidentAnalytics') as mock_analytics_class:
            mock_analytics = MagicMock()
            mock_analytics.get_service_metrics_last_x_days.return_value = [mock_service_metrics]
            mock_analytics_class.return_value = mock_analytics
            
            response = client.get('/api/service/PHMCGNE/summary?days=7')
            
            assert response.status_code == 200
            assert response.is_json
            
            data = response.get_json()
            assert data['service_id'] == 'PHMCGNE'
            assert data['total_incidents'] == 100
            assert data['escalation_rate'] == 15.0
    
    def test_api_service_summary_service_not_found(self, client):
        """Test service summary API when service is not found"""
        with patch('app_v2.IncidentAnalytics') as mock_analytics_class:
            mock_analytics = MagicMock()
            mock_analytics.get_service_metrics_last_x_days.return_value = []  # No services found
            mock_analytics_class.return_value = mock_analytics
            
            response = client.get('/api/service/NONEXISTENT/summary')
            
            assert response.status_code == 404
            assert response.is_json
            
            data = response.get_json()
            assert 'error' in data
    
    def test_api_service_summary_default_days_parameter(self, client):
        """Test service summary API uses default days parameter"""
        mock_service_metrics = ServiceMetrics(
            service_id='PHMCGNE',
            service_name='Test Service',
            total_incidents=50,
            triggered_incidents=10,
            resolved_incidents=40,
            escalated_incidents=5,
            escalation_rate=10.0
        )
        
        with patch('app_v2.IncidentAnalytics') as mock_analytics_class:
            mock_analytics = MagicMock()
            mock_analytics.get_service_metrics_last_x_days.return_value = [mock_service_metrics]
            mock_analytics_class.return_value = mock_analytics
            
            response = client.get('/api/service/PHMCGNE/summary')  # No days parameter
            
            assert response.status_code == 200
            
            # Should default to 7 days
            mock_analytics.get_service_metrics_last_x_days.assert_called_with(7)
    
    def test_api_admin_update_endpoint(self, client):
        """Test admin update API endpoint"""
        with patch('app_v2.subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_popen.return_value = mock_process
            
            response = client.post('/api/admin/update', 
                                 data={'days': '7'},
                                 content_type='application/x-www-form-urlencoded')
            
            assert response.status_code == 200
            assert response.is_json
            
            data = response.get_json()
            assert 'status' in data
            assert data['status'] == 'started'
            assert data['pid'] == 12345
    
    def test_load_service_config_success(self):
        """Test successful service configuration loading"""
        with patch('builtins.open', mock_open(read_data=SAMPLE_CONFIG_YAML)):
            services = load_service_config()
            
            expected = {
                'PHMCGNE': {
                    'name': 'Production Database Service',
                    'url': 'https://company.pagerduty.com/service-directory/PHMCGNE'
                },
                'PABCDEF': {
                    'name': 'Payment Processing Service',
                    'url': 'https://company.pagerduty.com/service-directory/PABCDEF'
                }
            }
            
            assert services == expected
    
    def test_load_service_config_file_not_found(self):
        """Test service config loading handles missing file"""
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            with patch('builtins.print') as mock_print:
                services = load_service_config()
                
                assert services == {}
                mock_print.assert_called()
    
    def test_load_service_config_invalid_yaml(self):
        """Test service config loading handles invalid YAML"""
        invalid_yaml = "invalid: yaml: [content"
        
        with patch('builtins.open', mock_open(read_data=invalid_yaml)):
            with patch('builtins.print') as mock_print:
                services = load_service_config()
                
                assert services == {}
                mock_print.assert_called()
    
    def test_load_service_config_invalid_service_url(self):
        """Test service config loading handles invalid service URLs"""
        invalid_config = """
token: test_token
services:
  - name: Invalid Service
    url: https://invalid.com/bad-url-format
"""
        
        with patch('builtins.open', mock_open(read_data=invalid_config)):
            with patch('builtins.print') as mock_print:
                services = load_service_config()
                
                # Should skip services with invalid URLs
                assert services == {}
    
    def test_utc_minus_7_timezone_constant(self):
        """Test that UTC_MINUS_7 timezone constant is correctly defined"""
        assert UTC_MINUS_7.utcoffset(None) == timedelta(hours=-7)
    
    def test_api_service_trends_endpoint(self, client):
        """Test service trends API endpoint"""
        mock_daily_counts = [
            {'date': '2025-08-23', 'total': 5, 'escalated': 1},
            {'date': '2025-08-22', 'total': 3, 'escalated': 0},
            {'date': '2025-08-21', 'total': 7, 'escalated': 2}
        ]
        
        with patch('app_v2.IncidentAnalytics') as mock_analytics_class:
            mock_analytics = MagicMock()
            mock_analytics.get_daily_incident_counts.return_value = mock_daily_counts
            mock_analytics_class.return_value = mock_analytics
            
            response = client.get('/api/service/PHMCGNE/trends?days=7')
            
            assert response.status_code == 200
            assert response.is_json
            
            data = response.get_json()
            assert isinstance(data, list)
            assert len(data) == 3
            assert data[0]['date'] == '2025-08-23'
            assert data[0]['total'] == 5
            assert data[0]['escalated'] == 1
    
    def test_error_handling_in_routes(self, client):
        """Test that routes handle exceptions gracefully"""
        # Test calendar endpoint with database error
        with patch('app_v2.IncidentDatabase', side_effect=Exception("Database error")):
            response = client.get('/api/service/PHMCGNE/calendar')
            assert response.status_code == 500
            assert 'error' in response.get_json()
        
        # Test summary endpoint with analytics error
        with patch('app_v2.IncidentAnalytics', side_effect=Exception("Analytics error")):
            response = client.get('/api/service/PHMCGNE/summary')
            assert response.status_code == 500
            assert 'error' in response.get_json()
    
    def test_cors_headers_if_present(self, client):
        """Test CORS headers if they are configured"""
        response = client.get('/api/services')
        
        # Basic response should work regardless of CORS setup
        assert response.status_code == 200
    
    def test_json_content_type(self, client):
        """Test that API endpoints return proper JSON content type"""
        with patch('app_v2.load_service_config', return_value={}):
            response = client.get('/api/services')
            
            assert response.status_code == 200
            assert 'application/json' in response.content_type
    
    def test_escalated_incidents_url_construction(self, client):
        """Test that escalated incidents get proper PagerDuty URLs"""
        mock_incident = MagicMock(
            id='ESCAL123',
            title='Escalated Test',
            created_at=datetime(2025, 8, 23, 10, 0, 0, tzinfo=UTC_MINUS_7),
            is_escalated=True,
            urgency='high',
            status='resolved',
            resolved_by_ccoe=False
        )
        mock_incident.is_triggered_or_acknowledged.return_value = False
        mock_incident.is_resolved.return_value = True
        mock_incident.is_caused_by_infrastructure.return_value = False
        
        with patch('app_v2.IncidentDatabase') as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_incidents_by_date_range.return_value = [mock_incident]
            mock_db_class.return_value = mock_db
            
            response = client.get('/api/service/PHMCGNE/calendar')
            
            data = response.get_json()
            escalated_incidents = data['2025-08-23']['escalated_incidents']
            
            assert len(escalated_incidents) == 1
            assert escalated_incidents[0]['html_url'] == 'https://ebay-cpt.pagerduty.com/incidents/ESCAL123'
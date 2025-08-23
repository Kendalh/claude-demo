"""
Tests for PagerDuty API Client (pagerduty_client_v2.py)
Tests API client with mocked HTTP requests and YAML configuration
"""
import pytest
import responses
import yaml
import tempfile
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, mock_open, MagicMock

from pagerduty_client_v2 import PagerDutyAPIClient
from test.fixtures.sample_pagerduty_data import (
    SAMPLE_PAGERDUTY_INCIDENTS_RESPONSE,
    SAMPLE_PAGERDUTY_LOG_ENTRIES_RESPONSE,
    SAMPLE_CONFIG_YAML,
    SAMPLE_ESCALATED_INCIDENT,
    SAMPLE_NON_ESCALATED_INCIDENT
)


class TestPagerDutyAPIClient:
    """Test suite for PagerDutyAPIClient"""
    
    def test_client_initialization(self):
        """Test basic client initialization"""
        client = PagerDutyAPIClient("test_token_123")
        
        assert client.api_token == "test_token_123"
        assert client.base_url == "https://api.pagerduty.com"
        assert "Token token=test_token_123" in client.headers["Authorization"]
        assert "application/vnd.pagerduty+json;version=2" in client.headers["Accept"]
        assert client.utc_minus_7.utcoffset(None) == timedelta(hours=-7)
    
    def test_extract_service_id_valid_urls(self):
        """Test service ID extraction from valid PagerDuty URLs"""
        client = PagerDutyAPIClient("test_token")
        
        test_cases = [
            ("https://company.pagerduty.com/service-directory/PHMCGNE", "PHMCGNE"),
            ("https://company.pagerduty.com/service-directory/PABCDEF", "PABCDEF"),
            ("https://another.pagerduty.com/service-directory/P123456", "P123456"),
        ]
        
        for url, expected_id in test_cases:
            result = client._extract_service_id(url)
            assert result == expected_id
    
    def test_extract_service_id_invalid_urls(self):
        """Test service ID extraction fails gracefully with invalid URLs"""
        client = PagerDutyAPIClient("test_token")
        
        invalid_urls = [
            "https://company.pagerduty.com/invalid-path",
            "https://company.pagerduty.com/service-directory/",
            "https://company.pagerduty.com/service-directory/TOOSHORT",
            "invalid-url"
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError, match="Could not extract service ID"):
                client._extract_service_id(url)
    
    def test_load_services_from_config(self, mock_pagerduty_config):
        """Test loading service configuration from YAML file"""
        client = PagerDutyAPIClient("test_token")
        
        with patch('builtins.open', mock_open(read_data=SAMPLE_CONFIG_YAML)):
            service_ids, service_id_to_name = client.load_services_from_config()
        
        assert service_ids == ['PHMCGNE', 'PABCDEF']
        assert service_id_to_name == {
            'PHMCGNE': 'Production Database Service',
            'PABCDEF': 'Payment Processing Service'
        }
    
    def test_load_services_from_config_file_not_found(self):
        """Test handling of missing config file"""
        client = PagerDutyAPIClient("test_token")
        
        with patch('builtins.open', side_effect=FileNotFoundError("Config file not found")):
            with pytest.raises(FileNotFoundError):
                client.load_services_from_config("nonexistent.yaml")
    
    def test_load_services_from_config_invalid_yaml(self):
        """Test handling of invalid YAML configuration"""
        client = PagerDutyAPIClient("test_token")
        
        invalid_yaml = "invalid: yaml: content: ["
        
        with patch('builtins.open', mock_open(read_data=invalid_yaml)):
            with pytest.raises(yaml.YAMLError):
                client.load_services_from_config()
    
    @responses.activate
    def test_fetch_incidents_from_api_basic(self):
        """Test basic incident fetching from API"""
        client = PagerDutyAPIClient("test_token")
        
        # Mock PagerDuty API response
        responses.add(
            responses.GET,
            "https://api.pagerduty.com/incidents",
            json=SAMPLE_PAGERDUTY_INCIDENTS_RESPONSE,
            status=200
        )
        
        # Mock service config
        with patch.object(client, 'load_services_from_config') as mock_load:
            mock_load.return_value = (['PHMCGNE'], {'PHMCGNE': 'Test Service'})
            
            # Mock escalation checking methods
            with patch.object(client, '_check_incident_escalation', return_value=False):
                with patch.object(client, '_get_incident_custom_fields', return_value={}):
                    with patch('builtins.print'):  # Suppress output
                        incidents = client.fetch_incidents_for_date_range(days=1)
        
        assert len(incidents) == 2
        assert incidents[0].id == "Q1ABC123DEF"
        assert incidents[1].id == "Q2DEF456GHI"
    
    @responses.activate
    def test_check_incident_escalation_true(self):
        """Test escalation detection when incident was escalated"""
        client = PagerDutyAPIClient("test_token")
        
        # Mock log entries response with escalation
        responses.add(
            responses.GET,
            "https://api.pagerduty.com/incidents/TEST123/log_entries",
            json=SAMPLE_PAGERDUTY_LOG_ENTRIES_RESPONSE,
            status=200
        )
        
        is_escalated = client._check_incident_escalation("TEST123")
        
        assert is_escalated is True
    
    @responses.activate  
    def test_check_incident_escalation_false(self):
        """Test escalation detection when incident was not escalated"""
        client = PagerDutyAPIClient("test_token")
        
        # Mock log entries response without escalation
        log_response = {
            "log_entries": [
                {
                    "type": "acknowledge_log_entry",
                    "created_at": "2025-08-23T10:15:00-07:00"
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://api.pagerduty.com/incidents/TEST123/log_entries",
            json=log_response,
            status=200
        )
        
        is_escalated = client._check_incident_escalation("TEST123")
        
        assert is_escalated is False
    
    @responses.activate
    def test_check_incident_escalation_api_error(self):
        """Test escalation check handles API errors gracefully"""
        client = PagerDutyAPIClient("test_token")
        
        # Mock API error response
        responses.add(
            responses.GET,
            "https://api.pagerduty.com/incidents/TEST123/log_entries",
            json={"error": "Not found"},
            status=404
        )
        
        with patch('builtins.print'):  # Suppress error output
            is_escalated = client._check_incident_escalation("TEST123")
        
        # Should default to False on error
        assert is_escalated is False
    
    @responses.activate
    def test_get_incident_custom_fields_success(self):
        """Test fetching custom fields from incident"""
        client = PagerDutyAPIClient("test_token")
        
        # Mock incident response with custom fields
        incident_response = {
            "incident": {
                "id": "TEST123",
                "custom_fields": [
                    {
                        "field": {"name": "resolution"},
                        "value": "ccoe"
                    },
                    {
                        "field": {"name": "prelim_root_cause"},
                        "value": "rheos"
                    }
                ]
            }
        }
        
        responses.add(
            responses.GET,
            "https://api.pagerduty.com/incidents/TEST123",
            json=incident_response,
            status=200
        )
        
        custom_fields = client._get_incident_custom_fields("TEST123")
        
        assert custom_fields == {
            "resolution": "ccoe",
            "prelim_root_cause": "rheos"
        }
    
    @responses.activate
    def test_get_incident_custom_fields_api_error(self):
        """Test custom fields fetching handles API errors gracefully"""
        client = PagerDutyAPIClient("test_token")
        
        # Mock API error response
        responses.add(
            responses.GET,
            "https://api.pagerduty.com/incidents/TEST123",
            json={"error": "Not found"},
            status=404
        )
        
        with patch('builtins.print'):  # Suppress error output
            custom_fields = client._get_incident_custom_fields("TEST123")
        
        # Should return empty dict on error
        assert custom_fields == {}
    
    def test_convert_to_incident_object_with_custom_fields(self):
        """Test conversion of PagerDuty API response to Incident object with custom fields"""
        client = PagerDutyAPIClient("test_token")
        
        raw_incident = SAMPLE_PAGERDUTY_INCIDENTS_RESPONSE["incidents"][0]
        custom_fields = {"resolution": "ccoe", "prelim_root_cause": "rheos"}
        service_id_to_name = {"PHMCGNE": "Production Database Service"}
        
        incident = client._convert_to_incident_object(
            raw_incident, True, service_id_to_name, custom_fields
        )
        
        assert incident.id == "Q1ABC123DEF"
        assert incident.title == "Database Connection Timeout"
        assert incident.status == "resolved"
        assert incident.service_id == "PHMCGNE"
        assert incident.service_name == "Production Database Service"
        assert incident.is_escalated is True
        assert incident.urgency == "high"
        assert incident.priority == "P1"
        assert incident.resolved_by_ccoe is True  # from custom field "resolution": "ccoe"
        assert incident.caused_by_infra == "rheos"  # from custom field "prelim_root_cause"
    
    def test_convert_to_incident_object_without_custom_fields(self):
        """Test conversion without custom fields uses defaults"""
        client = PagerDutyAPIClient("test_token")
        
        raw_incident = SAMPLE_PAGERDUTY_INCIDENTS_RESPONSE["incidents"][1]
        custom_fields = {}
        service_id_to_name = {"PHMCGNE": "Production Database Service"}
        
        incident = client._convert_to_incident_object(
            raw_incident, False, service_id_to_name, custom_fields
        )
        
        assert incident.resolved_by_ccoe is False  # default when no custom field
        assert incident.caused_by_infra is None  # default when no custom field
    
    def test_convert_to_incident_object_timezone_conversion(self):
        """Test that datetime conversion handles timezones correctly"""
        client = PagerDutyAPIClient("test_token")
        
        raw_incident = {
            "id": "TZ_TEST",
            "title": "Timezone Test",
            "status": "resolved",
            "service": {"id": "SERVICE1", "summary": "Test Service"},
            "created_at": "2025-08-23T10:00:00-07:00",  # UTC-7
            "updated_at": "2025-08-23T11:00:00-07:00",   # UTC-7
            "escalation_policy": {"id": "POLICY1", "summary": "Policy"},
            "urgency": "high",
            "priority": {"summary": "P1"},
            "description": "Test"
        }
        
        incident = client._convert_to_incident_object(
            raw_incident, False, {"SERVICE1": "Test Service"}, {}
        )
        
        # Should preserve timezone information
        assert incident.created_at.tzinfo is not None
        assert incident.created_at.tzinfo.utcoffset(None) == timedelta(hours=-7)
    
    def test_date_range_calculation_with_specific_dates(self):
        """Test date range calculation with specific start and end dates"""
        client = PagerDutyAPIClient("test_token")
        
        with patch.object(client, 'load_services_from_config') as mock_load:
            mock_load.return_value = (['PHMCGNE'], {'PHMCGNE': 'Test Service'})
            
            with patch.object(client, '_fetch_incidents_from_api', return_value=[]):
                with patch('builtins.print'):  # Suppress output
                    # This should not raise an error and should calculate date range correctly
                    incidents = client.fetch_incidents_for_date_range(
                        start_date="2025-08-20",
                        end_date="2025-08-23"
                    )
        
        assert incidents == []
    
    def test_date_range_calculation_with_days_parameter(self):
        """Test date range calculation using days parameter"""
        client = PagerDutyAPIClient("test_token")
        
        with patch.object(client, 'load_services_from_config') as mock_load:
            mock_load.return_value = (['PHMCGNE'], {'PHMCGNE': 'Test Service'})
            
            with patch.object(client, '_fetch_incidents_from_api', return_value=[]):
                with patch('builtins.print'):  # Suppress output
                    incidents = client.fetch_incidents_for_date_range(days=7)
        
        assert incidents == []
    
    def test_service_id_validation(self):
        """Test validation of provided service IDs against configuration"""
        client = PagerDutyAPIClient("test_token")
        
        with patch.object(client, 'load_services_from_config') as mock_load:
            mock_load.return_value = (['PHMCGNE', 'PABCDEF'], {'PHMCGNE': 'Service A', 'PABCDEF': 'Service B'})
            
            # Valid service IDs should work
            with patch.object(client, '_fetch_incidents_from_api', return_value=[]):
                with patch('builtins.print'):
                    incidents = client.fetch_incidents_for_date_range(
                        service_ids=['PHMCGNE'], days=1
                    )
                    assert incidents == []
            
            # Invalid service IDs should raise error
            with pytest.raises(ValueError, match="Invalid service IDs"):
                client.fetch_incidents_for_date_range(
                    service_ids=['INVALID'], days=1
                )
    
    @responses.activate
    def test_api_timeout_handling(self):
        """Test handling of API timeouts"""
        client = PagerDutyAPIClient("test_token")
        
        # Mock timeout response
        def timeout_callback(request):
            raise requests.exceptions.Timeout("Request timed out")
        
        responses.add_callback(
            responses.GET,
            "https://api.pagerduty.com/incidents/TEST123/log_entries",
            callback=timeout_callback
        )
        
        with patch('builtins.print'):  # Suppress error output
            is_escalated = client._check_incident_escalation("TEST123")
        
        # Should handle timeout gracefully and return False
        assert is_escalated is False
    
    @responses.activate
    def test_api_rate_limiting(self):
        """Test handling of API rate limiting"""
        client = PagerDutyAPIClient("test_token")
        
        # Mock rate limit response
        responses.add(
            responses.GET,
            "https://api.pagerduty.com/incidents/TEST123/log_entries",
            json={"error": {"code": 2006, "message": "Rate limited"}},
            status=429
        )
        
        with patch('builtins.print'):  # Suppress error output
            is_escalated = client._check_incident_escalation("TEST123")
        
        # Should handle rate limiting gracefully
        assert is_escalated is False
    
    def test_batch_processing_logic(self):
        """Test that batch processing works correctly"""
        client = PagerDutyAPIClient("test_token")
        
        # Create a large list of mock incidents to test batching
        large_incident_list = []
        for i in range(25):  # More than batch size of 20
            large_incident_list.append({
                "id": f"BATCH_{i:02d}",
                "title": f"Batch incident {i}",
                "status": "resolved",
                "service": {"id": "SERVICE1", "summary": "Test Service"},
                "created_at": "2025-08-23T10:00:00-07:00",
                "updated_at": "2025-08-23T11:00:00-07:00",
                "escalation_policy": {"id": "POLICY1", "summary": "Policy"},
                "urgency": "low",
                "priority": {"summary": "P3"},
                "description": "Batch test"
            })
        
        with patch.object(client, 'load_services_from_config') as mock_load:
            mock_load.return_value = (['SERVICE1'], {'SERVICE1': 'Test Service'})
            
            with patch.object(client, '_fetch_incidents_from_api', return_value=large_incident_list):
                with patch.object(client, '_check_incident_escalation', return_value=False):
                    with patch.object(client, '_get_incident_custom_fields', return_value={}):
                        with patch('builtins.print'):  # Suppress output
                            with patch('time.sleep'):  # Skip sleep delays
                                incidents = client.fetch_incidents_for_date_range(days=1)
        
        # Should process all incidents despite batching
        assert len(incidents) == 25
        assert incidents[0].id == "BATCH_00"
        assert incidents[24].id == "BATCH_24"
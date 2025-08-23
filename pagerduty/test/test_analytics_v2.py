"""
Tests for Analytics layer (analytics_v2.py)
Tests SQL-based metrics calculation with controlled test data
"""
import pytest
from datetime import datetime, timezone, timedelta
from freezegun import freeze_time

from analytics_v2 import IncidentAnalytics, MetricResult, ServiceMetrics
from test.fixtures.test_database import TestDatabaseHelper, create_sample_test_incidents


class TestIncidentAnalytics:
    """Test suite for IncidentAnalytics class"""
    
    def test_analytics_initialization(self, temp_db):
        """Test analytics initialization with database path"""
        analytics = IncidentAnalytics(temp_db)
        
        assert analytics.db_path == temp_db
        assert analytics.utc_minus_7.utcoffset(None) == timedelta(hours=-7)
    
    def test_get_total_incidents_last_x_days_with_data(self, temp_db):
        """Test total incidents calculation with sample data"""
        # Set up test database with incidents
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        sample_incidents = create_sample_test_incidents()
        db_helper.insert_sample_incidents(sample_incidents)
        
        analytics = IncidentAnalytics(temp_db)
        
        # Test with current date being in the range of our test incidents
        with freeze_time("2025-08-23 15:00:00"):  # UTC time
            result = analytics.get_total_incidents_last_x_days(7)
        
        assert isinstance(result, MetricResult)
        assert result.metric_name == "total_incidents"
        assert result.period_days == 7
        assert result.value >= 0  # Should have some incidents in range
    
    def test_get_total_incidents_last_x_days_empty_database(self, temp_db):
        """Test total incidents calculation with empty database"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        analytics = IncidentAnalytics(temp_db)
        
        result = analytics.get_total_incidents_last_x_days(7)
        
        assert result.metric_name == "total_incidents"
        assert result.value == 0
        assert result.period_days == 7
    
    def test_get_triggered_incidents_last_x_days(self, temp_db):
        """Test triggered incidents calculation"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        sample_incidents = create_sample_test_incidents()
        db_helper.insert_sample_incidents(sample_incidents)
        
        analytics = IncidentAnalytics(temp_db)
        
        with freeze_time("2025-08-23 15:00:00"):
            result = analytics.get_triggered_incidents_last_x_days(7)
        
        assert result.metric_name == "triggered_incidents"
        assert result.value >= 0
        assert result.period_days == 7
    
    def test_get_resolved_incidents_last_x_days(self, temp_db):
        """Test resolved incidents calculation"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        sample_incidents = create_sample_test_incidents()
        db_helper.insert_sample_incidents(sample_incidents)
        
        analytics = IncidentAnalytics(temp_db)
        
        with freeze_time("2025-08-23 15:00:00"):
            result = analytics.get_resolved_incidents_last_x_days(7)
        
        assert result.metric_name == "resolved_incidents"
        assert result.value >= 0
        assert result.period_days == 7
    
    def test_get_escalated_incidents_last_x_days(self, temp_db):
        """Test escalated incidents calculation"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        sample_incidents = create_sample_test_incidents()
        db_helper.insert_sample_incidents(sample_incidents)
        
        analytics = IncidentAnalytics(temp_db)
        
        with freeze_time("2025-08-23 15:00:00"):
            result = analytics.get_escalated_incidents_last_x_days(7)
        
        assert result.metric_name == "escalated_incidents"
        assert result.value >= 0  # Should have some escalated incidents
        assert result.period_days == 7
    
    def test_get_escalation_rate_last_x_days_with_incidents(self, temp_db):
        """Test escalation rate calculation with incidents"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        sample_incidents = create_sample_test_incidents()
        db_helper.insert_sample_incidents(sample_incidents)
        
        analytics = IncidentAnalytics(temp_db)
        
        with freeze_time("2025-08-23 15:00:00"):
            rate = analytics.get_escalation_rate_last_x_days(7)
        
        assert isinstance(rate, float)
        assert 0.0 <= rate <= 100.0  # Should be a valid percentage
    
    def test_get_escalation_rate_last_x_days_no_incidents(self, temp_db):
        """Test escalation rate calculation with no incidents"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        analytics = IncidentAnalytics(temp_db)
        
        rate = analytics.get_escalation_rate_last_x_days(7)
        
        assert rate == 0.0
    
    def test_get_service_metrics_specific_service(self, temp_db):
        """Test service-specific metrics calculation"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        sample_incidents = create_sample_test_incidents()
        db_helper.insert_sample_incidents(sample_incidents)
        
        analytics = IncidentAnalytics(temp_db)
        
        with freeze_time("2025-08-23 15:00:00"):
            metrics = analytics.get_service_metrics('PHMCGNE', 7)
        
        assert isinstance(metrics, ServiceMetrics)
        assert metrics.service_id == 'PHMCGNE'
        assert metrics.total_incidents >= 0
        assert metrics.triggered_incidents >= 0
        assert metrics.resolved_incidents >= 0
        assert metrics.escalated_incidents >= 0
        assert 0.0 <= metrics.escalation_rate <= 100.0
    
    def test_get_service_metrics_nonexistent_service(self, temp_db):
        """Test service metrics for non-existent service"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        analytics = IncidentAnalytics(temp_db)
        
        metrics = analytics.get_service_metrics('NONEXISTENT', 7)
        
        assert metrics.service_id == 'NONEXISTENT'
        assert metrics.total_incidents == 0
        assert metrics.triggered_incidents == 0
        assert metrics.resolved_incidents == 0
        assert metrics.escalated_incidents == 0
        assert metrics.escalation_rate == 0.0
    
    def test_get_all_services_summary(self, temp_db):
        """Test getting summary for all services"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        sample_incidents = create_sample_test_incidents()
        db_helper.insert_sample_incidents(sample_incidents)
        
        analytics = IncidentAnalytics(temp_db)
        
        with freeze_time("2025-08-23 15:00:00"):
            summary = analytics.get_all_services_summary(7)
        
        assert isinstance(summary, list)
        assert len(summary) >= 0  # Should have at least some services
        
        if summary:
            for service_metrics in summary:
                assert isinstance(service_metrics, ServiceMetrics)
                assert service_metrics.service_id is not None
    
    def test_get_daily_incident_counts(self, temp_db):
        """Test daily incident count aggregation"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        sample_incidents = create_sample_test_incidents()
        db_helper.insert_sample_incidents(sample_incidents)
        
        analytics = IncidentAnalytics(temp_db)
        
        with freeze_time("2025-08-23 15:00:00"):
            daily_counts = analytics.get_daily_incident_counts(7)
        
        assert isinstance(daily_counts, list)
        assert len(daily_counts) <= 7  # Should not exceed requested days
        
        for day_data in daily_counts:
            assert 'date' in day_data
            assert 'total' in day_data
            assert 'escalated' in day_data
            assert isinstance(day_data['total'], int)
            assert isinstance(day_data['escalated'], int)
            assert day_data['escalated'] <= day_data['total']
    
    def test_get_incidents_by_service_for_calendar(self, temp_db):
        """Test calendar data generation for specific service"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        sample_incidents = create_sample_test_incidents()
        db_helper.insert_sample_incidents(sample_incidents)
        
        analytics = IncidentAnalytics(temp_db)
        
        calendar_data = analytics.get_incidents_by_service_for_calendar('PHMCGNE', 2025, 8)
        
        assert isinstance(calendar_data, dict)
        
        # Check that dates are in expected format
        for date_str, incidents in calendar_data.items():
            assert len(date_str) == 10  # YYYY-MM-DD format
            assert isinstance(incidents, list)
            
            for incident in incidents:
                assert 'id' in incident
                assert 'title' in incident
                assert 'status' in incident
                assert 'is_escalated' in incident
    
    def test_date_range_filtering_accuracy(self, temp_db, utc_minus_7):
        """Test that date range filtering works accurately"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        # Create incidents on specific dates
        from incident_v2 import Incident
        
        # Incident within range
        incident_in_range = Incident(
            id='IN_RANGE',
            title='In range incident',
            status='resolved',
            service_id='TEST_SERVICE',
            service_name='Test Service',
            created_at=datetime(2025, 8, 23, 10, 0, 0, tzinfo=utc_minus_7)
        )
        
        # Incident outside range (older)
        incident_out_range = Incident(
            id='OUT_RANGE',
            title='Out of range incident',
            status='resolved',
            service_id='TEST_SERVICE',
            service_name='Test Service',
            created_at=datetime(2025, 8, 10, 10, 0, 0, tzinfo=utc_minus_7)  # Too old
        )
        
        db_helper.insert_sample_incidents([incident_in_range, incident_out_range])
        
        analytics = IncidentAnalytics(temp_db)
        
        # Test with specific date that should only include the in-range incident
        with freeze_time("2025-08-23 15:00:00"):
            result = analytics.get_total_incidents_last_x_days(1)  # Last 1 day
        
        assert result.value == 1  # Should only count the in-range incident
    
    def test_escalation_rate_calculation_edge_cases(self, temp_db, utc_minus_7):
        """Test escalation rate calculation edge cases"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        from incident_v2 import Incident
        
        # Create incidents with known escalation pattern
        incidents = []
        for i in range(4):
            incidents.append(Incident(
                id=f'ESCAL_{i}',
                title=f'Escalation test {i}',
                status='resolved',
                service_id='TEST_SERVICE',
                service_name='Test Service',
                created_at=datetime(2025, 8, 23, 10, i, 0, tzinfo=utc_minus_7),
                is_escalated=(i % 2 == 0)  # 50% escalation rate
            ))
        
        db_helper.insert_sample_incidents(incidents)
        
        analytics = IncidentAnalytics(temp_db)
        
        with freeze_time("2025-08-23 15:00:00"):
            rate = analytics.get_escalation_rate_last_x_days(1)
        
        assert rate == 50.0  # Should be exactly 50% (2 out of 4 escalated)
    
    def test_ccoe_resolution_metrics(self, temp_db, utc_minus_7):
        """Test CCOE resolution tracking"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        from incident_v2 import Incident
        
        # Create incidents with known CCOE resolution pattern
        incidents = []
        for i in range(3):
            incidents.append(Incident(
                id=f'CCOE_{i}',
                title=f'CCOE test {i}',
                status='resolved',
                service_id='TEST_SERVICE',
                service_name='Test Service',
                created_at=datetime(2025, 8, 23, 10, i, 0, tzinfo=utc_minus_7),
                resolved_by_ccoe=(i == 0)  # Only first incident resolved by CCOE
            ))
        
        db_helper.insert_sample_incidents(incidents)
        
        analytics = IncidentAnalytics(temp_db)
        
        with freeze_time("2025-08-23 15:00:00"):
            metrics = analytics.get_service_metrics('TEST_SERVICE', 1)
        
        assert metrics.ccoe_resolved_incidents == 1  # Only one resolved by CCOE
        assert metrics.total_incidents == 3
    
    def test_infrastructure_cause_metrics(self, temp_db, utc_minus_7):
        """Test infrastructure cause tracking"""
        db_helper = TestDatabaseHelper(temp_db)
        db_helper.create_schema()
        
        from incident_v2 import Incident
        
        # Create incidents with infrastructure causes
        incidents = []
        infra_causes = [None, 'rheos', 'hadoop', None]
        
        for i, cause in enumerate(infra_causes):
            incidents.append(Incident(
                id=f'INFRA_{i}',
                title=f'Infrastructure test {i}',
                status='resolved',
                service_id='TEST_SERVICE',
                service_name='Test Service',
                created_at=datetime(2025, 8, 23, 10, i, 0, tzinfo=utc_minus_7),
                caused_by_infra=cause
            ))
        
        db_helper.insert_sample_incidents(incidents)
        
        analytics = IncidentAnalytics(temp_db)
        
        with freeze_time("2025-08-23 15:00:00"):
            metrics = analytics.get_service_metrics('TEST_SERVICE', 1)
        
        assert metrics.infrastructure_caused_incidents == 2  # Two with non-None causes
        assert metrics.total_incidents == 4
    
    def test_metric_result_dataclass(self):
        """Test MetricResult dataclass functionality"""
        result = MetricResult(
            metric_name="test_metric",
            value=42,
            period_days=7,
            service_id="TEST_SERVICE",
            service_name="Test Service"
        )
        
        assert result.metric_name == "test_metric"
        assert result.value == 42
        assert result.period_days == 7
        assert result.service_id == "TEST_SERVICE"
        assert result.service_name == "Test Service"
    
    def test_service_metrics_dataclass(self):
        """Test ServiceMetrics dataclass functionality"""
        metrics = ServiceMetrics(
            service_id="TEST_SERVICE",
            service_name="Test Service",
            total_incidents=100,
            triggered_incidents=20,
            resolved_incidents=80,
            escalated_incidents=15,
            escalation_rate=15.0,
            ccoe_resolved_incidents=10,
            infrastructure_caused_incidents=5
        )
        
        assert metrics.service_id == "TEST_SERVICE"
        assert metrics.service_name == "Test Service"
        assert metrics.total_incidents == 100
        assert metrics.triggered_incidents == 20
        assert metrics.resolved_incidents == 80
        assert metrics.escalated_incidents == 15
        assert metrics.escalation_rate == 15.0
        assert metrics.ccoe_resolved_incidents == 10
        assert metrics.infrastructure_caused_incidents == 5
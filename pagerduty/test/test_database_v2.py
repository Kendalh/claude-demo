"""
Tests for Database layer (database_v2.py)
Tests database operations with SQLite, using temporary databases for isolation
"""
import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, mock_open

from database_v2 import IncidentDatabase
from incident_v2 import Incident


class TestIncidentDatabase:
    """Test suite for the IncidentDatabase class"""
    
    def test_database_initialization(self, temp_db):
        """Test database initialization creates proper schema"""
        db = IncidentDatabase(temp_db)
        
        # Check that database file exists
        assert os.path.exists(temp_db)
        
        # Check that incidents table exists with correct schema
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            
            # Get table schema
            cursor.execute("PRAGMA table_info(incidents)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            # Verify all required columns exist
            expected_columns = {
                'id': 'TEXT',
                'title': 'TEXT',
                'status': 'TEXT',
                'service_id': 'TEXT',
                'service_name': 'TEXT',
                'created_at': 'TIMESTAMP',
                'resolved_at': 'TIMESTAMP',
                'acknowledged_at': 'TIMESTAMP',
                'is_escalated': 'BOOLEAN',
                'escalation_policy_id': 'TEXT',
                'escalation_policy_name': 'TEXT',
                'urgency': 'TEXT',
                'priority': 'TEXT',
                'description': 'TEXT',
                'resolved_by_ccoe': 'BOOLEAN',
                'caused_by_infra': 'TEXT',
                'updated_at': 'TIMESTAMP'
            }
            
            for col_name, col_type in expected_columns.items():
                assert col_name in columns, f"Column {col_name} missing"
                assert col_type in columns[col_name], f"Column {col_name} has wrong type"
    
    def test_database_indexes_created(self, temp_db):
        """Test that performance indexes are created"""
        db = IncidentDatabase(temp_db)
        
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            
            # Get list of indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]
            
            expected_indexes = [
                'idx_incidents_service_created',
                'idx_incidents_status',
                'idx_incidents_escalated',
                'idx_incidents_created_date'
            ]
            
            for index_name in expected_indexes:
                assert index_name in indexes, f"Index {index_name} not created"
    
    def test_store_single_incident(self, test_db, sample_incident):
        """Test storing a single incident"""
        test_db.store_incident(sample_incident)
        
        # Verify incident was stored
        with sqlite3.connect(test_db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM incidents WHERE id = ?", (sample_incident.id,))
            row = cursor.fetchone()
            
            assert row is not None
            assert row[0] == sample_incident.id  # id column
            assert row[1] == sample_incident.title  # title column
            assert row[2] == sample_incident.status  # status column
    
    def test_store_incident_with_timezone_conversion(self, test_db, utc_minus_7):
        """Test that timezone conversion works during storage"""
        # Create incident with UTC timezone
        utc_time = datetime(2025, 8, 23, 17, 0, 0, tzinfo=timezone.utc)
        incident = Incident(
            id='TZ_TEST',
            title='Timezone test',
            status='triggered',
            service_id='SERVICE1',
            service_name='Test Service',
            created_at=utc_time
        )
        
        test_db.store_incident(incident)
        
        # Verify stored time includes timezone info
        with sqlite3.connect(test_db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT created_at FROM incidents WHERE id = ?", (incident.id,))
            stored_time_str = cursor.fetchone()[0]
            
            # Should be stored as ISO string with timezone
            assert 'T' in stored_time_str
            assert stored_time_str.endswith(':00')
    
    def test_store_incident_upsert_behavior(self, test_db, sample_incident):
        """Test that storing the same incident twice updates rather than duplicates"""
        # Store incident first time
        test_db.store_incident(sample_incident)
        
        # Modify incident and store again
        sample_incident.status = 'resolved'
        sample_incident.urgency = 'low'
        test_db.store_incident(sample_incident)
        
        # Verify only one record exists with updated data
        with sqlite3.connect(test_db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), status, urgency FROM incidents WHERE id = ?", 
                         (sample_incident.id,))
            count, status, urgency = cursor.fetchone()
            
            assert count == 1
            assert status == 'resolved'
            assert urgency == 'low'
    
    def test_store_incidents_batch(self, test_db, sample_incidents):
        """Test batch storage of multiple incidents"""
        stored_count = test_db.store_incidents_batch(sample_incidents)
        
        assert stored_count == len(sample_incidents)
        
        # Verify all incidents were stored
        with sqlite3.connect(test_db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM incidents")
            count = cursor.fetchone()[0]
            
            assert count == len(sample_incidents)
    
    def test_store_incidents_batch_empty_list(self, test_db):
        """Test batch storage with empty list"""
        stored_count = test_db.store_incidents_batch([])
        
        assert stored_count == 0
        
        # Verify no incidents were stored
        with sqlite3.connect(test_db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM incidents")
            count = cursor.fetchone()[0]
            
            assert count == 0
    
    def test_store_incidents_batch_with_errors(self, test_db, sample_incidents):
        """Test batch storage handles individual errors gracefully"""
        # Corrupt one incident's data to cause an error
        sample_incidents[1].id = None  # This should cause an error
        
        with patch('builtins.print'):  # Suppress error print statements
            stored_count = test_db.store_incidents_batch(sample_incidents)
        
        # Should store all incidents except the corrupted one
        assert stored_count == len(sample_incidents) - 1
    
    def test_get_incidents_by_date_range(self, test_db, sample_incidents):
        """Test retrieving incidents by date range"""
        # Store sample incidents
        test_db.store_incidents_batch(sample_incidents)
        
        # Get incidents for a specific date
        incidents = test_db.get_incidents_by_date_range('2025-08-23', '2025-08-23')
        
        # Should return incidents created on that date
        assert len(incidents) > 0
        for incident in incidents:
            assert incident.get_date_str_utc_minus_7() == '2025-08-23'
    
    def test_get_incidents_by_date_range_with_service_filter(self, test_db, sample_incidents):
        """Test retrieving incidents filtered by service"""
        # Store sample incidents
        test_db.store_incidents_batch(sample_incidents)
        
        # Get incidents for specific service
        incidents = test_db.get_incidents_by_date_range(
            '2025-08-20', '2025-08-25', 
            service_id='PHMCGNE'
        )
        
        # All returned incidents should be from specified service
        for incident in incidents:
            assert incident.service_id == 'PHMCGNE'
    
    def test_get_incidents_by_date_range_ordering(self, test_db, utc_minus_7):
        """Test that incidents are returned in descending order by created_at"""
        # Create incidents with different creation times
        incidents = []
        base_time = datetime(2025, 8, 23, 10, 0, 0, tzinfo=utc_minus_7)
        for i in range(3):
            incidents.append(Incident(
                id=f'ORDER_{i}',
                title=f'Incident {i}',
                status='triggered',
                service_id='SERVICE1',
                service_name='Test Service',
                created_at=base_time + timedelta(hours=i)
            ))
        
        test_db.store_incidents_batch(incidents)
        
        # Retrieve incidents
        retrieved = test_db.get_incidents_by_date_range('2025-08-23', '2025-08-23')
        
        # Should be ordered by creation time (newest first)
        assert len(retrieved) == 3
        assert retrieved[0].id == 'ORDER_2'  # Latest created
        assert retrieved[1].id == 'ORDER_1'
        assert retrieved[2].id == 'ORDER_0'  # Earliest created
    
    def test_get_incidents_by_date_range_empty_result(self, test_db):
        """Test date range query with no matching incidents"""
        incidents = test_db.get_incidents_by_date_range('2020-01-01', '2020-01-01')
        
        assert incidents == []
    
    def test_incident_roundtrip_serialization(self, test_db, sample_incident):
        """Test that incidents can be stored and retrieved without data loss"""
        # Store incident
        test_db.store_incident(sample_incident)
        
        # Retrieve incident
        incidents = test_db.get_incidents_by_date_range(
            '2025-08-23', '2025-08-23', 
            service_id=sample_incident.service_id
        )
        
        assert len(incidents) == 1
        retrieved = incidents[0]
        
        # Verify all fields match
        assert retrieved.id == sample_incident.id
        assert retrieved.title == sample_incident.title
        assert retrieved.status == sample_incident.status
        assert retrieved.service_id == sample_incident.service_id
        assert retrieved.service_name == sample_incident.service_name
        assert retrieved.is_escalated == sample_incident.is_escalated
        assert retrieved.urgency == sample_incident.urgency
        assert retrieved.priority == sample_incident.priority
        assert retrieved.description == sample_incident.description
        assert retrieved.resolved_by_ccoe == sample_incident.resolved_by_ccoe
        assert retrieved.caused_by_infra == sample_incident.caused_by_infra
        
        # Datetime fields should match (timezone-aware comparison)
        assert retrieved.created_at == sample_incident.created_at
        assert retrieved.resolved_at == sample_incident.resolved_at
        assert retrieved.acknowledged_at == sample_incident.acknowledged_at
    
    def test_database_connection_error_handling(self, temp_db):
        """Test database handles connection errors gracefully"""
        # Create database with invalid path
        invalid_path = "/invalid/path/database.db"
        
        with pytest.raises(Exception):
            IncidentDatabase(invalid_path)
    
    def test_database_migration_columns(self, temp_db):
        """Test that database migration adds missing columns gracefully"""
        # Create database without new columns first
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE incidents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    service_id TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            conn.commit()
        
        # Initialize IncidentDatabase (should add missing columns)
        with patch('builtins.print'):  # Suppress initialization print
            db = IncidentDatabase(temp_db)
        
        # Verify new columns were added
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(incidents)")
            columns = [row[1] for row in cursor.fetchall()]
            
            assert 'resolved_by_ccoe' in columns
            assert 'caused_by_infra' in columns
    
    def test_store_incident_with_none_values(self, test_db, utc_minus_7):
        """Test storing incident with None values in optional fields"""
        incident = Incident(
            id='NONE_TEST',
            title='Test with None values',
            status='triggered',
            service_id='SERVICE1',
            service_name='Test Service',
            created_at=datetime(2025, 8, 23, 10, 0, 0, tzinfo=utc_minus_7),
            resolved_at=None,
            acknowledged_at=None,
            escalation_policy_id=None,
            escalation_policy_name=None,
            priority=None,
            description=None,
            caused_by_infra=None
        )
        
        test_db.store_incident(incident)
        
        # Retrieve and verify None values are preserved
        incidents = test_db.get_incidents_by_date_range('2025-08-23', '2025-08-23')
        retrieved = next(i for i in incidents if i.id == 'NONE_TEST')
        
        assert retrieved.resolved_at is None
        assert retrieved.acknowledged_at is None
        assert retrieved.escalation_policy_id is None
        assert retrieved.escalation_policy_name is None
        assert retrieved.priority is None
        assert retrieved.description is None
        assert retrieved.caused_by_infra is None
    
    @patch('builtins.print')
    def test_initialization_success_message(self, mock_print, temp_db):
        """Test that successful database initialization prints success message"""
        IncidentDatabase(temp_db)
        
        mock_print.assert_called_with(f"✅ Database initialized at {temp_db}")
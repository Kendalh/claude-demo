"""
Test database utilities and sample data for testing
"""
import sqlite3
import tempfile
import os
from datetime import datetime, timezone, timedelta
from typing import List

from incident_v2 import Incident


class TestDatabaseHelper:
    """Helper class for creating and managing test databases"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.temp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
            self.db_path = self.temp_file.name
            self.temp_file.close()
        else:
            self.db_path = db_path
            self.temp_file = None
    
    def create_schema(self):
        """Create the incidents table schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    service_id TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    resolved_at TIMESTAMP,
                    acknowledged_at TIMESTAMP,
                    is_escalated BOOLEAN NOT NULL DEFAULT 0,
                    escalation_policy_id TEXT,
                    escalation_policy_name TEXT,
                    urgency TEXT DEFAULT 'low',
                    priority TEXT,
                    description TEXT,
                    resolved_by_ccoe BOOLEAN NOT NULL DEFAULT 0,
                    caused_by_infra TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_service_created ON incidents (service_id, created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON incidents (status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_escalated ON incidents (is_escalated)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_date ON incidents (DATE(created_at))")
            
            conn.commit()
    
    def insert_sample_incidents(self, incidents: List[Incident]):
        """Insert sample incidents into the test database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for incident in incidents:
                incident_dict = incident.to_dict()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO incidents (
                        id, title, status, service_id, service_name,
                        created_at, resolved_at, acknowledged_at,
                        is_escalated, escalation_policy_id, escalation_policy_name,
                        urgency, priority, description, resolved_by_ccoe, caused_by_infra
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    incident_dict['id'],
                    incident_dict['title'], 
                    incident_dict['status'],
                    incident_dict['service_id'],
                    incident_dict['service_name'],
                    incident_dict['created_at'],
                    incident_dict['resolved_at'],
                    incident_dict['acknowledged_at'],
                    incident_dict['is_escalated'],
                    incident_dict['escalation_policy_id'],
                    incident_dict['escalation_policy_name'],
                    incident_dict['urgency'],
                    incident_dict['priority'],
                    incident_dict['description'],
                    incident_dict['resolved_by_ccoe'],
                    incident_dict['caused_by_infra']
                ))
            
            conn.commit()
    
    def cleanup(self):
        """Clean up temporary database file"""
        if self.temp_file:
            try:
                os.unlink(self.db_path)
            except FileNotFoundError:
                pass


def create_sample_test_incidents():
    """Create a diverse set of test incidents for analytics testing"""
    utc_minus_7 = timezone(timedelta(hours=-7))
    base_time = datetime(2025, 8, 20, 10, 0, 0, tzinfo=utc_minus_7)
    
    incidents = []
    
    # Recent incidents (last 7 days)
    for i in range(10):
        created_time = base_time + timedelta(days=i, hours=i*2)
        resolved_time = created_time + timedelta(hours=1) if i % 3 != 0 else None
        acknowledged_time = created_time + timedelta(minutes=15)
        
        incidents.append(Incident(
            id=f'RECENT{i:02d}ABC',
            title=f'Recent incident {i}',
            status='resolved' if resolved_time else 'triggered',
            service_id='PHMCGNE' if i % 2 == 0 else 'PABCDEF',
            service_name='Test Service A' if i % 2 == 0 else 'Test Service B',
            created_at=created_time,
            resolved_at=resolved_time,
            acknowledged_at=acknowledged_time,
            is_escalated=i % 4 == 0,  # 25% escalation rate
            escalation_policy_id=f'POLICY{i%3}',
            escalation_policy_name=f'Escalation Policy {i%3}',
            urgency='high' if i % 3 == 0 else 'low',
            priority=f'P{(i%4)+1}',
            description=f'Test incident {i} description',
            resolved_by_ccoe=i % 5 == 0,  # 20% CCOE resolution rate
            caused_by_infra='rheos' if i % 6 == 0 else None
        ))
    
    # Older incidents (30+ days ago)
    old_base_time = base_time - timedelta(days=35)
    for i in range(5):
        created_time = old_base_time + timedelta(days=i)
        resolved_time = created_time + timedelta(hours=2)
        
        incidents.append(Incident(
            id=f'OLD{i:02d}XYZ',
            title=f'Old incident {i}',
            status='resolved',
            service_id='PHMCGNE',
            service_name='Test Service A',
            created_at=created_time,
            resolved_at=resolved_time,
            acknowledged_at=created_time + timedelta(minutes=30),
            is_escalated=i % 2 == 0,
            escalation_policy_id='POLICY0',
            escalation_policy_name='Default Policy',
            urgency='low',
            priority='P3',
            description=f'Old test incident {i}',
            resolved_by_ccoe=False,
            caused_by_infra=None
        ))
    
    return incidents
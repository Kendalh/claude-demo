"""
Database Access Layer
Centralized database operations for storing and retrieving Incident objects
"""
import sqlite3
import os
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from incident_v2 import Incident


class IncidentDatabase:
    """Centralized database access layer for Incident objects"""
    
    def __init__(self, db_path: str = "incidents_v2.db"):
        self.db_path = db_path
        self.utc_minus_7 = timezone(timedelta(hours=-7))
        self._init_database()
    
    def _init_database(self):
        """Initialize database with incidents table"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create incidents table
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
            
            # Add new columns if they don't exist (for database migration)
            try:
                cursor.execute("ALTER TABLE incidents ADD COLUMN resolved_by_ccoe BOOLEAN NOT NULL DEFAULT 0")
            except sqlite3.OperationalError:
                pass  # Column already exists
                
            try:
                cursor.execute("ALTER TABLE incidents ADD COLUMN caused_by_infra TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_incidents_service_created 
                ON incidents(service_id, created_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_incidents_status 
                ON incidents(status)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_incidents_escalated 
                ON incidents(is_escalated)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_incidents_created_date 
                ON incidents(DATE(created_at))
            """)
            
            conn.commit()
            print(f"✅ Database initialized at {self.db_path}")
    
    def store_incident(self, incident: Incident) -> None:
        """Store a single incident in the database (INSERT OR REPLACE)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            incident_data = incident.to_dict()
            
            # Get current time in UTC-7
            current_time_utc7 = datetime.now(self.utc_minus_7).isoformat()
            
            cursor.execute("""
                INSERT OR REPLACE INTO incidents 
                (id, title, status, service_id, service_name, created_at, resolved_at, 
                 acknowledged_at, is_escalated, escalation_policy_id, escalation_policy_name,
                 urgency, priority, description, resolved_by_ccoe, caused_by_infra, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                incident_data['id'],
                incident_data['title'],
                incident_data['status'],
                incident_data['service_id'],
                incident_data['service_name'],
                incident_data['created_at'],
                incident_data['resolved_at'],
                incident_data['acknowledged_at'],
                incident_data['is_escalated'],
                incident_data['escalation_policy_id'],
                incident_data['escalation_policy_name'],
                incident_data['urgency'],
                incident_data['priority'],
                incident_data['description'],
                incident_data['resolved_by_ccoe'],
                incident_data['caused_by_infra'],
                current_time_utc7
            ))
            
            conn.commit()
    
    def store_incidents_batch(self, incidents: List[Incident]) -> int:
        """Store multiple incidents in batch for better performance"""
        if not incidents:
            return 0
        
        stored_count = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for incident in incidents:
                try:
                    incident_data = incident.to_dict()
                    
                    # Get current time in UTC-7
                    current_time_utc7 = datetime.now(self.utc_minus_7).isoformat()
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO incidents 
                        (id, title, status, service_id, service_name, created_at, resolved_at, 
                         acknowledged_at, is_escalated, escalation_policy_id, escalation_policy_name,
                         urgency, priority, description, resolved_by_ccoe, caused_by_infra, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        incident_data['id'],
                        incident_data['title'],
                        incident_data['status'],
                        incident_data['service_id'],
                        incident_data['service_name'],
                        incident_data['created_at'],
                        incident_data['resolved_at'],
                        incident_data['acknowledged_at'],
                        incident_data['is_escalated'],
                        incident_data['escalation_policy_id'],
                        incident_data['escalation_policy_name'],
                        incident_data['urgency'],
                        incident_data['priority'],
                        incident_data['description'],
                        incident_data['resolved_by_ccoe'],
                        incident_data['caused_by_infra'],
                        current_time_utc7
                    ))
                    stored_count += 1
                    
                except Exception as e:
                    print(f"❌ Failed to store incident {incident.id}: {e}")
            
            conn.commit()
        
        print(f"💾 Stored {stored_count}/{len(incidents)} incidents in database")
        return stored_count
    
    def get_incidents_by_date_range(self, start_date: str, end_date: str, 
                                   service_id: Optional[str] = None) -> List[Incident]:
        """Get incidents within date range (dates in UTC-7 timezone)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM incidents 
                WHERE substr(created_at, 1, 10) BETWEEN ? AND ?
            """
            params = [start_date, end_date]
            
            if service_id:
                query += " AND service_id = ?"
                params.append(service_id)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            
            incidents = []
            for row in cursor.fetchall():
                incident_data = dict(row)
                incidents.append(Incident.from_dict(incident_data))
            
            return incidents
    
    def get_incidents_last_x_days(self, days: int = 7, 
                                 service_id: Optional[str] = None) -> List[Incident]:
        """Get incidents from last X days (UTC-7 timezone)"""
        now_utc7 = datetime.now(self.utc_minus_7)
        end_date = now_utc7.date().isoformat()
        start_date = (now_utc7.date() - timedelta(days=days)).isoformat()
        
        return self.get_incidents_by_date_range(start_date, end_date, service_id)
    
    def get_escalated_incidents_last_x_days(self, days: int = 7) -> List[Incident]:
        """Get only escalated incidents from last X days"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            now_utc7 = datetime.now(self.utc_minus_7)
            end_date = now_utc7.date().isoformat()
            start_date = (now_utc7.date() - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                SELECT * FROM incidents 
                WHERE DATE(created_at) BETWEEN ? AND ?
                AND is_escalated = 1
                ORDER BY created_at DESC
            """, (start_date, end_date))
            
            incidents = []
            for row in cursor.fetchall():
                incident_data = dict(row)
                incidents.append(Incident.from_dict(incident_data))
            
            return incidents
    
    def get_incident_by_id(self, incident_id: str) -> Optional[Incident]:
        """Get a specific incident by its ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM incidents 
                WHERE id = ?
            """, (incident_id,))
            
            row = cursor.fetchone()
            if row:
                incident_data = dict(row)
                return Incident.from_dict(incident_data)
            return None
    
    def get_all_service_ids(self) -> List[str]:
        """Get all unique service IDs in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT service_id FROM incidents")
            result = cursor.fetchall()
            
            return [row[0] for row in result]
    
    def get_incident_count(self) -> int:
        """Get total number of incidents in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM incidents")
            result = cursor.fetchone()
            
            return result[0] if result else 0
    
    def delete_incidents_older_than_days(self, days: int = 30) -> int:
        """Delete incidents older than specified days (UTC-7 timezone)"""
        now_utc7 = datetime.now(self.utc_minus_7)
        cutoff_date = (now_utc7.date() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM incidents 
                WHERE DATE(created_at) < ?
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            if deleted_count > 0:
                print(f"🗑️ Deleted {deleted_count} incidents older than {days} days")
            
            return deleted_count
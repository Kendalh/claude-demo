"""
Incident Data Transfer Object
Pure data class with no external dependencies - serves as DTO between API and Database layers
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Incident:
    """
    Pure data transfer object representing a PagerDuty incident
    Contains only data fields and basic utility methods - no API or database calls
    """
    id: str
    title: str
    status: str  # triggered, acknowledged, resolved
    service_id: str
    service_name: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    is_escalated: bool = False
    escalation_policy_id: Optional[str] = None
    escalation_policy_name: Optional[str] = None
    urgency: str = "low"  # low, high
    priority: Optional[str] = None
    description: Optional[str] = None
    resolved_by_ccoe: bool = False  # True if resolution field is "ccoe"
    caused_by_infra: Optional[str] = None  # Infrastructure root cause value (rheos, hadoop, tess, etc.)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert incident to dictionary for database storage"""
        return {
            'id': self.id,
            'title': self.title,
            'status': self.status,
            'service_id': self.service_id,
            'service_name': self.service_name,
            'created_at': self.created_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'is_escalated': self.is_escalated,
            'escalation_policy_id': self.escalation_policy_id,
            'escalation_policy_name': self.escalation_policy_name,
            'urgency': self.urgency,
            'priority': self.priority,
            'description': self.description,
            'resolved_by_ccoe': self.resolved_by_ccoe,
            'caused_by_infra': self.caused_by_infra
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Incident':
        """Create Incident from dictionary (e.g., from database)"""
        created_at = datetime.fromisoformat(data['created_at'])
        resolved_at = datetime.fromisoformat(data['resolved_at']) if data['resolved_at'] else None
        acknowledged_at = datetime.fromisoformat(data['acknowledged_at']) if data['acknowledged_at'] else None
        
        return cls(
            id=data['id'],
            title=data['title'],
            status=data['status'],
            service_id=data['service_id'],
            service_name=data['service_name'],
            created_at=created_at,
            resolved_at=resolved_at,
            acknowledged_at=acknowledged_at,
            is_escalated=bool(data['is_escalated']),
            escalation_policy_id=data['escalation_policy_id'],
            escalation_policy_name=data['escalation_policy_name'],
            urgency=data['urgency'],
            priority=data['priority'],
            description=data['description'],
            resolved_by_ccoe=bool(data.get('resolved_by_ccoe', False)),
            caused_by_infra=data.get('caused_by_infra')
        )
    
    def get_date_str_utc_minus_7(self) -> str:
        """Get incident date in UTC-7 timezone as string"""
        from datetime import timezone, timedelta
        utc_minus_7 = timezone(timedelta(hours=-7))
        local_time = self.created_at.astimezone(utc_minus_7)
        return local_time.date().isoformat()
    
    def is_triggered_or_acknowledged(self) -> bool:
        """Check if incident is in triggered or acknowledged state"""
        return self.status.lower() in ['triggered', 'acknowledged']
    
    def is_resolved(self) -> bool:
        """Check if incident is resolved"""
        return self.status.lower() == 'resolved'
    
    def is_caused_by_infrastructure(self) -> bool:
        """Check if incident is caused by infrastructure issue"""
        return bool(self.caused_by_infra and self.caused_by_infra.strip())
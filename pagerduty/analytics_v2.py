"""
Data Analysis Layer
Centralized analytics that issue SQL queries to calculate metrics
"""
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass


@dataclass
class MetricResult:
    """Data class for metric results"""
    metric_name: str
    value: int
    period_days: int
    service_id: Optional[str] = None
    service_name: Optional[str] = None


@dataclass
class ServiceMetrics:
    """Data class for service-level metrics"""
    service_id: str
    service_name: str
    total_incidents: int
    triggered_incidents: int
    resolved_incidents: int
    escalated_incidents: int
    escalation_rate: float
    ccoe_resolved_incidents: int = 0
    infrastructure_caused_incidents: int = 0


class IncidentAnalytics:
    """Centralized data analysis layer using SQL queries for metrics calculation"""
    
    def __init__(self, db_path: str = "incidents_v2.db"):
        self.db_path = db_path
        self.utc_minus_7 = timezone(timedelta(hours=-7))
    
    def get_total_incidents_last_x_days(self, days: int = 7) -> MetricResult:
        """Get total number of incidents in the last X days"""
        now_utc7 = datetime.now(self.utc_minus_7)
        start_date = (now_utc7.date() - timedelta(days=days)).isoformat()
        end_date = now_utc7.date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM incidents 
                WHERE DATE(created_at) BETWEEN ? AND ?
            """, (start_date, end_date))
            
            result = cursor.fetchone()
            count = result[0] if result else 0
            
            return MetricResult(
                metric_name="total_incidents",
                value=count,
                period_days=days
            )
    
    def get_triggered_incidents_last_x_days(self, days: int = 7) -> MetricResult:
        """Get total triggered incidents in the last X days"""
        now_utc7 = datetime.now(self.utc_minus_7)
        start_date = (now_utc7.date() - timedelta(days=days)).isoformat()
        end_date = now_utc7.date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM incidents 
                WHERE DATE(created_at) BETWEEN ? AND ?
                AND status IN ('triggered', 'acknowledged')
            """, (start_date, end_date))
            
            result = cursor.fetchone()
            count = result[0] if result else 0
            
            return MetricResult(
                metric_name="triggered_incidents",
                value=count,
                period_days=days
            )
    
    def get_resolved_incidents_last_x_days(self, days: int = 7) -> MetricResult:
        """Get total resolved incidents in the last X days"""
        now_utc7 = datetime.now(self.utc_minus_7)
        start_date = (now_utc7.date() - timedelta(days=days)).isoformat()
        end_date = now_utc7.date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM incidents 
                WHERE DATE(created_at) BETWEEN ? AND ?
                AND status = 'resolved'
            """, (start_date, end_date))
            
            result = cursor.fetchone()
            count = result[0] if result else 0
            
            return MetricResult(
                metric_name="resolved_incidents",
                value=count,
                period_days=days
            )
    
    def get_escalated_incidents_last_x_days(self, days: int = 7) -> MetricResult:
        """Get total escalated incidents in the last X days"""
        now_utc7 = datetime.now(self.utc_minus_7)
        start_date = (now_utc7.date() - timedelta(days=days)).isoformat()
        end_date = now_utc7.date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM incidents 
                WHERE DATE(created_at) BETWEEN ? AND ?
                AND is_escalated = 1
            """, (start_date, end_date))
            
            result = cursor.fetchone()
            count = result[0] if result else 0
            
            return MetricResult(
                metric_name="escalated_incidents",
                value=count,
                period_days=days
            )
    
    def get_escalation_rate_last_x_days(self, days: int = 7) -> float:
        """Get escalation rate (percentage) for the last X days"""
        total_metric = self.get_total_incidents_last_x_days(days)
        escalated_metric = self.get_escalated_incidents_last_x_days(days)
        
        if total_metric.value == 0:
            return 0.0
        
        return (escalated_metric.value / total_metric.value) * 100
    
    def get_ccoe_resolved_incidents_last_x_days(self, days: int = 7) -> MetricResult:
        """Get number of incidents resolved by CCOE in the last X days"""
        now_utc7 = datetime.now(self.utc_minus_7)
        start_date = (now_utc7.date() - timedelta(days=days)).isoformat()
        end_date = now_utc7.date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM incidents 
                WHERE DATE(created_at) BETWEEN ? AND ?
                  AND resolved_by_ccoe = 1
            """, (start_date, end_date))
            
            count = cursor.fetchone()[0]
            
            return MetricResult(
                metric_name="ccoe_resolved_incidents",
                value=count,
                period_days=days
            )
    
    def get_infrastructure_caused_incidents_last_x_days(self, days: int = 7) -> MetricResult:
        """Get number of incidents caused by infrastructure issues in the last X days"""
        now_utc7 = datetime.now(self.utc_minus_7)
        start_date = (now_utc7.date() - timedelta(days=days)).isoformat()
        end_date = now_utc7.date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM incidents 
                WHERE DATE(created_at) BETWEEN ? AND ?
                  AND caused_by_infra IS NOT NULL 
                  AND caused_by_infra != ''
            """, (start_date, end_date))
            
            count = cursor.fetchone()[0]
            
            return MetricResult(
                metric_name="infrastructure_caused_incidents",
                value=count,
                period_days=days
            )
    
    def get_service_metrics_last_x_days(self, days: int = 7) -> List[ServiceMetrics]:
        """Get metrics broken down by service for the last X days"""
        now_utc7 = datetime.now(self.utc_minus_7)
        start_date = (now_utc7.date() - timedelta(days=days)).isoformat()
        end_date = now_utc7.date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    service_id,
                    service_name,
                    COUNT(*) as total_incidents,
                    SUM(CASE WHEN status IN ('triggered', 'acknowledged') THEN 1 ELSE 0 END) as triggered_incidents,
                    SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved_incidents,
                    SUM(CASE WHEN is_escalated = 1 THEN 1 ELSE 0 END) as escalated_incidents,
                    SUM(CASE WHEN resolved_by_ccoe = 1 THEN 1 ELSE 0 END) as ccoe_resolved_incidents,
                    SUM(CASE WHEN caused_by_infra IS NOT NULL AND caused_by_infra != '' THEN 1 ELSE 0 END) as infrastructure_caused_incidents
                FROM incidents 
                WHERE DATE(created_at) BETWEEN ? AND ?
                GROUP BY service_id, service_name
                ORDER BY total_incidents DESC
            """, (start_date, end_date))
            
            results = []
            for row in cursor.fetchall():
                service_id, service_name, total, triggered, resolved, escalated, ccoe_resolved, infra_caused = row
                escalation_rate = (escalated / total * 100) if total > 0 else 0.0
                
                results.append(ServiceMetrics(
                    service_id=service_id,
                    service_name=service_name,
                    total_incidents=total,
                    triggered_incidents=triggered,
                    resolved_incidents=resolved,
                    escalated_incidents=escalated,
                    escalation_rate=escalation_rate,
                    ccoe_resolved_incidents=ccoe_resolved,
                    infrastructure_caused_incidents=infra_caused
                ))
            
            return results
    
    def get_daily_incident_trend_last_x_days(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily incident counts for trend analysis"""
        now_utc7 = datetime.now(self.utc_minus_7)
        start_date = (now_utc7.date() - timedelta(days=days)).isoformat()
        end_date = now_utc7.date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    DATE(created_at) as incident_date,
                    COUNT(*) as total_incidents,
                    SUM(CASE WHEN status IN ('triggered', 'acknowledged') THEN 1 ELSE 0 END) as triggered_incidents,
                    SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved_incidents,
                    SUM(CASE WHEN is_escalated = 1 THEN 1 ELSE 0 END) as escalated_incidents
                FROM incidents 
                WHERE DATE(created_at) BETWEEN ? AND ?
                GROUP BY DATE(created_at)
                ORDER BY incident_date DESC
            """, (start_date, end_date))
            
            results = []
            for row in cursor.fetchall():
                date, total, triggered, resolved, escalated = row
                results.append({
                    'date': date,
                    'total_incidents': total,
                    'triggered_incidents': triggered,
                    'resolved_incidents': resolved,
                    'escalated_incidents': escalated,
                    'escalation_rate': (escalated / total * 100) if total > 0 else 0.0
                })
            
            return results
    
    def get_summary_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive summary metrics for the last X days"""
        total_metric = self.get_total_incidents_last_x_days(days)
        triggered_metric = self.get_triggered_incidents_last_x_days(days)
        resolved_metric = self.get_resolved_incidents_last_x_days(days)
        escalated_metric = self.get_escalated_incidents_last_x_days(days)
        escalation_rate = self.get_escalation_rate_last_x_days(days)
        
        service_metrics = self.get_service_metrics_last_x_days(days)
        daily_trend = self.get_daily_incident_trend_last_x_days(days)
        
        return {
            'period_days': days,
            'total_incidents': total_metric.value,
            'triggered_incidents': triggered_metric.value,
            'resolved_incidents': resolved_metric.value,
            'escalated_incidents': escalated_metric.value,
            'escalation_rate': round(escalation_rate, 2),
            'services_count': len(service_metrics),
            'service_metrics': service_metrics,
            'daily_trend': daily_trend
        }
    
    def get_top_escalated_services(self, days: int = 7, limit: int = 5) -> List[ServiceMetrics]:
        """Get top services by escalated incident count"""
        service_metrics = self.get_service_metrics_last_x_days(days)
        
        # Sort by escalated incidents count, then by escalation rate
        sorted_services = sorted(
            service_metrics, 
            key=lambda x: (x.escalated_incidents, x.escalation_rate), 
            reverse=True
        )
        
        return sorted_services[:limit]
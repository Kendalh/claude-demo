"""
Sample PagerDuty API response data for testing
"""

SAMPLE_PAGERDUTY_INCIDENTS_RESPONSE = {
    "incidents": [
        {
            "id": "Q1ABC123DEF",
            "title": "Database Connection Timeout",
            "status": "resolved",
            "service": {
                "id": "PHMCGNE",
                "summary": "Production Database Service"
            },
            "created_at": "2025-08-23T10:00:00-07:00",
            "updated_at": "2025-08-23T11:30:00-07:00",
            "escalation_policy": {
                "id": "POLICY123", 
                "summary": "Database Team Escalation"
            },
            "urgency": "high",
            "priority": {
                "summary": "P1"
            },
            "description": "Database connection timeouts affecting multiple services",
            "custom_fields": [
                {
                    "field": {
                        "name": "resolution"
                    },
                    "value": "ccoe"
                },
                {
                    "field": {
                        "name": "prelim_root_cause"
                    },
                    "value": "rheos"
                }
            ]
        },
        {
            "id": "Q2DEF456GHI",
            "title": "API Rate Limit Exceeded",
            "status": "triggered",
            "service": {
                "id": "PHMCGNE",
                "summary": "Production Database Service"
            },
            "created_at": "2025-08-23T12:00:00-07:00",
            "updated_at": "2025-08-23T12:15:00-07:00",
            "escalation_policy": {
                "id": "POLICY123",
                "summary": "Database Team Escalation"
            },
            "urgency": "low",
            "priority": {
                "summary": "P3"
            },
            "description": "API requests hitting rate limits",
            "custom_fields": [
                {
                    "field": {
                        "name": "resolution"
                    },
                    "value": "team"
                },
                {
                    "field": {
                        "name": "prelim_root_cause"
                    },
                    "value": "hadoop"
                }
            ]
        }
    ]
}

SAMPLE_PAGERDUTY_LOG_ENTRIES_RESPONSE = {
    "log_entries": [
        {
            "id": "LOG123",
            "type": "escalate_log_entry",
            "created_at": "2025-08-23T10:30:00-07:00",
            "agent": {
                "summary": "Database Team Escalation Policy"
            },
            "channel": {
                "summary": "Auto-escalation after 30 minutes"
            }
        },
        {
            "id": "LOG124", 
            "type": "acknowledge_log_entry",
            "created_at": "2025-08-23T10:15:00-07:00",
            "agent": {
                "summary": "John Doe"
            }
        }
    ]
}

SAMPLE_PAGERDUTY_SERVICES_RESPONSE = {
    "services": [
        {
            "id": "PHMCGNE",
            "name": "Production Database Service",
            "status": "active",
            "escalation_policy": {
                "id": "POLICY123",
                "summary": "Database Team Escalation"
            }
        },
        {
            "id": "PABCDEF", 
            "name": "Payment Processing Service",
            "status": "active",
            "escalation_policy": {
                "id": "POLICY456",
                "summary": "Payment Team Escalation"
            }
        }
    ]
}

SAMPLE_ESCALATED_INCIDENT = {
    "id": "Q3GHI789JKL",
    "title": "Critical System Failure",
    "status": "resolved",
    "service": {
        "id": "PHMCGNE",
        "summary": "Production Database Service"
    },
    "created_at": "2025-08-22T15:00:00-07:00",
    "updated_at": "2025-08-22T18:00:00-07:00",
    "escalation_policy": {
        "id": "POLICY123",
        "summary": "Database Team Escalation"
    },
    "urgency": "high",
    "priority": {
        "summary": "P1"
    },
    "description": "Complete system outage requiring escalation",
    "custom_fields": [
        {
            "field": {
                "name": "resolution"
            },
            "value": "ccoe"
        },
        {
            "field": {
                "name": "prelim_root_cause"
            },
            "value": "tess"
        }
    ]
}

SAMPLE_NON_ESCALATED_INCIDENT = {
    "id": "Q4JKL012MNO",
    "title": "Minor Performance Issue",
    "status": "resolved", 
    "service": {
        "id": "PABCDEF",
        "summary": "Payment Processing Service"
    },
    "created_at": "2025-08-22T09:00:00-07:00",
    "updated_at": "2025-08-22T09:30:00-07:00",
    "escalation_policy": {
        "id": "POLICY456",
        "summary": "Payment Team Escalation"
    },
    "urgency": "low",
    "priority": {
        "summary": "P4"
    },
    "description": "Slight performance degradation resolved quickly",
    "custom_fields": [
        {
            "field": {
                "name": "resolution"
            },
            "value": "team"
        }
    ]
}

SAMPLE_CONFIG_YAML = """
token: test_api_token_12345
services:
  - name: Production Database Service
    url: https://company.pagerduty.com/service-directory/PHMCGNE
  - name: Payment Processing Service
    url: https://company.pagerduty.com/service-directory/PABCDEF
"""
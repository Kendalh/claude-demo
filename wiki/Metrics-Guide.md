# Metrics & Analytics Guide

Complete guide to understanding the metrics tracked by the PagerDuty Incident Analytics Dashboard.

## 📊 Overview

The system tracks six key metrics for each service:

1. **Total Incidents** - All incidents in the period
2. **Triggered Incidents** - Currently active incidents
3. **Resolved Incidents** - Successfully closed incidents
4. **Escalated Incidents** - Incidents requiring escalation
5. **CCOE Resolved Incidents** - Incidents resolved by CCOE team
6. **Infrastructure Caused Incidents** - Incidents from infrastructure issues

## 🎯 Metric Definitions

### 1. Total Incidents

**Definition:** Count of all incidents created within the specified time period.

**Calculation:**
```sql
SELECT COUNT(*) FROM incidents
WHERE DATE(created_at) BETWEEN start_date AND end_date
  AND service_id = 'PHMCGNE'
```

**Includes:**
- All incident statuses (triggered, acknowledged, resolved)
- All urgency levels (high, low)
- All priorities

**Use Cases:**
- Overall service health indicator
- Workload measurement
- Trend analysis

**What Good Looks Like:**
- Stable or decreasing trend over time
- Predictable patterns (e.g., lower on weekends)

**Red Flags:**
- Sudden spikes (may indicate outage)
- Sustained increase (may indicate systemic issue)

---

### 2. Triggered Incidents

**Definition:** Count of incidents currently in triggered or acknowledged status.

**Calculation:**
```sql
SELECT COUNT(*) FROM incidents
WHERE status IN ('triggered', 'acknowledged')
  AND DATE(created_at) BETWEEN start_date AND end_date
  AND service_id = 'PHMCGNE'
```

**Status Breakdown:**
- **triggered**: Incident is open, not yet acknowledged
- **acknowledged**: On-call engineer is aware, working on it

**Use Cases:**
- Current workload assessment
- On-call stress indicator
- Real-time service health

**What Good Looks Like:**
- Low absolute number
- Quick transition to resolved
- Minimal backlog

**Red Flags:**
- High triggered count (overwhelmed on-call)
- Incidents stuck in triggered state
- Increasing backlog

---

### 3. Resolved Incidents

**Definition:** Count of incidents that have been resolved within the specified time period.

**Calculation:**
```sql
SELECT COUNT(*) FROM incidents
WHERE status = 'resolved'
  AND DATE(created_at) BETWEEN start_date AND end_date
  AND service_id = 'PHMCGNE'
```

**Criteria:**
- Status is 'resolved'
- Has `resolved_at` timestamp
- Created within the analysis period

**Use Cases:**
- Team productivity measurement
- Resolution efficiency tracking
- Success rate calculation

**What Good Looks Like:**
- Resolved count ≈ Total incidents
- Quick time to resolution
- High resolution rate

**Red Flags:**
- Low resolution rate (many incidents unresolved)
- Long time to resolution
- Increasing unresolved backlog

---

### 4. Escalated Incidents

**Definition:** Count of incidents that required escalation to another team or higher level of support.

**Detection Method:**
Analyzes PagerDuty log entries for `escalate_log_entry` type:

```python
def check_if_escalated(log_entries):
    for entry in log_entries:
        if entry.get('type') == 'escalate_log_entry':
            return True
    return False
```

**Calculation:**
```sql
SELECT COUNT(*) FROM incidents
WHERE is_escalated = 1
  AND DATE(created_at) BETWEEN start_date AND end_date
  AND service_id = 'PHMCGNE'
```

**What Counts as Escalation:**
- Manual escalation by on-call engineer
- Automatic escalation due to timeout
- Transfer to another team
- Escalation to manager or senior engineer

**Use Cases:**
- Service complexity indicator
- On-call capability assessment
- Training needs identification

**What Good Looks Like:**
- Low escalation rate (< 10%)
- Stable or decreasing trend
- Clear escalation patterns

**Red Flags:**
- High escalation rate (> 20%)
- Increasing trend
- Frequent escalations on same incident types

---

### 5. Escalation Rate

**Definition:** Percentage of incidents that required escalation.

**Calculation:**
```
Escalation Rate = (Escalated Incidents / Total Incidents) × 100%
```

**Example:**
```
Total: 100 incidents
Escalated: 15 incidents
Escalation Rate = (15 / 100) × 100% = 15%
```

**Benchmarks:**
- **Excellent**: < 5%
- **Good**: 5-10%
- **Acceptable**: 10-15%
- **Concerning**: 15-20%
- **Critical**: > 20%

**Use Cases:**
- Service health primary indicator
- On-call effectiveness measurement
- Runbook quality assessment

**What Good Looks Like:**
- Low rate (< 10%)
- Stable or decreasing trend
- Similar across services

**Red Flags:**
- Rate > 20%
- Increasing trend
- Large variance between services

---

### 6. CCOE Resolved Incidents

**Definition:** Count of incidents resolved by the CCOE (Center of Excellence) team.

**Detection Method:**
Checks custom field `resolution` for value `ccoe`:

```python
custom_fields = api.get_incident_custom_fields(incident_id)
for field in custom_fields:
    if field['name'] == 'resolution' and field['value'].lower() == 'ccoe':
        incident.resolved_by_ccoe = True
```

**Calculation:**
```sql
SELECT COUNT(*) FROM incidents
WHERE resolved_by_ccoe = 1
  AND DATE(created_at) BETWEEN start_date AND end_date
  AND service_id = 'PHMCGNE'
```

**Use Cases:**
- CCOE workload tracking
- Team contribution measurement
- Resource allocation planning

**What Good Looks Like:**
- Appropriate for service type
- Consistent support availability
- Quick CCOE response time

**Red Flags:**
- High CCOE dependency (> 30% of incidents)
- Increasing trend (indicates knowledge gap)
- Slow CCOE response

---

### 7. Infrastructure Caused Incidents

**Definition:** Count of incidents caused by underlying infrastructure issues.

**Detection Method:**
Checks custom field `prelim_root_cause` for infrastructure component values:

```python
infrastructure_components = ['rheos', 'hadoop', 'tess', 'hbase', 'kafka', ...]

custom_fields = api.get_incident_custom_fields(incident_id)
for field in custom_fields:
    if field['name'] == 'prelim_root_cause':
        if field['value'] in infrastructure_components:
            incident.prelim_root_cause = field['value']
```

**Calculation:**
```sql
SELECT COUNT(*) FROM incidents
WHERE prelim_root_cause IS NOT NULL
  AND DATE(created_at) BETWEEN start_date AND end_date
  AND service_id = 'PHMCGNE'
```

**Common Infrastructure Components:**
- **rheos**: Compute infrastructure
- **hadoop**: Data processing
- **tess**: Configuration management
- **hbase**: NoSQL database
- **kafka**: Message streaming

**Use Cases:**
- Infrastructure health tracking
- Dependency identification
- Platform team accountability

**What Good Looks Like:**
- Low infrastructure incident rate
- Decreasing trend
- Proactive infrastructure improvements

**Red Flags:**
- High infrastructure dependency
- Recurring failures in same component
- Increasing trend

---

## 📈 Metric Relationships

### Total Incidents Breakdown

```
Total Incidents = Triggered + Resolved
```

**Note:** This is for incidents created in the period, not current state.

### Escalation Analysis

```
Escalation Rate = (Escalated / Total) × 100%
```

Higher escalation rate may indicate:
- Complex incidents
- Insufficient on-call training
- Poor runbook quality
- Service architecture issues

### CCOE Dependency

```
CCOE Dependency = (CCOE Resolved / Total Resolved) × 100%
```

High dependency may indicate:
- Specialized knowledge required
- Knowledge not distributed to team
- Service ownership unclear

### Infrastructure Impact

```
Infrastructure Impact = (Infrastructure Caused / Total) × 100%
```

High impact may indicate:
- Unreliable infrastructure
- Service too dependent on infrastructure
- Need for better error handling

---

## 📊 Time-Based Analysis

### Daily Metrics

**Use Cases:**
- Identify specific problem days
- Correlate with deployments or events
- Spot patterns (day of week)

**Example Query:**
```sql
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total,
    SUM(is_escalated) as escalated
FROM incidents
WHERE service_id = 'PHMCGNE'
GROUP BY DATE(created_at)
ORDER BY date DESC
```

### Weekly Metrics

**Use Cases:**
- Week-over-week comparison
- Short-term trend analysis
- Sprint retrospectives

**Recommended Period:** 7 days

### Monthly Metrics

**Use Cases:**
- Long-term trend analysis
- Quarterly reporting
- Capacity planning

**Recommended Period:** 30 days

---

## 🎯 Service-Level Metrics

### Per-Service Analysis

Each service has its own metric profile:

```python
class ServiceMetrics:
    service_id: str
    service_name: str
    total_incidents: int
    triggered_incidents: int
    resolved_incidents: int
    escalated_incidents: int
    escalation_rate: float
    ccoe_resolved_incidents: int
    infrastructure_caused_incidents: int
```

### Cross-Service Comparison

**Top Escalated Services:**
Identifies services with highest escalation rates.

**Use Cases:**
- Priority ranking for improvements
- Resource allocation
- Training focus areas

**Example:**
```
Top Escalated Services (Last 7 Days):
1. Service A: 25 escalated (20.5%)
2. Service B: 18 escalated (15.3%)
3. Service C: 12 escalated (10.1%)
```

---

## 📉 Trend Analysis

### Trend Visualization

The dashboard shows trends using Chart.js:

- **X-axis**: Date
- **Y-axis**: Incident count
- **Lines**: Each metric (color-coded)

**Trend Patterns:**

1. **Improving**: Decreasing total and escalated incidents
2. **Stable**: Consistent incident counts over time
3. **Degrading**: Increasing incidents or escalation rate
4. **Volatile**: Large day-to-day variations

### Moving Averages

**7-Day Moving Average:**
Smooths out daily variations to show true trends.

```sql
SELECT 
    date,
    AVG(total_incidents) OVER (
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg
FROM daily_metrics
```

---

## 🎨 Metric Display

### Dashboard Cards

Summary cards show current metrics with visual indicators:

```
┌─────────────────────────┐
│ Total Incidents         │
│        128              │
│     ↑ 5.2% from last    │
└─────────────────────────┘
```

### Color Coding

**Badge Colors:**
- **Blue**: Total incidents
- **Orange**: Triggered incidents
- **Green**: Resolved incidents
- **Red**: Escalated incidents (with "!" indicator)
- **Cyan**: CCOE resolved (with "C" indicator)
- **Gray**: Infrastructure caused (with "I" indicator)

### Calendar View

Each day shows:
```
[20]
🔵 15  (total)
🟠 3   (triggered)
🟢 12  (resolved)
🔴 2!  (escalated)
🔵 1C  (CCOE)
⚫ 1I  (infra)
```

---

## 🔍 Metric Drill-Down

### From Summary to Details

**Level 1: Overall Summary**
```
Total: 128, Escalated: 15 (11.7%)
```

**Level 2: Service Breakdown**
```
Service A: 45 total, 5 escalated (11.1%)
Service B: 32 total, 3 escalated (9.4%)
```

**Level 3: Daily Trend**
```
Oct 20: 18 total, 2 escalated
Oct 19: 22 total, 3 escalated
```

**Level 4: Individual Incidents**
```
Q1ABCDEF: High CPU - Escalated to Platform Team
```

### Hover Details

On calendar, hovering escalated badges shows:
- Incident ID
- Incident title
- Direct link to PagerDuty
- Status and urgency

---

## 📐 Metric Calculations

### Summary Metrics

**Overall Metrics:**
```python
summary = {
    'total_incidents': 128,
    'triggered_incidents': 23,
    'resolved_incidents': 105,
    'escalated_incidents': 15,
    'escalation_rate': 11.72,
    'services_count': 6,
    'ccoe_resolved_incidents': 8,
    'infrastructure_caused_incidents': 12
}
```

**SQL Implementation:**
```sql
SELECT 
    COUNT(*) as total_incidents,
    SUM(CASE WHEN status IN ('triggered','acknowledged') THEN 1 ELSE 0 END) as triggered,
    SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved,
    SUM(is_escalated) as escalated,
    ROUND(100.0 * SUM(is_escalated) / COUNT(*), 2) as escalation_rate,
    SUM(resolved_by_ccoe) as ccoe_resolved,
    SUM(CASE WHEN prelim_root_cause IS NOT NULL THEN 1 ELSE 0 END) as infra_caused
FROM incidents
WHERE DATE(created_at) >= DATE('now', '-7 days')
```

---

## 💡 Best Practices

### Metric Interpretation

1. **Context Matters**: Compare to historical baselines
2. **Look for Trends**: Single data points can be misleading
3. **Multiple Metrics**: Use combination of metrics for insights
4. **Drill Down**: Always investigate anomalies

### Setting Baselines

1. **Collect 30 days**: Establish baseline over time
2. **Account for Variability**: Weekends vs weekdays
3. **Seasonal Patterns**: Month-end, quarter-end effects
4. **Set Thresholds**: Define acceptable ranges

### Action Triggers

**When Escalation Rate > 15%:**
- Review recent incidents
- Update runbooks
- Schedule training

**When CCOE Dependency > 30%:**
- Knowledge transfer session
- Update documentation
- Improve on-call training

**When Infrastructure Incidents > 20%:**
- Meet with platform team
- Review SLAs
- Implement circuit breakers

---

**See Also:**
- [Web Dashboard](Web-Dashboard.md)
- [CLI Guide](CLI-Guide.md)
- [Database Schema](Database-Schema.md)

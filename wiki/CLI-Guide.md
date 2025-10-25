# Command Line Interface Guide

Complete reference for the PagerDuty Incident Analytics Dashboard CLI.

## 📖 Overview

The command-line interface (`main_v2.py`) provides powerful tools for:
- Fetching and updating incident data from PagerDuty
- Viewing summaries and analytics
- Managing the database
- Troubleshooting and debugging

## 🚀 Basic Usage

```bash
python3 main_v2.py [COMMAND] [OPTIONS]
```

## 📋 Commands Reference

### 1. Update Incidents

Fetch incident data from PagerDuty API and update the database.

#### Update All Services

```bash
python3 main_v2.py --update-incidents DAYS
```

**Examples:**
```bash
# Last 7 days (all services)
python3 main_v2.py --update-incidents 7

# Last 30 days (all services)
python3 main_v2.py --update-incidents 30

# Last 3 days (quick update)
python3 main_v2.py --update-incidents 3
```

**What it does:**
- Fetches incidents from all services in `PagerDuty.yaml`
- Retrieves log entries to detect escalations
- Extracts custom fields (CCOE resolution, root cause)
- Stores/updates incidents in database
- Shows progress and summary

**Output:**
```
🔄 Updating incidents for all services for the last 7 days...
⏱️ This may take several minutes for escalation checking...
🌐 Starting API calls to PagerDuty...
💾 Storing incidents in database...

📊 Update Summary:
   Period: Last 7 days
   Total incidents fetched: 128
   Incidents stored: 128
   Escalated incidents: 15
   Execution time: 245.32 seconds (4.1 minutes)
✅ Update completed successfully
```

#### Update Specific Service

```bash
python3 main_v2.py --update-incidents DAYS --service SERVICE_ID
```

**Examples:**
```bash
# Update only Sojourner service for last 7 days
python3 main_v2.py --update-incidents 7 --service PHMCGNE

# Update only Customer Journey Signals for last 14 days
python3 main_v2.py --update-incidents 14 --service P0CAL62
```

**Benefits:**
- ⚡ Faster than updating all services
- 🎯 Focus on specific service
- 🔄 Good for frequent updates of critical services

**Finding Service IDs:**
```bash
# View all service IDs
python3 main_v2.py --database-info
```

### 2. Show Summary

Display incident metrics and statistics.

#### Overall Summary

```bash
python3 main_v2.py --show-summary [DAYS]
```

**Examples:**
```bash
# 7-day summary (default)
python3 main_v2.py --show-summary

# 30-day summary
python3 main_v2.py --show-summary 30

# 14-day summary
python3 main_v2.py --show-summary 14
```

**Output:**
```
📊 Incident Summary - Last 7 Days
==================================================

🔢 Overall Metrics:
   Total incidents: 128
   Triggered incidents: 23
   Resolved incidents: 105
   Escalated incidents: 15
   Escalation rate: 11.7%
   Services monitored: 6

🔧 Service Breakdown:

    Service Name: Sojourner SLA Service
      Service ID: PHMCGNE
      Total incidents: 45
      • Triggered: 8
      • Resolved: 37
      • Escalated: 5 (11.1%)

    Service Name: Customer Journey Signals
      Service ID: P0CAL62
      Total incidents: 32
      • Triggered: 5
      • Resolved: 27
      • Escalated: 3 (9.4%)

🚨 Top Escalated Services:
   1. Sojourner SLA Service: 5 escalated (11.1%)
   2. Customer Journey Signals: 3 escalated (9.4%)
   3. Product Analytics: 2 escalated (8.0%)

📈 Daily Trend:
   2025-10-20: 18 total, 2 escalated
   2025-10-19: 22 total, 3 escalated
   2025-10-18: 15 total, 1 escalated
   ...
```

**Metrics Explained:**
- **Total incidents**: All incidents in the period
- **Triggered**: Currently active (not resolved)
- **Resolved**: Successfully resolved
- **Escalated**: Had escalation log entries
- **Escalation rate**: (Escalated / Total) × 100%

### 3. Show Escalations

Display only escalated incidents with details.

```bash
python3 main_v2.py --show-escalations [DAYS]
```

**Examples:**
```bash
# Escalations in last 7 days
python3 main_v2.py --show-escalations

# Escalations in last 30 days
python3 main_v2.py --show-escalations 30
```

**Output:**
```
🚨 Escalated Incidents - Last 7 Days
==================================================
Found 15 escalated incidents:

📍 Sojourner SLA Service
   ID: Q1ABCDEF
   Title: High CPU usage on production server
   Status: resolved
   Created: 2025-10-20 14:30:45 UTC
   Urgency: high
   Priority: P1
   URL: https://ebay-cpt.pagerduty.com/incidents/Q1ABCDEF

📍 Customer Journey Signals
   ID: Q2GHIJKL
   Title: Database connection timeout
   Status: triggered
   Created: 2025-10-20 09:15:30 UTC
   Urgency: high
   Priority: P2
   URL: https://ebay-cpt.pagerduty.com/incidents/Q2GHIJKL
```

**Use Cases:**
- 🔍 Investigation: Review recent escalations
- 📊 Reporting: Generate escalation reports
- 🎯 Focus: Identify problem areas

### 4. Database Information

View database statistics and health.

```bash
python3 main_v2.py --database-info
```

**Output:**
```
📊 Database Information
==================================================

📈 Statistics:
   Total incidents: 1,234
   Triggered incidents: 234
   Resolved incidents: 1,000
   Escalated incidents: 123
   CCOE resolved: 45
   Infrastructure caused: 67

📅 Date Range:
   Earliest incident: 2025-08-15
   Latest incident: 2025-10-20
   Days of data: 66

🔧 Services in Database:
   • PHMCGNE: Sojourner SLA Service
   • P0CAL62: Customer Journey Signals
   • PVT5IW4: Touchstone Reporting Support
   • PY23FJQ: Touchstone On Call
   • PHZ57RZ: Tracking CCOE High Priority
   • PJFLEB2: Product Analytics

💾 Database File:
   Path: /path/to/pagerduty.db
   Size: 2.4 MB
```

**Use Cases:**
- ✅ Verify data is loaded
- 🔍 Check date coverage
- 📊 Quick statistics overview
- 🎯 Find service IDs for targeted updates

### 5. Get Incident Details

Retrieve detailed information for a specific incident.

```bash
python3 main_v2.py --get-incident INCIDENT_ID
```

**Examples:**
```bash
# Get incident by ID
python3 main_v2.py --get-incident Q1ABCDEF

# Get incident by number
python3 main_v2.py --get-incident 12345
```

**Output:**
```
📋 Incident Details
==================================================
ID: Q1ABCDEF
Number: #12345
Title: High CPU usage on production server
Status: resolved
Urgency: high
Priority: P1

Service: Sojourner SLA Service (PHMCGNE)

Timestamps:
   Created: 2025-10-20 14:30:45
   Updated: 2025-10-20 15:45:30
   Resolved: 2025-10-20 16:00:00

Analytics:
   Escalated: Yes
   CCOE Resolved: No
   Infrastructure Cause: rheos

URL: https://ebay-cpt.pagerduty.com/incidents/Q1ABCDEF
```

**Use Cases:**
- 🔍 Debug specific incident
- ✅ Verify data accuracy
- 📊 Incident investigation

### 6. Update Specific Service for Date

Update a specific service for a specific date.

```bash
python3 main_v2.py --update-service SERVICE_ID --date YYYY-MM-DD
```

**Examples:**
```bash
# Update Sojourner for specific date
python3 main_v2.py --update-service PHMCGNE --date 2025-10-20

# Update Customer Journey for yesterday
python3 main_v2.py --update-service P0CAL62 --date 2025-10-19
```

**Use Cases:**
- 🎯 Targeted update for specific day
- 🔄 Refresh specific service data
- 🐛 Fix missing data for particular date

### 7. Cleanup Old Data

Remove incidents older than specified days.

```bash
python3 main_v2.py --cleanup DAYS
```

**Examples:**
```bash
# Remove incidents older than 60 days
python3 main_v2.py --cleanup 60

# Remove incidents older than 90 days
python3 main_v2.py --cleanup 90
```

**Output:**
```
🧹 Cleaning up incidents older than 60 days...
✅ Removed 234 old incidents
💾 Database size reduced
```

**Recommendations:**
- 🗓️ Run monthly
- 📊 Keep 60-90 days of data
- 💾 Free up disk space
- ⚡ Improve query performance

**Warning:** This permanently deletes data!

### 8. Help

Display all available commands.

```bash
python3 main_v2.py --help
```

## 🎯 Common Workflows

### Daily Update Workflow

```bash
# Morning routine - update yesterday's data
python3 main_v2.py --update-incidents 2

# Check summary
python3 main_v2.py --show-summary 7

# Review escalations
python3 main_v2.py --show-escalations 7
```

### Weekly Analysis Workflow

```bash
# Update full week
python3 main_v2.py --update-incidents 7

# Generate weekly summary
python3 main_v2.py --show-summary 7

# Compare with previous 30 days
python3 main_v2.py --show-summary 30
```

### Targeted Investigation Workflow

```bash
# Update specific service
python3 main_v2.py --update-incidents 14 --service PHMCGNE

# View escalations for that service
python3 main_v2.py --show-escalations 14

# Get details on specific incident
python3 main_v2.py --get-incident Q1ABCDEF
```

### Monthly Maintenance Workflow

```bash
# Update all data
python3 main_v2.py --update-incidents 30

# Check database health
python3 main_v2.py --database-info

# Cleanup old data
python3 main_v2.py --cleanup 90
```

## ⚙️ Advanced Usage

### Combining with Shell Scripts

#### Automated Daily Update

```bash
#!/bin/bash
# daily_update.sh

cd /path/to/pagerduty
python3 main_v2.py --update-incidents 2 > /tmp/pagerduty_update.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Daily update successful"
else
    echo "❌ Update failed - check /tmp/pagerduty_update.log"
fi
```

#### Weekly Report

```bash
#!/bin/bash
# weekly_report.sh

cd /path/to/pagerduty
python3 main_v2.py --show-summary 7 > weekly_report_$(date +%Y-%m-%d).txt
python3 main_v2.py --show-escalations 7 >> weekly_report_$(date +%Y-%m-%d).txt
```

### Cron Scheduling

```cron
# Update daily at 9 AM
0 9 * * * cd /path/to/pagerduty && python3 main_v2.py --update-incidents 2

# Weekly summary on Mondays at 8 AM
0 8 * * 1 cd /path/to/pagerduty && python3 main_v2.py --show-summary 7 | mail -s "Weekly PagerDuty Summary" team@example.com

# Monthly cleanup on 1st day at midnight
0 0 1 * * cd /path/to/pagerduty && python3 main_v2.py --cleanup 90
```

### Output Redirection

```bash
# Save to file
python3 main_v2.py --show-summary 7 > summary.txt

# Append to file
python3 main_v2.py --show-escalations >> escalations.log

# Both stdout and stderr
python3 main_v2.py --update-incidents 7 > update.log 2>&1

# Suppress output
python3 main_v2.py --cleanup 60 > /dev/null 2>&1
```

## 🛑 Signal Handling

The CLI gracefully handles interruption signals:

### Ctrl+C (SIGINT)

```bash
# Press Ctrl+C during long operation
python3 main_v2.py --update-incidents 30
^C
🛑 Operation cancelled by user after 45.2 seconds
💾 Any processed incidents have been saved to the database
```

**Behavior:**
- Saves all processed incidents
- Displays execution time
- Exits cleanly

### Timeout Protection

For very long operations:
- Heartbeat messages every 30 seconds
- Progress indicators
- Prevents timeouts

## 🐛 Debugging

### Verbose Output

Currently not available, but can be added:

```python
# Future enhancement
python3 main_v2.py --update-incidents 7 --verbose
```

### Dry Run Mode

Currently not available, but recommended:

```python
# Future enhancement
python3 main_v2.py --update-incidents 7 --dry-run
```

### Error Messages

Common error patterns:

```bash
# Invalid service ID
❌ Service ID INVALID not found in PagerDuty.yaml
💡 Available services: PHMCGNE, P0CAL62, PVT5IW4, ...

# API authentication failure
❌ Error: 401 Unauthorized
💡 Check API token in PagerDuty.yaml

# Network issues
❌ Error: Connection timeout
💡 Check network connectivity to PagerDuty API
```

## 💡 Tips & Best Practices

### Performance Tips

1. **Use Specific Services**: Update only needed services
   ```bash
   python3 main_v2.py --update-incidents 7 --service PHMCGNE
   ```

2. **Shorter Time Ranges**: Start with fewer days
   ```bash
   python3 main_v2.py --update-incidents 3  # Faster than 30
   ```

3. **Off-Peak Updates**: Run during low-activity periods

### Data Management Tips

1. **Regular Updates**: Daily updates are faster than weekly
2. **Incremental Approach**: Update recent data more frequently
3. **Regular Cleanup**: Monthly cleanup keeps database performant

### Scheduling Tips

1. **Stagger Updates**: Don't update all services at once
2. **Early Morning**: Run before business hours
3. **Monitor First**: Check results before automation

## 📊 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error occurred |
| 130 | Interrupted by user (Ctrl+C) |

**Usage in scripts:**
```bash
python3 main_v2.py --update-incidents 7
if [ $? -eq 0 ]; then
    echo "Success"
else
    echo "Failed"
fi
```

---

**See Also:**
- [Quick Start Guide](Quick-Start.md)
- [Web Dashboard](Web-Dashboard.md)
- [Troubleshooting](Troubleshooting.md)

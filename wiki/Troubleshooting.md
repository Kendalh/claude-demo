# Troubleshooting Guide

Common issues and their solutions for the PagerDuty Incident Analytics Dashboard.

## 🔍 Quick Diagnostics

Run these commands to diagnose most issues:

```bash
# Check Python version
python3 --version

# Check dependencies
pip list | grep -E "requests|flask|pyyaml"

# Check configuration
cat PagerDuty.yaml

# Check database
python3 main_v2.py --database-info

# Test API connection
python3 main_v2.py --update-incidents 1
```

## 🚨 Common Issues

### 1. API Authentication Errors

#### Symptom
```
❌ Error: 401 Unauthorized
```

#### Causes
- Invalid API token
- Expired API token
- Missing API token in configuration

#### Solutions

**Verify Token in Config:**
```bash
grep "^token:" PagerDuty.yaml
```

**Test Token Manually:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Accept: application/vnd.pagerduty+json;version=2" \
     "https://api.pagerduty.com/incidents?limit=1"
```

**Generate New Token:**
1. Log into PagerDuty
2. Go to **Integrations** → **API Access Keys**
3. Create new API key with **Read** permissions
4. Update `PagerDuty.yaml`:
   ```yaml
   token: your_new_token_here
   ```

---

### 2. No Incidents Found

#### Symptom
```
ℹ️ No incidents found for the specified period
```

#### Causes
- No incidents in the date range
- Service IDs incorrect
- Date range too narrow

#### Solutions

**Verify Service Configuration:**
```bash
# Check service URLs in PagerDuty.yaml
python3 main_v2.py --database-info
```

**Try Longer Period:**
```bash
# Expand to 30 days
python3 main_v2.py --update-incidents 30
```

**Check PagerDuty Web UI:**
- Confirm incidents exist in PagerDuty
- Verify service IDs are correct
- Check date ranges match

**Verify Service ID Extraction:**
```python
# Service URL should end with 7-character ID
# Correct: https://company.pagerduty.com/service-directory/PHMCGNE
# Incorrect: https://company.pagerduty.com/service-directory/
```

---

### 3. Database Locked Error

#### Symptom
```
sqlite3.OperationalError: database is locked
```

#### Causes
- Another process accessing database
- Web server running while updating
- Previous process didn't exit cleanly

#### Solutions

**Check for Running Processes:**
```bash
# Find Python processes
ps aux | grep "python.*main_v2\|python.*app_v2"

# Kill if found
kill -9 <PID>
```

**Close Web Dashboard:**
```bash
# Stop Flask app
# Press Ctrl+C in terminal running app_v2.py
```

**Wait and Retry:**
```bash
# SQLite locks are usually brief
sleep 5
python3 main_v2.py --update-incidents 7
```

**Enable WAL Mode (Advanced):**
```python
# Add to database_v2.py connection setup
connection.execute('PRAGMA journal_mode=WAL')
```

---

### 4. Slow Performance / Timeouts

#### Symptom
```
⏱️ This may take several minutes for escalation checking...
💓 Still processing... (300s elapsed)
```

#### Causes
- Large date range (30+ days)
- Many services configured
- Network latency to PagerDuty API
- Rate limiting

#### Solutions

**Use Smaller Date Ranges:**
```bash
# Instead of 30 days
python3 main_v2.py --update-incidents 30

# Try 7 days
python3 main_v2.py --update-incidents 7

# Or update incrementally
python3 main_v2.py --update-incidents 3
```

**Update One Service at a Time:**
```bash
# Much faster than all services
python3 main_v2.py --update-incidents 7 --service PHMCGNE
```

**Check Network:**
```bash
# Test connectivity
ping api.pagerduty.com

# Check latency
curl -w "Time: %{time_total}s\n" -o /dev/null -s \
  "https://api.pagerduty.com/incidents?limit=1"
```

**Optimize for Large Updates:**
- Run during off-peak hours
- Update most critical services more frequently
- Use background task scheduling

---

### 5. Missing Custom Fields Data

#### Symptom
```
CCOE Resolved: 0
Infrastructure Caused: 0
```
(When you expect some incidents to have these values)

#### Causes
- Custom fields not populated in PagerDuty
- Custom field names changed
- API not returning custom field data

#### Solutions

**Verify Single Incident:**
```bash
# Get detailed incident info
python3 main_v2.py --get-incident Q1ABCDEF

# Check if custom fields are shown
```

**Test API Directly:**
```bash
# Get custom fields for an incident
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Accept: application/vnd.pagerduty+json;version=2" \
     "https://api.pagerduty.com/incidents/INCIDENT_ID/custom_fields/values"
```

**Check Field Names:**
```python
# In pagerduty_client_v2.py, verify field names:
# - 'resolution' for CCOE
# - 'prelim_root_cause' for infrastructure
```

**Re-fetch Recent Data:**
```bash
# Force refresh
python3 main_v2.py --update-incidents 7
```

---

### 6. Web Dashboard Not Loading

#### Symptom
- Blank page
- 404 errors
- Can't connect to localhost:5003

#### Solutions

**Verify Server is Running:**
```bash
# Check if app_v2.py is running
ps aux | grep app_v2

# Check port
lsof -i :5003
```

**Start Web Server:**
```bash
cd pagerduty
python3 app_v2.py
```

**Check Logs:**
```
# Flask shows startup messages
* Running on http://127.0.0.1:5003
```

**Try Different Port:**
```python
# In app_v2.py, change port if 5003 is in use
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)
```

**Check Firewall:**
```bash
# macOS
# System Preferences → Security & Privacy → Firewall

# Linux
sudo ufw status
```

---

### 7. Calendar Not Showing Data

#### Symptom
- Calendar displays but no incident counts
- Empty cells in calendar view

#### Causes
- No data for selected month
- Service filter issue
- Date conversion issue

#### Solutions

**Check Database:**
```bash
python3 main_v2.py --database-info
```

**Verify Date Range:**
```bash
# Ensure data exists for the month you're viewing
python3 main_v2.py --show-summary 30
```

**Check Browser Console:**
```
# Open browser DevTools (F12)
# Check Console tab for JavaScript errors
# Check Network tab for failed API calls
```

**Refresh Data:**
```bash
# Update recent data
python3 main_v2.py --update-incidents 30
```

---

### 8. Incorrect Incident Counts

#### Symptom
- Web dashboard shows different counts than CLI
- Counts don't match PagerDuty web UI

#### Causes
- Timezone differences
- Date boundary issues
- Stale data

#### Solutions

**Verify Timezone:**
```python
# All dates should be UTC-7
# Check incident.created_at timestamps
```

**Compare Data Sources:**
```bash
# CLI summary
python3 main_v2.py --show-summary 7

# Check web dashboard
# Should match within timezone variance
```

**Re-sync Data:**
```bash
# Fresh pull from PagerDuty
python3 main_v2.py --update-incidents 7
```

**Check Date Filters:**
```sql
-- Test SQL directly
SELECT 
    DATE(created_at) as date,
    COUNT(*) 
FROM incidents 
GROUP BY DATE(created_at)
ORDER BY date DESC
LIMIT 10;
```

---

### 9. Dependencies Installation Issues

#### Symptom
```
ModuleNotFoundError: No module named 'requests'
```

#### Solutions

**Install Requirements:**
```bash
pip install -r requirements.txt
```

**Use Virtual Environment:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

**Check Python Path:**
```bash
which python3
which pip

# Ensure they're from same installation
```

**Manual Installation:**
```bash
pip install requests>=2.31.0
pip install pyyaml>=6.0
pip install python-dateutil>=2.8.2
pip install Flask>=2.3.0
```

---

### 10. Escalation Detection Issues

#### Symptom
```
Escalated incidents: 0
```
(When you know incidents were escalated)

#### Causes
- Log entries not checked
- Escalation log entry type changed
- API permission issue

#### Solutions

**Check Log Entries:**
```bash
# Get incident details
python3 main_v2.py --get-incident Q1ABCDEF

# Verify is_escalated flag
```

**Test API Call:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Accept: application/vnd.pagerduty+json;version=2" \
     "https://api.pagerduty.com/incidents/INCIDENT_ID/log_entries"
```

**Verify Logic:**
```python
# In pagerduty_client_v2.py
# Should check for: entry.get('type') == 'escalate_log_entry'
```

**Re-fetch Data:**
```bash
python3 main_v2.py --update-incidents 7
```

---

## 🛠️ Debugging Tools

### Enable Flask Debug Mode

```python
# In app_v2.py
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
```

**Provides:**
- Detailed error pages
- Auto-reload on code changes
- Interactive debugger

### SQLite Database Inspection

```bash
# Open database
sqlite3 pagerduty.db

# Check schema
.schema incidents

# Check data
SELECT COUNT(*) FROM incidents;
SELECT * FROM incidents LIMIT 5;

# Check date range
SELECT MIN(created_at), MAX(created_at) FROM incidents;

# Exit
.quit
```

### Check API Response

```python
# Add to pagerduty_client_v2.py for debugging
import json

response = requests.get(url, headers=headers)
print(json.dumps(response.json(), indent=2))
```

### Trace Execution

```bash
# Run with Python debugger
python3 -m pdb main_v2.py --update-incidents 7

# Set breakpoint
(Pdb) b pagerduty_client_v2:123
(Pdb) c
```

---

## 📊 Health Checks

### System Health Check Script

```bash
#!/bin/bash
# health_check.sh

echo "=== PagerDuty Dashboard Health Check ==="

echo -e "\n1. Python Version:"
python3 --version

echo -e "\n2. Dependencies:"
pip list | grep -E "requests|flask|pyyaml|dateutil"

echo -e "\n3. Configuration:"
if [ -f "PagerDuty.yaml" ]; then
    echo "✅ PagerDuty.yaml exists"
else
    echo "❌ PagerDuty.yaml missing"
fi

echo -e "\n4. Database:"
python3 main_v2.py --database-info | head -5

echo -e "\n5. API Test:"
python3 -c "
from pagerduty_client_v2 import PagerDutyAPIClient
import yaml
config = yaml.safe_load(open('PagerDuty.yaml'))
client = PagerDutyAPIClient(config['token'])
print('✅ API client initialized')
"

echo -e "\n=== Health Check Complete ==="
```

---

## 🆘 Getting Help

### Gather Information

Before seeking help, collect:

```bash
# System info
python3 --version
pip list

# Error logs
python3 main_v2.py --update-incidents 7 2>&1 | tee error.log

# Database info
python3 main_v2.py --database-info

# Configuration (sanitize token!)
cat PagerDuty.yaml | sed 's/token:.*/token: [REDACTED]/'
```

### Common Error Patterns

| Error | Quick Fix |
|-------|-----------|
| `401 Unauthorized` | Check API token |
| `database is locked` | Stop other processes |
| `No module named 'X'` | Install dependencies |
| `No incidents found` | Check date range |
| `Connection timeout` | Check network |

---

## 💡 Prevention Tips

1. **Regular Updates**: Daily small updates vs weekly large updates
2. **Monitor Logs**: Check execution logs for warnings
3. **Test Changes**: Use `--service` flag to test on one service
4. **Backup Database**: Before major updates or cleanup
5. **Version Control**: Track configuration changes
6. **Document Custom Changes**: Note any modifications to code

---

**See Also:**
- [FAQ](FAQ.md)
- [Performance Tuning](Performance.md)
- [Development Guide](Development.md)

# Frequently Asked Questions (FAQ)

Common questions and answers about the PagerDuty Incident Analytics Dashboard.

## 📋 General Questions

### What is this dashboard for?

The PagerDuty Incident Analytics Dashboard is a tool for analyzing incident data from PagerDuty. It provides:
- Historical incident tracking
- Escalation analysis
- Service-level metrics
- CCOE resolution tracking
- Infrastructure issue identification

**Primary Users:** On-call engineers, SRE teams, engineering managers, and service owners.

### Do I need PagerDuty admin access?

**No.** You only need:
- A PagerDuty account
- Ability to generate a **read-only** API token
- Access to view the services you want to monitor

### Can this replace the PagerDuty web UI?

**No.** This is a **supplementary analytics tool**, not a replacement. Use PagerDuty for:
- Incident response and management
- Creating and acknowledging incidents
- On-call scheduling

Use this dashboard for:
- Historical analysis and trends
- Escalation tracking
- Custom metrics (CCOE, infrastructure)
- Cross-service comparisons

### Is my data secure?

**Data Storage:** All data is stored locally in a SQLite database on your machine.

**API Token:** Stored in plain text in `PagerDuty.yaml` (local file only).

**Network:** Only communicates with PagerDuty API (HTTPS).

**Recommendation for Production:**
- Use environment variables for API token
- Restrict file permissions: `chmod 600 PagerDuty.yaml`
- Don't commit configuration to version control

---

## 🔧 Setup & Configuration

### How do I get a PagerDuty API token?

1. Log into PagerDuty
2. Go to **Integrations** → **API Access Keys**
3. Click **Create New API Key**
4. Description: "Incident Analytics"
5. Select **Read-only** access
6. Click **Create Key** and copy token

See [Configuration Guide](Configuration.md) for detailed steps.

### How many services can I monitor?

**Technical Limit:** No hard limit

**Practical Limits:**
- **Performance:** 20-30 services runs efficiently
- **UI:** Dashboard tabs work best with < 10 services
- **API Rate Limiting:** PagerDuty may throttle with too many requests

**Recommendation:** Start with 5-10 critical services.

### Can I monitor services from multiple PagerDuty accounts?

**Not currently.** The application supports one API token, which belongs to one PagerDuty account.

**Workaround:** Run multiple instances:
- Separate directories for each account
- Different configuration files
- Different databases

### What if I don't have custom fields configured?

The dashboard works fine without custom fields:
- **CCOE Resolved** will show 0
- **Infrastructure Caused** will show 0
- All other metrics work normally

Custom fields are **optional enhancements**.

---

## 📊 Data & Metrics

### How far back can I fetch data?

**Technical Limit:** PagerDuty API allows up to 6 months

**Recommended:**
- **Initial load:** 30 days
- **Regular updates:** 7 days
- **Maximum:** 90 days

**Performance Note:** Fetching 90+ days can take 30+ minutes.

### How often should I update data?

**Recommendations:**

| Frequency | Use Case | Command |
|-----------|----------|---------|
| **Daily** | Production monitoring | `--update-incidents 2` |
| **Weekly** | Regular tracking | `--update-incidents 7` |
| **Monthly** | Historical analysis | `--update-incidents 30` |
| **Ad-hoc** | Investigations | As needed |

**Best Practice:** Daily updates are faster than weekly.

### Why don't my counts match PagerDuty exactly?

**Common reasons:**

1. **Timezone Differences**
   - Dashboard uses UTC-7
   - PagerDuty may use different timezone
   - Date boundaries may differ

2. **Update Timing**
   - Data may be stale
   - Run `--update-incidents` to refresh

3. **Service Filters**
   - Dashboard only shows configured services
   - PagerDuty shows all services

4. **Date Range Calculation**
   - Different interpretation of "last 7 days"
   - Dashboard uses incident `created_at`

### What is "escalation" exactly?

**Definition:** An incident is escalated when:
- On-call engineer manually escalates to another team
- Automatic escalation due to timeout
- Transfer to higher level of support

**Detection:** The system checks PagerDuty log entries for `escalate_log_entry` type.

**Not Escalation:**
- Reassignment within same team
- Notes or comments
- Acknowledgment

### What is the difference between "Triggered" and "Total" incidents?

**Total Incidents:** All incidents created in the time period (any status)
- Includes: triggered, acknowledged, resolved

**Triggered Incidents:** Only incidents currently active (not resolved)
- Includes: triggered, acknowledged
- Excludes: resolved

**Example:**
- Last 7 days: 100 total incidents
- Of those: 90 resolved, 10 still triggered
- Triggered count: 10

---

## 🖥️ Web Dashboard

### Why can't I access the dashboard from another computer?

**Default:** Dashboard binds to `localhost` (127.0.0.1) only.

**To allow remote access:**
```python
# In app_v2.py
app.run(debug=True, host='0.0.0.0', port=5003)
```

**Security Warning:** This exposes dashboard to network. Add authentication if needed.

### Can I change the port?

**Yes.** Edit `app_v2.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

Then access at: `http://localhost:8080`

### Why is the calendar empty?

**Common causes:**

1. **No data for that month**
   - Check: `python3 main_v2.py --database-info`
   - Solution: Update data for that month

2. **Wrong service selected**
   - Check: Switch to different service tab

3. **Date range issue**
   - Solution: Navigate to current month

### How do I see incident details?

**Calendar View:**
- Hover over red escalated badge
- Popup shows incident title and link
- Click link to open in PagerDuty

**Command Line:**
```bash
python3 main_v2.py --get-incident Q1ABCDEF
```

---

## 🛠️ Operations

### How long does an update take?

**Depends on:**
- Number of services
- Number of days
- Number of incidents
- Network speed

**Typical Times:**

| Scenario | Duration |
|----------|----------|
| 1 service, 7 days, ~50 incidents | 1-2 minutes |
| 6 services, 7 days, ~300 incidents | 4-6 minutes |
| 6 services, 30 days, ~1000 incidents | 15-25 minutes |

**Why so long?**
- API call for each incident's log entries
- API call for each incident's custom fields
- Rate limiting by PagerDuty
- Network latency

### Can I run updates in the background?

**Yes, using screen or tmux:**

```bash
# Using screen
screen -S pagerduty
python3 main_v2.py --update-incidents 30
# Press Ctrl+A then D to detach

# Reattach later
screen -r pagerduty
```

**Or use nohup:**
```bash
nohup python3 main_v2.py --update-incidents 30 > update.log 2>&1 &
```

### How do I automate daily updates?

**Using cron:**

```bash
# Edit crontab
crontab -e

# Add line (daily at 9 AM)
0 9 * * * cd /path/to/pagerduty && python3 main_v2.py --update-incidents 2
```

**Or create a script:**
```bash
#!/bin/bash
# daily_update.sh
cd /path/to/pagerduty
python3 main_v2.py --update-incidents 2
```

Make executable and schedule:
```bash
chmod +x daily_update.sh
```

### What happens if update is interrupted?

**Good news:** All processed incidents are saved immediately.

**Behavior:**
- Press Ctrl+C: Graceful shutdown, data saved
- Network timeout: Partial data saved
- System crash: Data saved up to last batch

**Recovery:** Simply run update again. The system is idempotent (safe to run multiple times).

---

## 🐛 Troubleshooting

### "No module named 'requests'" error

**Solution:**
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install requests pyyaml python-dateutil Flask
```

### "Database is locked" error

**Cause:** Another process is using the database.

**Solutions:**
1. Stop web dashboard: Press Ctrl+C in terminal running `app_v2.py`
2. Kill other processes: `ps aux | grep python` then `kill PID`
3. Wait a few seconds and retry

### "401 Unauthorized" error

**Cause:** Invalid or expired API token.

**Solutions:**
1. Check token in `PagerDuty.yaml`
2. Generate new token in PagerDuty
3. Verify token has read permissions

### Web dashboard shows "Error loading data"

**Solutions:**
1. **Check browser console:** Press F12, check Console tab
2. **Verify server is running:** Terminal should show Flask startup messages
3. **Check API endpoint:** Open `http://localhost:5003/api/services` in browser
4. **Update data:** Run `python3 main_v2.py --update-incidents 7`

---

## 📈 Advanced Usage

### Can I export data to CSV/Excel?

**Not built-in**, but you can query the database:

```bash
# Export to CSV
sqlite3 -header -csv pagerduty.db "SELECT * FROM incidents" > incidents.csv

# Export specific query
sqlite3 -header -csv pagerduty.db \
  "SELECT service_name, status, created_at FROM incidents 
   WHERE is_escalated = 1" > escalations.csv
```

### Can I integrate with other tools?

**Yes.** The Flask API can be called by other applications:

```bash
# Get service summary
curl http://localhost:5003/api/service/PHMCGNE/summary?days=7

# Get calendar data
curl http://localhost:5003/api/service/PHMCGNE/calendar?year=2025&month=10
```

**API Documentation:** See [API Reference](API-Reference.md)

### Can I add custom metrics?

**Yes.** Requires code changes:

1. **Database:** Add column to `incidents` table
2. **API Client:** Extract custom field
3. **Analytics:** Add SQL query for metric
4. **Web UI:** Display in dashboard

See [Development Guide](Development.md) for details.

### Can I change the timezone?

**Yes**, but requires code changes in:
- `pagerduty_client_v2.py`
- `app_v2.py`
- Any date-handling code

See [Configuration Guide](Configuration.md#timezone-configuration)

---

## 💾 Data Management

### How much disk space does it use?

**Typical Usage:**
- **Database:** ~500-800 bytes per incident
- **50,000 incidents:** ~40 MB
- **100,000 incidents:** ~80 MB

**Plus:**
- Application files: ~1 MB
- Dependencies: ~50 MB

### How do I backup my data?

**Database Backup:**
```bash
# Simple copy
cp pagerduty.db pagerduty.db.backup

# With date
cp pagerduty.db pagerduty.db.$(date +%Y%m%d)

# SQLite backup
sqlite3 pagerduty.db ".backup pagerduty.db.backup"
```

**Configuration Backup:**
```bash
cp PagerDuty.yaml PagerDuty.yaml.backup
```

**Automated Backup:**
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d)
cp pagerduty.db "$BACKUP_DIR/pagerduty.db.$DATE"
```

### How do I restore from backup?

```bash
# Stop all processes first
# Then restore
cp pagerduty.db.backup pagerduty.db
```

### Should I clean up old data?

**Recommendations:**
- **Keep:** 60-90 days of data
- **Frequency:** Monthly cleanup
- **Command:** `python3 main_v2.py --cleanup 90`

**Benefits:**
- Faster queries
- Less disk space
- Better performance

**Warning:** Cleanup permanently deletes data!

---

## 🚀 Performance

### Why is the initial update so slow?

**Reasons:**
1. **Many API calls:** Each incident requires 2-3 API calls
2. **Rate limiting:** PagerDuty throttles requests
3. **Network latency:** External API calls
4. **Data volume:** Processing hundreds/thousands of incidents

**Tips:**
- Start with shorter date ranges (3-5 days)
- Update one service first to test
- Run during off-peak hours
- Subsequent updates are faster (only new data)

### How can I make it faster?

**Optimization Strategies:**

1. **Update frequently:** Daily updates are faster than weekly
2. **Target specific services:** Use `--service` flag
3. **Shorter date ranges:** 7 days vs 30 days
4. **Network optimization:** Use wired connection, not WiFi
5. **Database maintenance:** Regular cleanup and VACUUM

### Can multiple people use it simultaneously?

**Current Limitation:** SQLite has single-writer limitation.

**Workarounds:**
1. **Read-only access:** Multiple people can view web dashboard
2. **Separate databases:** Each user runs their own instance
3. **Upgrade to PostgreSQL:** For production multi-user deployment

---

**See Also:**
- [Troubleshooting Guide](Troubleshooting.md)
- [Quick Start Guide](Quick-Start.md)
- [Configuration Guide](Configuration.md)

# Quick Start Guide

Get started with the PagerDuty Incident Analytics Dashboard in minutes!

## ⚡ 5-Minute Setup

### Prerequisites Check

Before you begin, ensure you have:
- ✅ Python 3.8 or higher installed
- ✅ PagerDuty account with API access
- ✅ Network access to PagerDuty API endpoints

```bash
# Check Python version
python3 --version
```

### Step 1: Install Dependencies

```bash
cd /Users/yaya/Documents/workspace/claude-demo/pagerduty
pip install -r requirements.txt
```

### Step 2: Configure PagerDuty

Edit `PagerDuty.yaml` with your API token and services:

```yaml
token: your_pagerduty_api_token_here
services:
  - name: Your Service Name
    url: https://your-company.pagerduty.com/service-directory/SERVICE_ID
```

**How to get your API token:**
1. Log into PagerDuty
2. Go to **Integrations** → **API Access Keys**
3. Create a new API key with **Read** permissions
4. Copy the token into `PagerDuty.yaml`

### Step 3: Fetch Initial Data

```bash
# Fetch incidents from the last 7 days
python3 main_v2.py --update-incidents 7
```

This will:
- ✅ Connect to PagerDuty API
- ✅ Fetch incidents for all configured services
- ✅ Analyze escalations from log entries
- ✅ Extract custom fields (CCOE resolution, infrastructure cause)
- ✅ Store data in SQLite database

**Expected output:**
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

### Step 4: View Summary

```bash
# Show incident summary
python3 main_v2.py --show-summary
```

**Expected output:**
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
```

### Step 5: Launch Web Dashboard

```bash
python3 app_v2.py
```

Open your browser to: **http://localhost:5003/**

You'll see:
- 📊 Service tabs for each configured service
- 📅 Calendar view with daily incident counts
- 📈 Trend charts for 7-day or 30-day periods
- 🎯 Summary metrics cards

## 🎉 You're Ready!

That's it! You now have a fully functional incident analytics dashboard.

## 🔄 Daily Workflow

### Update Data (Run Daily or As Needed)

```bash
# Update last 7 days of data
python3 main_v2.py --update-incidents 7

# Or use the web admin panel
# Navigate to http://localhost:5003/admin
```

### View Reports

**Command Line:**
```bash
# Summary for last 7 days
python3 main_v2.py --show-summary

# Summary for last 30 days
python3 main_v2.py --show-summary 30

# Show escalated incidents only
python3 main_v2.py --show-escalations
```

**Web Dashboard:**
- Open http://localhost:5003/
- Click on service tabs
- Toggle between 7-day and 30-day views
- Hover over escalated badges for incident details

## 📚 Next Steps

Now that you're up and running, explore:

- **[Web Dashboard Guide](Web-Dashboard.md)** - Learn all dashboard features
- **[CLI Guide](CLI-Guide.md)** - Master command-line operations
- **[Metrics Guide](Metrics-Guide.md)** - Understand all metrics
- **[Configuration Guide](Configuration.md)** - Advanced configuration options

## ⚠️ Common First-Time Issues

### API Token Invalid
**Error:** `❌ Error: 401 Unauthorized`

**Solution:** 
- Verify your API token in `PagerDuty.yaml`
- Ensure the token has **Read** permissions
- Check token hasn't expired

### No Incidents Found
**Error:** `ℹ️ No incidents found for the specified period`

**Solution:**
- Check date range - try longer period (e.g., 30 days)
- Verify service IDs are correct in `PagerDuty.yaml`
- Confirm services have incidents in PagerDuty

### Slow Performance
**Issue:** Initial update takes a long time

**Explanation:** This is normal! The system:
- Fetches detailed incident data
- Makes additional API calls for log entries and custom fields
- First run for 7 days typically takes 3-5 minutes

**Tips:**
- Start with fewer days (3-4 days)
- Update one service at a time: `--update-incidents 7 --service SERVICE_ID`
- Subsequent updates are faster (only new/changed incidents)

### Database Errors
**Error:** `database is locked`

**Solution:**
- Ensure no other processes are accessing the database
- Close the web dashboard if running
- Wait a few seconds and try again

## 🔧 Quick Commands Reference

```bash
# Update incidents
python3 main_v2.py --update-incidents 7                    # All services, 7 days
python3 main_v2.py --update-incidents 7 --service PHMCGNE  # Specific service

# View summaries
python3 main_v2.py --show-summary                          # 7-day summary
python3 main_v2.py --show-summary 30                       # 30-day summary
python3 main_v2.py --show-escalations                      # Escalated incidents

# Database operations
python3 main_v2.py --database-info                         # Show DB stats
python3 main_v2.py --cleanup 60                            # Remove data older than 60 days
python3 main_v2.py --get-incident Q1ABC123DEF              # Get incident details

# Web dashboard
python3 app_v2.py                                          # Start web server
```

## 💡 Pro Tips

1. **Schedule Daily Updates**: Add to cron to run automatically
   ```bash
   0 9 * * * cd /path/to/pagerduty && python3 main_v2.py --update-incidents 7
   ```

2. **Keep Web Server Running**: Use `screen` or `tmux` for persistent sessions
   ```bash
   screen -S pagerduty
   python3 app_v2.py
   # Press Ctrl+A then D to detach
   ```

3. **Focus on Specific Services**: Update only the services you care about most frequently

4. **Use Admin Panel**: Easier than command line for routine updates

5. **Monitor Escalation Rates**: Track trends over time to identify problem areas

---

**Need Help?** Check the [Troubleshooting Guide](Troubleshooting.md) or [FAQ](FAQ.md)

# Configuration Guide

Complete guide to configuring the PagerDuty Incident Analytics Dashboard.

## 📁 Configuration Files

### PagerDuty.yaml

The main configuration file containing API credentials and service definitions.

**Location:** `/Users/yaya/Documents/workspace/claude-demo/pagerduty/PagerDuty.yaml`

## 🔧 Basic Configuration

### Minimal Configuration

```yaml
token: your_pagerduty_api_token_here
services:
  - name: My Service
    url: https://your-company.pagerduty.com/service-directory/SERVICE_ID
```

### Complete Configuration Example

```yaml
token: u+61MTPh5pwWQ6r-My4Q
services:
  - name: 9647 - Touchstone Reporting Support Service
    url: https://ebay-cpt.pagerduty.com/service-directory/PVT5IW4
  - name: 9664 - Touchstone On Call Service
    url: https://ebay-cpt.pagerduty.com/service-directory/PY23FJQ
  - name: 1690 - Sojourner SLA Service
    url: https://ebay-cpt.pagerduty.com/service-directory/PHMCGNE
  - name: Customer Journey Signals
    url: https://ebay-cpt.pagerduty.com/service-directory/P0CAL62
  - name: 1092 - Tracking CCOE High Priority
    url: https://ebay-cpt.pagerduty.com/service-directory/PHZ57RZ
  - name: Product Analytics
    url: https://ebay-cpt.pagerduty.com/service-directory/PJFLEB2
```

## 🔑 API Token Configuration

### Getting Your API Token

1. **Login to PagerDuty**
   - Navigate to your PagerDuty account
   - URL format: `https://your-company.pagerduty.com`

2. **Access API Keys**
   - Click your profile icon (top right)
   - Select **Integrations** → **API Access Keys**
   - Or navigate directly to: `https://your-company.pagerduty.com/api_keys`

3. **Create New API Key**
   - Click **Create New API Key**
   - Description: "Incident Analytics Dashboard"
   - Permissions: **Read-only** access (recommended)
   - Click **Create Key**

4. **Copy Token**
   - Copy the generated token immediately
   - **Important:** Token is only shown once!
   - Format: Alphanumeric string (e.g., `u+61MTPh5pwWQ6r-My4Q`)

5. **Add to Configuration**
   ```yaml
   token: YOUR_COPIED_TOKEN_HERE
   ```

### Token Permissions

**Required Permissions:**
- ✅ Read incidents
- ✅ Read services
- ✅ Read log entries
- ✅ Read custom fields

**Not Required:**
- ❌ Write/Update permissions
- ❌ Delete permissions
- ❌ Admin permissions

### Token Security

**Best Practices:**
- 🔒 Keep token confidential
- 🔄 Rotate tokens periodically (every 6 months)
- 📝 Use descriptive token names
- 🚫 Never commit tokens to version control

**Production Deployment:**
```bash
# Use environment variable instead
export PAGERDUTY_API_TOKEN="your_token_here"
```

```python
# Modify config_loader.py to read from environment
import os
token = os.getenv('PAGERDUTY_API_TOKEN', config.get('token'))
```

## 🎯 Service Configuration

### Service URL Format

PagerDuty service URLs follow this pattern:
```
https://YOUR-COMPANY.pagerduty.com/service-directory/SERVICE_ID
```

**Components:**
- `YOUR-COMPANY`: Your PagerDuty subdomain
- `SERVICE_ID`: 7-character service identifier (e.g., `PHMCGNE`)

### Finding Service IDs

#### Method 1: PagerDuty Web UI

1. Navigate to **Services** → **Service Directory**
2. Click on desired service
3. Check URL: `https://company.pagerduty.com/service-directory/PHMCGNE`
4. Service ID is the last 7 characters: `PHMCGNE`

#### Method 2: Browser Inspection

1. Open PagerDuty service page
2. Right-click → Inspect Element
3. Look for service ID in HTML attributes
4. Example: `data-service-id="PHMCGNE"`

#### Method 3: API Call

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Accept: application/vnd.pagerduty+json;version=2" \
     "https://api.pagerduty.com/services" | jq '.services[] | {id, name}'
```

### Service Name Guidelines

**Recommended Format:**
```yaml
- name: "[Ticket Number] - Descriptive Service Name"
  url: https://...
```

**Examples:**
```yaml
- name: 9647 - Touchstone Reporting Support Service
- name: 1690 - Sojourner SLA Service
- name: Customer Journey Signals
```

**Benefits:**
- Easy identification in reports
- Ticket number reference
- Consistent naming

### Adding New Services

1. **Get Service Details:**
   - Service name from PagerDuty
   - Service URL with ID

2. **Add to Configuration:**
   ```yaml
   services:
     # ... existing services ...
     - name: New Service Name
       url: https://your-company.pagerduty.com/service-directory/NEW_ID
   ```

3. **Verify Configuration:**
   ```bash
   python3 main_v2.py --database-info
   ```

4. **Fetch Initial Data:**
   ```bash
   python3 main_v2.py --update-incidents 7 --service NEW_ID
   ```

### Removing Services

1. **Delete from Configuration:**
   - Remove service entry from `PagerDuty.yaml`

2. **Data Handling:**
   - Historical data remains in database
   - New updates won't fetch this service
   - Manually cleanup if needed:
     ```sql
     DELETE FROM incidents WHERE service_id = 'OLD_ID';
     ```

## ⚙️ Advanced Configuration

### Multiple Configuration Files

For different environments:

**Development:**
```yaml
# PagerDuty.dev.yaml
token: dev_token_here
services:
  - name: Test Service
    url: https://company.pagerduty.com/service-directory/TESTID
```

**Production:**
```yaml
# PagerDuty.prod.yaml
token: prod_token_here
services:
  - name: Production Service
    url: https://company.pagerduty.com/service-directory/PRODID
```

**Usage:**
```python
# Modify config_loader.py
import sys
env = sys.argv[1] if len(sys.argv) > 1 else 'dev'
config_file = f'PagerDuty.{env}.yaml'
```

### Service Groups

Organize services by team or function:

```yaml
token: your_token

# Analytics Team Services
services:
  - name: Sojourner SLA Service
    url: https://ebay-cpt.pagerduty.com/service-directory/PHMCGNE
  - name: Customer Journey Signals
    url: https://ebay-cpt.pagerduty.com/service-directory/P0CAL62

# Platform Team Services  
  - name: Product Analytics
    url: https://ebay-cpt.pagerduty.com/service-directory/PJFLEB2
```

### Custom Fields Configuration

Custom fields are automatically detected, but you can document expected fields:

```yaml
token: your_token
services:
  - name: My Service
    url: https://...

# Documentation (not parsed by application)
custom_fields:
  resolution:
    description: "Resolution team (ccoe, team, etc.)"
    values: ["ccoe", "team", "self-service"]
  prelim_root_cause:
    description: "Infrastructure component causing issue"
    values: ["rheos", "hadoop", "tess", "hbase", "kafka"]
```

## 🌐 Network Configuration

### Proxy Configuration

If behind corporate proxy:

```python
# Add to pagerduty_client_v2.py
import os

proxies = {
    'http': os.getenv('HTTP_PROXY'),
    'https': os.getenv('HTTPS_PROXY')
}

response = requests.get(url, headers=headers, proxies=proxies)
```

**Environment Variables:**
```bash
export HTTP_PROXY="http://proxy.company.com:8080"
export HTTPS_PROXY="http://proxy.company.com:8080"
```

### SSL Certificate

For custom SSL certificates:

```python
# Add to pagerduty_client_v2.py
cert_path = "/path/to/nscacert_combined.pem"
response = requests.get(url, headers=headers, verify=cert_path)
```

### Timeout Configuration

**Default Timeouts:**
- Connection timeout: 30 seconds
- Read timeout: 60 seconds

**Custom Timeouts:**
```python
# In pagerduty_client_v2.py
timeout = (30, 120)  # (connect, read)
response = requests.get(url, headers=headers, timeout=timeout)
```

## 🗄️ Database Configuration

### Database Location

**Default:** `pagerduty.db` in the application directory

**Custom Location:**
```python
# In database_v2.py
class IncidentDatabase:
    def __init__(self, db_path='custom/path/pagerduty.db'):
        self.db_path = db_path
```

### Database Settings

**SQLite PRAGMA Settings:**
```python
# In database_v2.py connection setup
connection.execute('PRAGMA journal_mode=WAL')      # Better concurrency
connection.execute('PRAGMA synchronous=NORMAL')    # Faster writes
connection.execute('PRAGMA cache_size=10000')      # More cache
connection.execute('PRAGMA temp_store=MEMORY')     # Memory temp tables
```

## 🌍 Timezone Configuration

### Current Setting

**Timezone:** UTC-7 (Pacific Time)

**Location:** Hardcoded in `pagerduty_client_v2.py` and `app_v2.py`

### Changing Timezone

```python
# In pagerduty_client_v2.py
from datetime import timezone, timedelta

# Change from UTC-7 to UTC-5 (Eastern)
UTC_MINUS_7 = timezone(timedelta(hours=-5))
```

**Files to Update:**
- `pagerduty_client_v2.py`
- `app_v2.py`
- `database_v2.py` (if timezone-specific queries)

## 🖥️ Web Server Configuration

### Port Configuration

**Default Port:** 5003

**Change Port:**
```python
# In app_v2.py
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
```

### Debug Mode

**Development:**
```python
app.run(debug=True, host='0.0.0.0', port=5003)
```

**Production:**
```python
app.run(debug=False, host='127.0.0.1', port=5003)
```

### Host Binding

**Localhost Only (Secure):**
```python
app.run(host='127.0.0.1', port=5003)
```

**All Interfaces (For Remote Access):**
```python
app.run(host='0.0.0.0', port=5003)
```

## 📝 Configuration Validation

### Validation Script

```python
#!/usr/bin/env python3
# validate_config.py

import yaml
import re
import sys

def validate_config():
    try:
        with open('PagerDuty.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check token
        if 'token' not in config:
            print("❌ Missing 'token' in configuration")
            return False
        
        if not config['token']:
            print("❌ Token is empty")
            return False
        
        # Check services
        if 'services' not in config:
            print("❌ Missing 'services' in configuration")
            return False
        
        if not config['services']:
            print("❌ No services configured")
            return False
        
        # Validate each service
        for i, service in enumerate(config['services']):
            if 'name' not in service:
                print(f"❌ Service {i} missing 'name'")
                return False
            
            if 'url' not in service:
                print(f"❌ Service {i} ({service['name']}) missing 'url'")
                return False
            
            # Validate URL format
            if not re.search(r'/service-directory/[A-Z0-9]{7}$', service['url']):
                print(f"⚠️ Service {i} ({service['name']}) URL may be invalid")
                print(f"   Expected format: .../service-directory/XXXXXXX")
        
        print(f"✅ Configuration valid")
        print(f"   Token: {'*' * 20}")
        print(f"   Services: {len(config['services'])}")
        return True
        
    except FileNotFoundError:
        print("❌ PagerDuty.yaml not found")
        return False
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        return False

if __name__ == '__main__':
    sys.exit(0 if validate_config() else 1)
```

**Run Validation:**
```bash
python3 validate_config.py
```

## 🔄 Configuration Best Practices

### 1. Version Control

**Do Commit:**
- `PagerDuty.yaml.template` (without token)
- Configuration documentation

**Don't Commit:**
- `PagerDuty.yaml` (contains sensitive token)

**Template Example:**
```yaml
# PagerDuty.yaml.template
token: YOUR_API_TOKEN_HERE
services:
  - name: Service Name
    url: https://your-company.pagerduty.com/service-directory/SERVICE_ID
```

### 2. Documentation

Document in `PagerDuty.yaml` with comments:

```yaml
# PagerDuty API Token
# Generated: 2025-10-20
# Permissions: Read-only
# Expires: Never (rotate every 6 months)
token: your_token_here

# Services monitored by this dashboard
services:
  # Analytics Team
  - name: Sojourner SLA Service
    url: https://ebay-cpt.pagerduty.com/service-directory/PHMCGNE
    # Team: Data Analytics
    # On-call: @analytics-oncall
```

### 3. Regular Audits

**Monthly Review:**
- ✅ Verify token is still valid
- ✅ Check services list is current
- ✅ Remove decommissioned services
- ✅ Add new services

### 4. Backup

```bash
# Backup configuration
cp PagerDuty.yaml PagerDuty.yaml.backup.$(date +%Y%m%d)

# Backup before changes
cp PagerDuty.yaml PagerDuty.yaml.before-change
```

---

**See Also:**
- [Quick Start Guide](Quick-Start.md)
- [Installation Guide](Installation.md)
- [Troubleshooting](Troubleshooting.md)

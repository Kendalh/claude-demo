# PagerDuty Incident Analytics Dashboard v2

A comprehensive incident management and analytics system that integrates with PagerDuty to provide detailed incident tracking, escalation analysis, CCOE resolution monitoring, and infrastructure issue identification.

## 🚀 Features

### Core Functionality
- **Incident Data Collection**: Automatically fetches incidents from PagerDuty API with custom fields
- **Escalation Detection**: Analyzes log entries to identify truly escalated incidents
- **CCOE Resolution Tracking**: Identifies incidents resolved by CCOE teams
- **Infrastructure Issue Analysis**: Tracks incidents caused by infrastructure problems
- **Web Dashboard**: Interactive Bootstrap 5 UI with charts and calendar views
- **Database Storage**: SQLite database with efficient querying and analytics

### Analytics & Metrics
- **Service-Level Metrics**: Per-service incident analysis and trends
- **Calendar Views**: Daily incident counts with visual indicators
- **Trend Charts**: Historical data visualization using Chart.js
- **Summary Statistics**: 7-day and 30-day summary reports
- **Escalation Analysis**: Detailed escalation tracking and reporting

### Advanced Features
- **Custom Fields Integration**: Extracts resolution type and root cause data
- **Batch Processing**: Efficient API calls with retry logic and timeout handling
- **Real-time Updates**: Live dashboard updates with fresh data
- **Admin Interface**: Data management and system monitoring tools

## 📋 Prerequisites

- Python 3.8 or higher
- PagerDuty API access token
- Network access to PagerDuty API endpoints

## 🛠️ Setup & Installation

### 1. Environment Setup

```bash
# Clone or download the application files
cd pagerduty

# Install required Python packages
pip install requests flask pyyaml sqlite3
```

### 2. Configuration

Create a `PagerDuty.yaml` configuration file:

```yaml
token: your_pagerduty_api_token_here
services:
  - name: Service Name 1
    url: https://your-company.pagerduty.com/service-directory/SERVICE_ID_1
  - name: Service Name 2
    url: https://your-company.pagerduty.com/service-directory/SERVICE_ID_2
  # Add more services as needed
```

**Important**: Replace `your_pagerduty_api_token_here` with your actual PagerDuty API token and update the service URLs with your organization's services.

### 3. Database Initialization

The database will be automatically created on first run. No manual setup required.

## 💻 Command Line Usage

### Core Commands

#### Update Incident Data
```bash
# Update incidents for the last 7 days (all services)
python3 main_v2.py --update-incidents 7

# Update incidents for the last 30 days (all services)
python3 main_v2.py --update-incidents 30

# Update specific service for the last 7 days
python3 main_v2.py --update-incidents 7 --service PHMCGNE

# Update specific service for the last 14 days
python3 main_v2.py --update-incidents 14 --service P0CAL62
```

#### View Analytics
```bash
# Show 7-day summary (default)
python3 main_v2.py --show-summary

# Show 14-day summary
python3 main_v2.py --show-summary 14

# Show escalated incidents for last 7 days
python3 main_v2.py --show-escalations

# Show escalated incidents for last 30 days
python3 main_v2.py --show-escalations 30
```

#### Database Management
```bash
# Show database information and statistics
python3 main_v2.py --database-info

# Clean up incidents older than 60 days
python3 main_v2.py --cleanup 60

# Get details for a specific incident
python3 main_v2.py --get-incident Q1ABC123DEF
```

#### Targeted Updates
```bash
# Update specific service for a specific date
python3 main_v2.py --update-service PHMCGNE --date 2025-08-20

# Available service IDs are shown in --database-info
```

### Web Dashboard

Start the web application:
```bash
python3 app_v2.py
```

Access the dashboard at:
- **Main Dashboard**: http://localhost:5003/
- **Admin Panel**: http://localhost:5003/admin

## 🎯 Key Metrics Tracked

### Standard Incident Metrics
- **Total Incidents**: All incidents in the specified time period
- **Triggered Incidents**: Currently active (triggered/acknowledged) incidents
- **Resolved Incidents**: Successfully resolved incidents
- **Escalated Incidents**: Incidents that required escalation (via log entries analysis)
- **CCOE Resolved**: Incidents resolved by CCOE teams (custom field: resolution = "ccoe")
- **Infrastructure Caused**: Incidents caused by infrastructure issues (custom field: prelim_root_cause has value)

## 🖥️ Web Dashboard Features

### Service Tabs
- Individual tabs for each configured service
- Service-specific metrics and trends
- Interactive period selection (7-day vs 30-day views)

### Calendar View
- Daily incident counts with color-coded indicators
- Hover popups for escalated incidents with PagerDuty links
- Visual badges for different incident types:
  - **Blue**: Total incidents
  - **Orange**: Triggered incidents  
  - **Green**: Resolved incidents
  - **Red**: Escalated incidents (with "!" indicator)
  - **Cyan**: CCOE resolved (with "C" indicator)
  - **Gray**: Infrastructure caused (with "I" indicator)

### Trend Charts
- Interactive Chart.js visualizations
- Multi-line charts showing all metric trends over time
- Responsive design for mobile and desktop

### Admin Panel
- Real-time data updates with progress tracking
- System statistics and health monitoring
- Database management tools

## 🔧 Architecture

### Components
- **main_v2.py**: Command-line interface and core operations
- **app_v2.py**: Flask web application and API endpoints
- **pagerduty_client_v2.py**: PagerDuty API client with custom fields support
- **database_v2.py**: SQLite database operations and schema management
- **analytics_v2.py**: SQL-based analytics and metrics calculation
- **incident_v2.py**: Data transfer object for incident representation

### Data Flow
1. **Collection**: API client fetches incidents + custom fields from PagerDuty
2. **Processing**: Escalation analysis via log entries + custom fields parsing
3. **Storage**: Structured data stored in SQLite with proper indexing
4. **Analytics**: SQL queries generate metrics across time periods
5. **Visualization**: Web UI displays interactive charts and calendars

## 🕐 Timezone Handling

All operations use **UTC-7** timezone for consistency:
- Incident dates are converted to UTC-7 for local analysis
- Database stores incidents with proper timezone conversion
- Web dashboard displays times in UTC-7 format

## 🔍 Troubleshooting

### Common Issues

**API Timeout Errors**:
- Reduce the number of days in update commands
- Use targeted service updates for large datasets
- Check network connectivity to PagerDuty API

**Missing Custom Fields Data**:
- Verify incidents have custom fields populated in PagerDuty
- Use `--get-incident` command to inspect specific incident data
- Run `--update-service` for targeted updates with fixed parsing

**Database Issues**:
- Run `--database-info` to check database status
- Use `--cleanup` to remove old data and free space
- Database auto-migrates schema changes on startup

### Performance Tips
- Use specific date ranges for large data updates
- Run regular cleanup to maintain database performance
- Monitor system resources during large API operations

## 📊 Sample Output

### Command Line Summary
```
📊 Incident Summary (Last 7 Days)
=====================================
Total Incidents: 258
Triggered: 45
Resolved: 195
Escalated: 21
CCOE Resolved: 12
Infrastructure Caused: 8
Escalation Rate: 8.1%
```

### Web Dashboard
The web interface provides:
- Real-time metrics cards with current counts
- Interactive service tabs with individual analytics
- Calendar grid showing daily incident distribution
- Trend charts with multi-metric visualization
- Admin tools for data management

## 🤝 Contributing

When extending the application:
1. Follow the existing architecture patterns
2. Update database schema in `database_v2.py` with migration logic
3. Add corresponding analytics methods in `analytics_v2.py`
4. Update API endpoints in `app_v2.py` for web access
5. Enhance UI templates for new visualizations

## 📝 License

This application is designed for internal incident management and analytics purposes.
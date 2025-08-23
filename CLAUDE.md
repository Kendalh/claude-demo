# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **PagerDuty Incident Analytics Dashboard** - a Python-based system that integrates with PagerDuty's API to provide comprehensive incident tracking, escalation analysis, and custom field processing. The system stores data in SQLite and presents it through a Flask web application with interactive dashboards.

## Essential Commands

### Development Environment Setup
```bash
cd pagerduty/
pip3 install -r requirements.txt
```

### Core Application Commands
```bash
# Update incident data (primary operation)
python3 main_v2.py --update-incidents 7                    # Last 7 days, all services
python3 main_v2.py --update-service PHMCGNE --date 2025-8-18  # Specific service/date
./run_update_v2.sh 7                                       # Background update with monitoring

# Analytics and reporting
python3 main_v2.py --show-summary                          # 7-day summary
python3 main_v2.py --show-escalations 30                   # Escalated incidents
python3 main_v2.py --database-info                         # Database statistics

# Web dashboard
python3 app_v2.py                                          # Start web server (port 5003)
```

### Database Management
```bash
python3 main_v2.py --cleanup 60                            # Remove incidents older than 60 days
python3 main_v2.py --get-incident Q1ABC123DEF              # Inspect specific incident
```

## Architecture Overview

### Core Components & Data Flow
```
PagerDuty API → Client Layer → Database Layer → Analytics Layer → Web UI
```

**Key Files:**
- `main_v2.py` - CLI interface and orchestration
- `pagerduty_client_v2.py` - API client with custom fields parsing. All the PagerDuty API integrations should be in this file.
- `database_v2.py` - SQLite operations with UTC-7 timezone handling
- `analytics_v2.py` - SQL-based metrics calculation
- `app_v2.py` - Flask web application and REST API
- `incident_v2.py` - Data transfer object (pure data class)
- `test folder` - All the unit test cases

### Critical Design Patterns

**Timezone Handling**: All timestamps are converted to UTC-7 at ingestion time and stored in local timezone. Database queries work directly with stored timestamps without conversion.

**Custom Fields Processing**: 
- Resolution field: `'ccoe'` value determines `resolved_by_ccoe` boolean
- Root cause field: Any value determines `caused_by_infra` string

**Escalation Detection**: Analyzes PagerDuty log entries for `'escalate_log_entry'` type rather than relying on status fields.

**Batch Processing**: API calls are batched (20 incidents) with retry logic and timeout handling to prevent API throttling.

## Configuration Requirements

### PagerDuty.yaml Structure
```yaml
token: your_pagerduty_api_token
services:
  - name: Service Display Name
    url: https://company.pagerduty.com/service-directory/SERVICE_ID
```

Service IDs are extracted from URLs using regex pattern: `/([A-Z0-9]{7})$/`

## Database Schema Key Points

**incidents table** stores all data with these critical fields:
- `resolved_by_ccoe: BOOLEAN` - Derived from custom field `resolution = 'ccoe'`
- `caused_by_infra: TEXT` - Stores `prelim_root_cause` custom field value
- `is_escalated: BOOLEAN` - Determined by log entry analysis
- All timestamps stored in UTC-7 format as ISO strings

**Indexes** exist on: `service_id + created_at`, `status`, `is_escalated`, `DATE(created_at)`

## Web Application Structure

### API Endpoints
- `/api/service/<id>/summary?days=X` - Service metrics for period
- `/api/service/<id>/calendar?year=Y&month=M` - Calendar data
- `/api/service/<id>/trends?days=X` - Time series data
- `/api/admin/update` - Trigger data updates

### Frontend Components
- Service tabs with individual analytics
- Bootstrap 5 responsive design with 6-column metrics layout
- Chart.js for trend visualization
- Custom calendar grid with escalation popups

## Development Patterns 
Make sure when you add features, make according changes to the unit test cases and README file. Run the unit tests cases and fix the failure ones. 
Don't overwelming the README, just add major features and make it concise. 

### Error Handling
- All API calls include retry logic with exponential backoff
- Graceful degradation when custom fields are missing
- Signal handlers for clean shutdown during long operations

### Data Processing Pipeline
1. **Fetch**: API client retrieves incidents + custom fields + log entries
2. **Transform**: Convert timestamps, parse custom fields, detect escalations
3. **Store**: Batch insert with UTC-7 conversion
4. **Query**: SQL aggregations for metrics
5. **Present**: JSON API + HTML dashboard

### Testing Approach
Use `--get-incident INCIDENT_ID` to inspect individual incident processing and verify custom field parsing. 

## Performance Considerations

- Use `--update-service` for targeted updates instead of full refreshes
- Monitor `run_update_v2.sh` background process via `update_log.txt`
- Regular cleanup recommended for large datasets
- SQLite handles concurrent reads well but limit concurrent writes

## Common Issues & Solutions

**API Timeouts**: Reduce batch size or use service-specific updates for large datasets.

**Missing Escalation Data**: Escalations determined by log entries, not incident status. Use targeted date ranges if missing.

**Timezone Misalignment**: All date operations must account for UTC-7 storage format. Use `DATE(created_at)` for date filtering.
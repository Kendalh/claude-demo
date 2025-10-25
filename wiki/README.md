# PagerDuty Incident Analytics Dashboard - Repository Wiki

Welcome to the complete documentation for the PagerDuty Incident Analytics Dashboard project!

## 📚 Documentation Index

This wiki contains comprehensive documentation organized into the following categories:

### 🚀 Getting Started

| Document | Description |
|----------|-------------|
| **[Home](Home.md)** | Wiki overview and navigation |
| **[Quick Start Guide](Quick-Start.md)** | Get up and running in 5 minutes |
| **[Installation](Installation.md)** | Detailed installation instructions |
| **[Configuration Guide](Configuration.md)** | Complete configuration reference |

### 🏗️ Architecture & Design

| Document | Description |
|----------|-------------|
| **[System Architecture](Architecture.md)** | High-level design and components |
| **[Database Schema](Database-Schema.md)** | Database structure and queries |
| **[API Integration](API-Integration.md)** | PagerDuty API integration details |
| **[Data Flow](Data-Flow.md)** | Data movement through the system |

### 📖 User Guides

| Document | Description |
|----------|-------------|
| **[CLI Guide](CLI-Guide.md)** | Command-line interface reference |
| **[Web Dashboard](Web-Dashboard.md)** | Web interface usage guide |
| **[Admin Panel](Admin-Panel.md)** | Administrative functions |
| **[Metrics & Analytics](Metrics-Guide.md)** | Understanding metrics and reports |

### 🛠️ Operations & Maintenance

| Document | Description |
|----------|-------------|
| **[Troubleshooting](Troubleshooting.md)** | Common issues and solutions |
| **[FAQ](FAQ.md)** | Frequently asked questions |
| **[Performance](Performance.md)** | Optimization and tuning |
| **[Backup & Recovery](Backup-Recovery.md)** | Data protection strategies |

### 👨‍💻 Development

| Document | Description |
|----------|-------------|
| **[Development Guide](Development.md)** | Contributing and extending |
| **[Testing Guide](Testing.md)** | Running tests and coverage |
| **[API Reference](API-Reference.md)** | Flask API endpoints |
| **[Code Style Guide](Code-Style.md)** | Coding standards |

### 📋 Reference

| Document | Description |
|----------|-------------|
| **[Glossary](Glossary.md)** | Terms and definitions |
| **[Release Notes](Release-Notes.md)** | Version history |
| **[Deployment Guide](Deployment.md)** | Production deployment |

## 🎯 Quick Navigation

### I want to...

**Get started quickly:**
→ [Quick Start Guide](Quick-Start.md)

**Understand how it works:**
→ [System Architecture](Architecture.md)

**Configure the application:**
→ [Configuration Guide](Configuration.md)

**Use the command line:**
→ [CLI Guide](CLI-Guide.md)

**Use the web dashboard:**
→ [Web Dashboard](Web-Dashboard.md)

**Understand the metrics:**
→ [Metrics Guide](Metrics-Guide.md)

**Fix a problem:**
→ [Troubleshooting](Troubleshooting.md)

**Find an answer:**
→ [FAQ](FAQ.md)

**Contribute code:**
→ [Development Guide](Development.md)

## 📊 Project Overview

The **PagerDuty Incident Analytics Dashboard** is a comprehensive incident management and analytics system that:

### Core Features

✅ **Automated Data Collection**
- Fetches incidents from PagerDuty API
- Extracts custom fields for enhanced analytics
- Detects escalations via log entry analysis
- Stores data in local SQLite database

✅ **Advanced Analytics**
- Service-level incident metrics
- Escalation rate tracking
- CCOE resolution monitoring
- Infrastructure issue identification
- Daily, weekly, and monthly trends

✅ **Interactive Web Dashboard**
- Multi-service tab interface
- Calendar views with daily metrics
- Dynamic trend charts
- Hover popups for incident details
- Responsive Bootstrap 5 UI

✅ **Command-Line Tools**
- Update incident data
- Generate reports and summaries
- Database management
- Export and analysis capabilities

### Technology Stack

- **Backend:** Python 3.8+
- **Web Framework:** Flask 2.3+
- **Database:** SQLite 3
- **Frontend:** Bootstrap 5, Chart.js
- **API:** PagerDuty REST API v2

### Key Metrics Tracked

1. **Total Incidents** - All incidents in period
2. **Triggered Incidents** - Currently active
3. **Resolved Incidents** - Successfully closed
4. **Escalated Incidents** - Required escalation
5. **CCOE Resolved** - Resolved by CCOE team
6. **Infrastructure Caused** - Infrastructure-related issues

## 🗺️ Documentation Roadmap

### For New Users

1. Start with [Quick Start Guide](Quick-Start.md)
2. Review [Configuration Guide](Configuration.md)
3. Learn [CLI Guide](CLI-Guide.md) or [Web Dashboard](Web-Dashboard.md)
4. Understand [Metrics Guide](Metrics-Guide.md)
5. Bookmark [Troubleshooting](Troubleshooting.md) and [FAQ](FAQ.md)

### For Developers

1. Read [System Architecture](Architecture.md)
2. Study [Database Schema](Database-Schema.md)
3. Review [Development Guide](Development.md)
4. Check [Testing Guide](Testing.md)
5. Reference [API Reference](API-Reference.md)

### For Operations

1. Review [Deployment Guide](Deployment.md)
2. Setup [Backup & Recovery](Backup-Recovery.md)
3. Learn [Performance](Performance.md) tuning
4. Master [Troubleshooting](Troubleshooting.md)
5. Monitor [Release Notes](Release-Notes.md)

## 📝 Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| Home | ✅ Complete | 2025-10-25 |
| Quick Start | ✅ Complete | 2025-10-25 |
| Architecture | ✅ Complete | 2025-10-25 |
| Database Schema | ✅ Complete | 2025-10-25 |
| CLI Guide | ✅ Complete | 2025-10-25 |
| Metrics Guide | ✅ Complete | 2025-10-25 |
| Configuration | ✅ Complete | 2025-10-25 |
| Troubleshooting | ✅ Complete | 2025-10-25 |
| FAQ | ✅ Complete | 2025-10-25 |
| Installation | 📝 Planned | TBD |
| Web Dashboard | 📝 Planned | TBD |
| Admin Panel | 📝 Planned | TBD |
| API Integration | 📝 Planned | TBD |
| Data Flow | 📝 Planned | TBD |
| Development | 📝 Planned | TBD |
| Testing | 📝 Planned | TBD |
| API Reference | 📝 Planned | TBD |
| Code Style | 📝 Planned | TBD |
| Deployment | 📝 Planned | TBD |
| Performance | 📝 Planned | TBD |
| Backup & Recovery | 📝 Planned | TBD |
| Glossary | 📝 Planned | TBD |
| Release Notes | 📝 Planned | TBD |

## 🤝 Contributing to Documentation

Found an error or want to improve the documentation?

1. Documentation files are in Markdown format
2. Follow the existing structure and style
3. Include code examples where helpful
4. Add diagrams using Mermaid syntax
5. Update the README index when adding new pages

## 📞 Support

- **Issues:** Check [Troubleshooting](Troubleshooting.md) first
- **Questions:** See [FAQ](FAQ.md)
- **Updates:** Monitor [Release Notes](Release-Notes.md)

## 📄 License

This documentation is part of the PagerDuty Incident Analytics Dashboard project.

---

**Last Updated:** 2025-10-25  
**Wiki Version:** 1.0  
**Project Version:** 2.0

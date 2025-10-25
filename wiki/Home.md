# PagerDuty Incident Analytics Dashboard Wiki

Welcome to the comprehensive documentation for the PagerDuty Incident Analytics Dashboard project. This wiki provides detailed information about the system architecture, setup, usage, and maintenance.

## 📚 Table of Contents

### Getting Started
- [**Quick Start Guide**](Quick-Start.md) - Get up and running quickly
- [**Installation & Setup**](Installation.md) - Detailed installation instructions
- [**Configuration Guide**](Configuration.md) - How to configure the application

### Architecture & Design
- [**System Architecture**](Architecture.md) - High-level system design and components
- [**Database Schema**](Database-Schema.md) - Database structure and relationships
- [**API Integration**](API-Integration.md) - PagerDuty API integration details
- [**Data Flow**](Data-Flow.md) - How data moves through the system

### User Guides
- [**Command Line Interface**](CLI-Guide.md) - Command-line usage and examples
- [**Web Dashboard**](Web-Dashboard.md) - Using the web interface
- [**Admin Panel**](Admin-Panel.md) - Administrative functions and tools
- [**Metrics & Analytics**](Metrics-Guide.md) - Understanding metrics and reports

### Development
- [**Development Guide**](Development.md) - Contributing and extending the application
- [**Testing Guide**](Testing.md) - Running tests and test coverage
- [**API Reference**](API-Reference.md) - Flask API endpoints documentation
- [**Code Style Guide**](Code-Style.md) - Coding standards and best practices

### Operations
- [**Deployment Guide**](Deployment.md) - Production deployment instructions
- [**Troubleshooting**](Troubleshooting.md) - Common issues and solutions
- [**Performance Tuning**](Performance.md) - Optimization tips and techniques
- [**Backup & Recovery**](Backup-Recovery.md) - Data backup and restoration

### Reference
- [**Glossary**](Glossary.md) - Terms and definitions
- [**FAQ**](FAQ.md) - Frequently asked questions
- [**Release Notes**](Release-Notes.md) - Version history and changes

## 🎯 Project Overview

The PagerDuty Incident Analytics Dashboard is a comprehensive incident management and analytics system that provides:

- **Real-time incident tracking** from PagerDuty services
- **Escalation detection** through log entry analysis
- **CCOE resolution monitoring** via custom fields
- **Infrastructure issue identification** with root cause tracking
- **Interactive web dashboard** with charts and calendar views
- **Command-line tools** for data management and reporting

## 🚀 Key Features

### Data Collection
- Automated incident fetching from PagerDuty API
- Custom fields extraction for enhanced analytics
- Escalation detection via log entry analysis
- UTC-7 timezone support for consistent date handling

### Analytics & Reporting
- Service-level incident metrics
- Daily, weekly, and monthly trend analysis
- Escalation rate tracking
- CCOE resolution metrics
- Infrastructure-caused incident tracking

### Web Interface
- Multi-service tab dashboard
- Interactive calendar views with daily metrics
- Dynamic trend charts using Chart.js
- Hover popups for escalated incident details
- Responsive Bootstrap 5 UI

### Administration
- Real-time data updates from PagerDuty
- Database management tools
- System statistics and health monitoring
- Cleanup utilities for old data

## 🏗️ Technology Stack

- **Backend**: Python 3.8+
- **Web Framework**: Flask 2.3+
- **Database**: SQLite 3
- **Frontend**: Bootstrap 5, Chart.js
- **APIs**: PagerDuty REST API v2
- **Configuration**: YAML

## 📊 Quick Stats

- **6 Core Services** monitored
- **6 Key Metrics** tracked per service
- **UTC-7 Timezone** for consistent reporting
- **SQLite Database** for efficient storage
- **RESTful API** for web interface

## 🔗 Quick Links

- [GitHub Repository](#) (Update with your repository URL)
- [PagerDuty API Documentation](https://developer.pagerduty.com/)
- [Issue Tracker](#) (Update with your issue tracker URL)

## 📝 Latest Updates

Check the [Release Notes](Release-Notes.md) for the latest changes and improvements.

## 🤝 Contributing

We welcome contributions! Please see our [Development Guide](Development.md) for information on how to contribute to this project.

## 📞 Support

- For bugs and feature requests, please use the issue tracker
- For general questions, refer to the [FAQ](FAQ.md)
- For troubleshooting, see the [Troubleshooting Guide](Troubleshooting.md)

## 📄 License

This application is designed for internal incident management and analytics purposes.

---

*Last Updated: 2025-10-25*

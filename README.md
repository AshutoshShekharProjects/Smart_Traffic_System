# Smart Traffic Prediction and Control System

## Overview
A comprehensive traffic flow prediction system using ML models deployed on cloud infrastructure with UNIX scheduling for automated data processing and real-time traffic control.

## Features
- 🚦 Real-time traffic flow prediction using ML models
- 📊 Interactive dashboard with live traffic visualization from Delhi & Bengaluru
- 🔄 Automated data refresh using UNIX cron jobs
- 🌐 Cloud-ready deployment architecture
- 📱 Responsive web interface
- 🎯 Traffic light control optimization for Indian traffic conditions
- 📈 Historical data analysis and trends
- 🇮🇳 Focused on high-traffic Indian metropolitan areas

## Tech Stack
- **Backend**: Python Flask, scikit-learn, pandas
- **Frontend**: React.js with modern UI components
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **Scheduling**: UNIX cron jobs
- **Deployment**: Docker containers
- **ML Models**: Random Forest, Linear Regression

## Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python app.py`
3. Access dashboard: `http://localhost:5000`

## Architecture
```
├── ML Models (Traffic Prediction for Indian Cities)
├── Data Simulator (8 High-Traffic Intersections: Delhi & Bengaluru)
├── UNIX Scheduler (Cron Jobs)
├── REST API (Flask)
└── Frontend Dashboard (Interactive Maps)
```

## Monitored Intersections (12 Locations Across 4 Cities)

### Delhi NCR
- **High Congestion**: Connaught Place, IFFCO Chowk Gurgaon
- **Medium Congestion**: Lajpat Nagar
- **Low Congestion**: Dwarka Sector 21

### Bengaluru
- **High Congestion**: Silk Board Junction, Electronic City
- **Medium Congestion**: Jayanagar 4th Block
- **Low Congestion**: Hebbal Flyover

### Mumbai
- **High Congestion**: Bandra Kurla Complex
- **Medium Congestion**: Andheri East

### Chennai
- **Medium Congestion**: Adyar Signal
- **Low Congestion**: OMR IT Corridor
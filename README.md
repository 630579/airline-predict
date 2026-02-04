## airline-predict
## Features

**Core Modules** :
- Flight Delay Prediction: Predict delays based on weather, maintenance, and operational factors
- Aircraft Health Monitoring: Real-time monitoring of engine performance, cabin conditions, and maintenance alerts
- Crew Scheduling Optimization: Automated crew assignment with duty time compliance
- Passenger Load Prediction: Forecast passenger demand and load factors
- Route Monitoring: Weather tracking and diversion recommendations
- Operations Dashboard: Real-time visualization of airline operations
- Daily Reporting: Comprehensive operational reports generation

 **Prerequisites** :
 
  - Python 3.8+
  - Required packages: tabulate

**Installation** :
  - Clone or download the project files
  
  - Install dependencies:
    ```sql bash
     pip install tabulate
    ```
## Commndline options
```sql
python main.py --monitor     # Start real-time monitoring
python main.py --analyze     # Run single comprehensive analysis
python main.py --report      # Generate daily report
```
## System Components
## Main Application (main.py) 
- Central system controller

- Interactive menu system

- Real-time monitoring threads

= Sample data generation

## Configuration (airline_config.json)
- Airline details (name, code, hub airport)

- Operational thresholds

- Aircraft fleet specifications

- Route definitions

- Alert levels and reporting settings

## Core Modules
**Log Processor**
- Processes flight logs and sensor data

- Aggregates metrics by flight

- Calculates summary statistics

**Delay Predictor**
Predicts flight delays using multiple factors:

 Weather conditions

- Maintenance issues

- Operational congestion

- Categorizes delays by severity

**Health Monitor**
- Monitors aircraft systems:

Engine vibration and thrust

Cabin pressure and temperature

Fuel consumption

Generates critical alerts

Crew Optimizer
Automated crew scheduling

Duty time compliance checks

Crew shortage detection

Load Predictor
Predicts passenger demand

Identifies overbooking risks

Categorizes demand levels

Route Monitor
Tracks weather along routes

Suggests diversions when needed

Monitors destination conditions

Dashboard
Real-time operations display

Visual summaries of all metrics

Alert status visualization

Reporter
Generates daily operations reports

Creates detailed analysis documents

PDF report generation

Interactive Menu Options
Run Complete Analysis: Comprehensive analysis of all flights

Start Real-time Monitoring: Continuous monitoring with live updates

Search Flight/Aircraft: Lookup specific flight or aircraft details

Generate Custom Report: Create detailed operations report

View Current Dashboard: Display real-time dashboard

System Configuration: Update thresholds and settings

Exit: Close the application

Search Features
Search flights by ID

Search aircraft by registration

Search crew members

Search by route
Configuration Management
Update weather thresholds

Modify maintenance limits

Adjust crew scheduling rules

Backup and restore system data


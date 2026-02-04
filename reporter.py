"""
Module for generating daily aviation reports
"""
import json
import os
from datetime import datetime
from tabulate import tabulate

class ReportGenerator:
    def __init__(self):
        self.reports_dir = "output/reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_daily_report(self, flights_data, predictions, date_str):
        """Generate daily aviation operations report"""
        report_path = os.path.join(self.reports_dir, f"aviation_report_{date_str}.txt")
        
        with open(report_path, 'w') as f:
            self._write_header(f, date_str)
            self._write_executive_summary(f, flights_data, predictions)
            self._write_delay_analysis(f, predictions.get('delays', []))
            self._write_health_alerts(f, predictions.get('health_alerts', []))
            self._write_load_analysis(f, predictions.get('load', []))
            self._write_crew_schedule(f, predictions.get('crew_assignments', {}))
            self._write_route_monitoring(f, predictions.get('route_alerts', []))
            self._write_recommendations(f, predictions)
            self._write_footer(f)
        
        return report_path
    
    def _write_header(self, file, date_str):
        """Write report header"""
        file.write("="*80 + "\n")
        file.write("DAILY AVIATION OPERATIONS REPORT\n".center(80))
        file.write("="*80 + "\n")
        file.write(f"Report Date: {date_str}\n")
        file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write("-"*80 + "\n\n")
    
    def _write_executive_summary(self, file, flights_data, predictions):
        """Write executive summary"""
        file.write("EXECUTIVE SUMMARY\n")
        file.write("="*40 + "\n\n")
        
        # Flight statistics
        total_flights = len(flights_data)
        file.write(f"Total Flights Monitored: {total_flights}\n")
        
        # Delay statistics
        delays = predictions.get('delays', [])
        if delays:
            total_delays = len(delays)
            avg_delay = sum(d['predicted_delay_minutes'] for d in delays) / total_delays
            file.write(f"Flights with Predicted Delays: {total_delays} ({total_delays/total_flights*100:.1f}%)\n")
            file.write(f"Average Predicted Delay: {avg_delay:.1f} minutes\n")
        else:
            file.write("Flights with Predicted Delays: 0\n")
        
        # Health alerts
        health_alerts = predictions.get('health_alerts', [])
        critical_alerts = [a for a in health_alerts if a['severity'] == 'CRITICAL']
        file.write(f"Critical Health Alerts: {len(critical_alerts)}\n")
        
        # Crew issues
        crew_data = predictions.get('crew_assignments', {})
        crew_issues = len(crew_data.get('issues', []))
        file.write(f"Crew Scheduling Issues: {crew_issues}\n")
        
        # Load statistics
        load_predictions = predictions.get('load', [])
        if load_predictions:
            avg_load = sum(p['predicted_load_factor'] for p in load_predictions) / len(load_predictions)
            file.write(f"Average Predicted Load Factor: {avg_load:.1%}\n")
        
        file.write("\n")
    
    def _write_delay_analysis(self, file, delay_predictions):
        """Write delay analysis section"""
        file.write("DELAY PREDICTION ANALYSIS\n")
        file.write("="*40 + "\n\n")
        
        if not delay_predictions:
            file.write("No delays predicted for today.\n\n")
            return
        
        # Categorize by severity
        severity_counts = {}
        for delay in delay_predictions:
            severity = delay['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        file.write("Delay Severity Distribution:\n")
        for severity in ['SEVERE', 'SIGNIFICANT', 'MODERATE', 'MINOR']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                file.write(f"  {severity}: {count} flights\n")
        
        # Top delays
        file.write("\nTop 5 Delays:\n")
        sorted_delays = sorted(delay_predictions, key=lambda x: x['predicted_delay_minutes'], reverse=True)[:5]
        
        table_data = []
        for delay in sorted_delays:
            table_data.append([
                delay['flight_id'],
                f"{delay['predicted_delay_minutes']} min",
                delay['severity'],
                ', '.join(delay['reasons'][:2])
            ])
        
        headers = ["Flight", "Delay", "Severity", "Primary Reasons"]
        file.write(tabulate(table_data, headers=headers, tablefmt="grid"))
        file.write("\n\n")
        
        # Delay reasons analysis
        file.write("Common Delay Reasons:\n")
        reasons = {}
        for delay in delay_predictions:
            for reason in delay['reasons']:
                reasons[reason] = reasons.get(reason, 0) + 1
        
        for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
            file.write(f"  {reason}: {count} occurrences\n")
        
        file.write("\n")
    
    def _write_health_alerts(self, file, health_alerts):
        """Write health alerts section"""
        file.write("AIRCRAFT HEALTH MONITORING\n")
        file.write("="*40 + "\n\n")
        
        if not health_alerts:
            file.write("No health alerts generated.\n\n")
            return
        
        # Critical alerts
        critical_alerts = [a for a in health_alerts if a['severity'] == 'CRITICAL']
        if critical_alerts:
            file.write("🔴 CRITICAL ALERTS:\n")
            for alert in critical_alerts:
                file.write(f"  Flight {alert['flight_id']} - {alert['aircraft_id']}\n")
                file.write(f"    Alert: {alert['alert_type']}\n")
                file.write(f"    Message: {alert['message']}\n")
                file.write(f"    Time: {alert['timestamp']}\n\n")
        
        # Alert statistics
        file.write("Alert Statistics:\n")
        alert_types = {}
        for alert in health_alerts:
            alert_type = alert['alert_type']
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
        
        for alert_type, count in sorted(alert_types.items(), key=lambda x: x[1], reverse=True):
            file.write(f"  {alert_type}: {count}\n")
        
        file.write("\n")
    
    def _write_load_analysis(self, file, load_predictions):
        """Write passenger load analysis"""
        file.write("PASSENGER LOAD PREDICTIONS\n")
        file.write("="*40 + "\n\n")
        
        if not load_predictions:
            file.write("No load predictions available.\n\n")
            return
        
        # Statistics
        total_capacity = sum(p['capacity'] for p in load_predictions)
        total_passengers = sum(p['predicted_passengers'] for p in load_predictions)
        avg_load = total_passengers / total_capacity if total_capacity > 0 else 0
        
        file.write(f"Total Predicted Passengers: {total_passengers:,}\n")
        file.write(f"Total Available Capacity: {total_capacity:,}\n")
        file.write(f"System-wide Load Factor: {avg_load:.1%}\n\n")
        
        # Flight categories
        full_flights = [p for p in load_predictions if p['predicted_load_factor'] > 0.9]
        low_flights = [p for p in load_predictions if p['predicted_load_factor'] < 0.4]
        
        file.write(f"Flights >90% Full: {len(full_flights)}\n")
        file.write(f"Flights <40% Load: {len(low_flights)}\n\n")
        
        # Top flights by load
        file.write("Top 5 Flights by Load Factor:\n")
        sorted_loads = sorted(load_predictions, key=lambda x: x['predicted_load_factor'], reverse=True)[:5]
        
        table_data = []
        for load in sorted_loads:
            table_data.append([
                load['flight_id'],
                load['predicted_passengers'],
                load['capacity'],
                f"{load['predicted_load_factor']:.1%}",
                load['demand_level']
            ])
        
        headers = ["Flight", "Passengers", "Capacity", "Load Factor", "Demand Level"]
        file.write(tabulate(table_data, headers=headers, tablefmt="grid"))
        file.write("\n\n")
    
    def _write_crew_schedule(self, file, crew_data):
        """Write crew scheduling section"""
        file.write("CREW SCHEDULING\n")
        file.write("="*40 + "\n\n")
        
        assignments = crew_data.get('assignments', [])
        issues = crew_data.get('issues', [])
        summary = crew_data.get('summary', {})
        
        file.write(f"Flights Scheduled: {summary.get('total_flights_scheduled', 0)}\n")
        file.write(f"Crew Members Utilized: {summary.get('total_crew_utilized', 0)}\n")
        file.write(f"Average Flights per Crew: {summary.get('avg_flights_per_crew', 0):.1f}\n\n")
        
        # Issues
        if issues:
            file.write("SCHEDULING ISSUES:\n")
            for issue in issues:
                file.write(f"  Type: {issue['type']}\n")
                file.write(f"  Severity: {issue['severity']}\n")
                if 'flight_id' in issue:
                    file.write(f"  Flight: {issue['flight_id']}\n")
                if 'crew_id' in issue:
                    file.write(f"  Crew: {issue['crew_id']}\n")
                file.write("\n")
        else:
            file.write("No scheduling issues detected.\n\n")
        
        # Sample assignments
        if assignments:
            file.write("Sample Crew Assignments (First 5):\n")
            for assignment in assignments[:5]:
                file.write(f"  Flight {assignment['flight_id']}:\n")
                file.write(f"    Captain: {assignment.get('captain', 'Not assigned')}\n")
                file.write(f"    First Officer: {assignment.get('first_officer', 'Not assigned')}\n")
                file.write(f"    Attendants: {len(assignment.get('attendants', []))}\n\n")
        
        file.write("\n")
    
    def _write_route_monitoring(self, file, route_alerts):
        """Write route monitoring section"""
        file.write("ROUTE MONITORING & DIVERSION RECOMMENDATIONS\n")
        file.write("="*40 + "\n\n")
        
        if not route_alerts:
            file.write("No route alerts generated.\n\n")
            return
        
        # Diversion recommendations
        diversions = [a for a in route_alerts if a['alert_type'] == 'DIVERSION_RECOMMENDED']
        if diversions:
            file.write("DIVERSION RECOMMENDATIONS:\n")
            for alert in diversions:
                file.write(f"  Flight: {alert['flight_id']}\n")
                file.write(f"  Current Destination: {alert['current_destination']}\n")
                file.write(f"  Suggested Diversion: {alert['suggested_diversion']}\n")
                file.write(f"  Additional Time: {alert['additional_flight_time_minutes']} minutes\n")
                file.write(f"  Reason: {alert['message']}\n\n")
        
        # Weather alerts
        weather_alerts = [a for a in route_alerts if a['alert_type'] != 'DIVERSION_RECOMMENDED']
        if weather_alerts:
            file.write("WEATHER ALERTS:\n")
            critical_weather = [a for a in weather_alerts if a['severity'] == 'CRITICAL']
            
            for alert in critical_weather:
                file.write(f"  Flight: {alert['flight_id']}\n")
                file.write(f"  Alert Type: {alert['alert_type']}\n")
                file.write(f"  Location: {alert.get('location', 'Unknown')}\n")
                file.write(f"  Message: {alert['message']}\n\n")
        
        file.write("\n")
    
    def _write_recommendations(self, file, predictions):
        """Write recommendations section"""
        file.write("OPERATIONAL RECOMMENDATIONS\n")
        file.write("="*40 + "\n\n")
        
        recommendations = []
        
        # Check for critical issues
        health_alerts = predictions.get('health_alerts', [])
        critical_health = [a for a in health_alerts if a['severity'] == 'CRITICAL']
        if critical_health:
            recommendations.append("Schedule immediate maintenance for aircraft with critical health alerts.")
        
        # Check for crew shortages
        crew_data = predictions.get('crew_assignments', {})
        crew_issues = crew_data.get('issues', [])
        critical_crew = [i for i in crew_issues if i['severity'] == 'CRITICAL']
        if critical_crew:
            recommendations.append("Address critical crew shortages immediately.")
        
        # Check for major delays
        delays = predictions.get('delays', [])
        severe_delays = [d for d in delays if d['severity'] in ['SEVERE', 'SIGNIFICANT']]
        if severe_delays:
            recommendations.append(f"Prepare passenger services for {len(severe_delays)} flights with significant delays.")
        
        # Check for overbooking
        load_predictions = predictions.get('load', [])
        overbooked = sum(1 for p in load_predictions 
                        if any(s['type'] == 'OVERBOOKING_RISK' for s in p['scenarios']))
        if overbooked:
            recommendations.append(f"Prepare overbooking protocols for {overbooked} flights.")
        
        # Check for diversions
        route_alerts = predictions.get('route_alerts', [])
        diversions = [a for a in route_alerts if a['alert_type'] == 'DIVERSION_RECOMMENDED']
        if diversions:
            recommendations.append(f"Coordinate with {len(diversions)} alternate airports for potential diversions.")
        
        # Write recommendations
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                file.write(f"{i}. {rec}\n")
        else:
            file.write("No critical recommendations at this time.\n")
        
        file.write("\n")
    
    def _write_footer(self, file):
        """Write report footer"""
        file.write("="*80 + "\n")
        file.write("END OF REPORT\n".center(80))
        file.write("="*80 + "\n")